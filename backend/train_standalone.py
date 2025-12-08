from train import train_model
import os

# Your training data path
data_path = "training_data.json"

# Model configuration
model_name = "unsloth/Qwen2.5-0.5B-Instruct"  # ← Much smaller - 500M params
output_dir = "models/my-pretrained-model"
max_steps = 60
learning_rate = 2e-4
batch_size = 1

print("🚀 Starting training...")
print(f"📁 Data: {data_path}")
print(f"🤖 Output: {output_dir}")
print(f"⚙️  Steps: {max_steps}")
print(f"📊 Learning Rate: {learning_rate}")
print("")

# Train the model
train_model(
    data_path=data_path,
    model_name=model_name,
    output_dir=output_dir,
    max_steps=max_steps,
    learning_rate=learning_rate,
    batch_size=batch_size,
    training_id=None,
    status_dict=None
)

print("")
print("✅ Training complete!")
print(f"📦 Model saved to: {output_dir}")
print("")
print("🚀 You can now run the web app:")
print("   python app.py")