from unsloth import FastLanguageModel
import torch

_model_cache = {}

def load_model(model_path):
    if model_path in _model_cache:
        return _model_cache[model_path]
    
    print(f"Loading model from {model_path}...")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_path,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    
    FastLanguageModel.for_inference(model)
    
    _model_cache[model_path] = (model, tokenizer)
    print(f"✅ Model loaded successfully")
    
    return model, tokenizer

def generate_response(model_path, prompt, max_tokens=256, temperature=0.7):
    try:
        model, tokenizer = load_model(model_path)
        
        formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"
        
        inputs = tokenizer([formatted_prompt], return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                use_cache=True,
            )
        
        full_response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        
        if "### Response:" in full_response:
            response = full_response.split("### Response:")[-1].strip()
        else:
            response = full_response
        
        return response
    
    except Exception as e:
        print(f"❌ Inference error: {str(e)}")
        raise

def clear_model_cache():
    global _model_cache
    _model_cache.clear()
    torch.cuda.empty_cache()
    print("🗑️ Model cache cleared")