from unsloth import FastLanguageModel
import torch
from datasets import load_dataset, Dataset
from trl import SFTTrainer
from transformers import TrainingArguments, TrainerCallback
import json

class StatusCallback(TrainerCallback):
    """Callback to track training progress and update status"""
    def __init__(self, training_id, status_dict):
        self.training_id = training_id
        self.status_dict = status_dict
    
    def on_step_end(self, args, state, control, **kwargs):
        """Update status after each training step"""
        if self.status_dict and self.training_id:
            self.status_dict[self.training_id].update({
                'status': 'training',
                'current_step': state.global_step,
                'total_steps': state.max_steps,
                'progress': int((state.global_step / state.max_steps) * 100),
                'loss': state.log_history[-1].get('loss', None) if state.log_history else None
            })
    
    def on_train_end(self, args, state, control, **kwargs):
        """Update status when training completes"""
        if self.status_dict and self.training_id:
            self.status_dict[self.training_id].update({
                'status': 'completed',
                'progress': 100,
                'current_step': state.max_steps,
                'total_steps': state.max_steps
            })

def format_data(examples, data_format='instruction'):
    """Format data into training text based on the detected format"""
    texts = []
    
    if data_format == 'instruction':
        for i in range(len(examples['instruction'])):
            instruction = examples['instruction'][i]
            # Handle both 'input' and 'scenario' fields
            input_text = examples.get('input', examples.get('scenario', [''] * len(examples['instruction'])))[i]
            # Handle both 'output' and 'advice' fields
            output = examples.get('output', examples.get('advice', [''] * len(examples['instruction'])))[i]
            
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
    """Automatically detect the format of the training data"""
    if isinstance(data, list) and len(data) > 0:
        sample = data[0]
        if 'instruction' in sample and ('output' in sample or 'advice' in sample):
            return 'instruction'
        elif 'conversations' in sample:
            return 'conversation'
        elif 'question' in sample and 'answer' in sample:
            return 'qa'
    return 'instruction'

def load_training_data(data_path):
    """Load and flatten nested JSON structures"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle nested structure - extract the array from any top-level key
    if isinstance(data, dict):
        # Find the first key that contains a list
        for key, value in data.items():
            if isinstance(value, list):
                print(f"📦 Found data under key: '{key}'")
                data = value
                break
    
    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of training examples")
    
    return data

def train_model(data_path, model_name, output_dir, max_steps=60, 
                learning_rate=2e-4, batch_size=1, training_id=None, 
                status_dict=None):
    """
    Main training function
    
    Args:
        data_path: Path to training data JSON file
        model_name: HuggingFace model identifier
        output_dir: Directory to save the trained model
        max_steps: Number of training steps
        learning_rate: Learning rate for training
        batch_size: Batch size per device
        training_id: Optional ID for tracking training progress
        status_dict: Optional dict for updating training status
    """
    try:
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'loading_model'
        
        print("🔧 Loading model...")
        max_seq_length = 2048
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,
            load_in_4bit=True,
            device_map="auto",
        )
        
        print("⚙️ Configuring LoRA...")
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
            lora_alpha=16,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=42,
        )
        
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'loading_data'
        
        print("📂 Loading training data...")
        # Load and flatten the data
        data = load_training_data(data_path)
        data_format = detect_format(data)
        
        print(f"📊 Data format detected: {data_format}")
        print(f"📝 Number of examples: {len(data)}")
        
        # Create dataset from the flattened data
        dataset = Dataset.from_list(data)
        
        def formatting_func(examples):
            return format_data(examples, data_format)
        
        print("🔄 Formatting dataset...")
        dataset = dataset.map(formatting_func, batched=True)
        
        if training_id and status_dict:
            status_dict[training_id]['status'] = 'training'
        
        callbacks = []
        if training_id and status_dict:
            callbacks.append(StatusCallback(training_id, status_dict))
        
        print("🏋️ Configuring training arguments...")
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
        
        print("🎯 Initializing trainer...")
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            args=training_args,
            callbacks=callbacks,
        )
        
        print("🚀 Starting training...")
        trainer.train()
        
        print("💾 Saving model...")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        if training_id and status_dict:
            status_dict[training_id].update({
                'status': 'completed',
                'progress': 100,
                'message': f'Model saved to {output_dir}'
            })
        
        print(f"✅ Training complete! Model saved to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if training_id and status_dict:
            status_dict[training_id].update({
                'status': 'failed',
                'error': str(e)
            })
        raise

if __name__ == "__main__":
    # Example usage when running directly
    train_model(
        data_path="training_data.json",
        model_name="unsloth/gemma-2-2b-it",
        output_dir="models/financial-advisor",
        max_steps=60,
        learning_rate=2e-4,
        batch_size=1
    )