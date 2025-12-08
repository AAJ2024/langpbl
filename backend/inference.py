from unsloth import FastLanguageModel
import torch

# Cache for loaded models to avoid reloading
_model_cache = {}

def generate_response(model_path, prompt, max_tokens=256, temperature=0.7):
    """
    Generate a response from the trained model
    
    Args:
        model_path: Path to the trained model directory
        prompt: The input prompt/question
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
    
    Returns:
        Generated response text
    """
    try:
        # Load model if not cached
        if model_path not in _model_cache:
            print(f"🔧 Loading model from {model_path}...")
            
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=model_path,
                max_seq_length=1024,
                dtype=None,
                load_in_4bit=True,
            )
            
            # Enable inference mode
            FastLanguageModel.for_inference(model)
            
            _model_cache[model_path] = (model, tokenizer)
            print(f"✅ Model loaded and cached!")
        else:
            model, tokenizer = _model_cache[model_path]
        
        # Format prompt for instruction-following
        formatted_prompt = f"""### Instruction:
Provide financial advice for this situation.

### Input:
{prompt}

### Response:
"""
        
        # Generate response
        inputs = tokenizer([formatted_prompt], return_tensors="pt").to("cuda")
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True if temperature > 0 else False,
            use_cache=True
        )
        
        # Decode and extract response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response part (after "### Response:")
        if "### Response:" in full_response:
            response = full_response.split("### Response:")[-1].strip()
        else:
            response = full_response.strip()
        
        return response
    
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        raise Exception(f"Failed to generate response: {str(e)}")

def clear_model_cache():
    """Clear the model cache to free up memory"""
    global _model_cache
    _model_cache = {}
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("🗑️ Model cache cleared")

# For testing the module directly
if __name__ == "__main__":
    test_prompt = "I'm 25 with $40k in student loans at 6% interest. Should I pay extra or invest?"
    
    try:
        response = generate_response(
            model_path="models/financial_advisor_model",
            prompt=test_prompt,
            max_tokens=400,
            temperature=0.7
        )
        print("\n💬 Test Question:")
        print(test_prompt)
        print("\n🤖 AI Response:")
        print(response)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nMake sure you have a trained model in models/financial_advisor_model/")