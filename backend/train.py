from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments, TrainerCallback
import json

class StatusCallback(TrainerCallback):
    def __init__(self, training_id, status_dict):
        self.training_id = training_id
        self.status_dict = status_dict
    
    def on_step_end(self, args, state, control, **kwargs):
        self.status_dict[self.training_id].update({
            'status': 'training',
            'current_step': state.global_step,
            'total_steps': state.max_steps,
            'progress': int((state.global_step / state.max_steps) * 100),
            'loss': state.log_history[-1].get('loss', None) if state.log_history else None
        })
    
    def on_train_end(self, args, state, control, **kwargs):
        self.status_dict[self.training_id].update({
            'status': 'completed',
            'progress': 100,
            'current_step': state.max_steps,
            'total_steps': state.max_steps
        })

def format_data(examples, data_format='instruction'):
    texts = []
    
    if data_format == 'instruction':
        for i in range(len(examples['instruction'])):
            instruction = examples['instruction'][i]
            input_text = examples.get('input', [''] * len(examples['instruction']))[i]
            output = examples['output'][i]
            
            text = f"### Instruction:\n{instruction}\n\n"
            if input_text and input_text.strip():
                text += f"### Input:\n{input_text}\n\n"
            text += f"### Response:\n{output}"
            texts.append(text)
    
    elif data_format == 'conversation':
        for conv in examples['conversations']:
            text = ""
            for message in conv:
                if message['from'] == 'human':
                    text += f"### Human:\n{message['value']}\n\n"
                else:
                    text += f"### Assistant:\n{message['value']}\n\n"
            texts.append(text.strip())
    
    elif data_format == 'qa':
        for i in range(len(examples['question'])):
            question = examples['question'][i]
            answer = examples['answer'][i]
            text = f"### Question:\n{question}\n\n### Answer:\n{answer}"
            texts.append(text)
    
    return {"text": texts}

def detect_format(data):
    if isinstance(data, list) and len(data) > 0:
        sample = data[0]
        if 'instruction' in sample and 'output' in sample:
            return 'instruction'
        elif 'conversations' in sample:
            return 'conversation'
        elif 'question' in sample and 'answer' in sample:
            return 'qa'
    return 'instruction'

def train_model(data_path, model_name, output_dir, max_steps=60, 
                learning_rate=2e-4, batch_size=1, training_id=None, 
                status_dict=None):
    try:
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'loading_model'
        
        max_seq_length = 2048
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )
        
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing=True,
            random_state=3407,
        )
        
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'loading_data'
        
        if data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_format = detect_format(data)
        else:
            data_format = 'instruction'
        
        dataset = load_dataset('json', data_files=data_path, split='train')
        
        def formatting_func(examples):
            return format_data(examples, data_format)
        
        dataset = dataset.map(formatting_func, batched=True)
        
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'training'
        
        callbacks = []
        if training_id and status_dict:
            callbacks.append(StatusCallback(training_id, status_dict))
        
        training_args = TrainingArguments(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=max_steps,
            learning_rate=learning_rate,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=output_dir,
            report_to="none",
        )
        
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            args=training_args,
            callbacks=callbacks,
        )
        
        trainer.train()
        
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        if training_id and status_dict:
            status_dict[training_id].update({
                'status': 'completed',
                'progress': 100,
                'message': f'Model saved to {output_dir}'
            })
        
        print(f"✅ Training complete! Model saved to: {output_dir}")
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        if training_id and status_dict:
            status_dict[training_id].update({
                'status': 'failed',
                'error': str(e)
            })
        raise