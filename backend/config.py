import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = os.path.join(BASE_DIR, 'data', 'uploads')
MODEL_PATH = os.path.join(BASE_DIR, 'models')
CHECKPOINT_PATH = os.path.join(BASE_DIR, 'checkpoints')

API_HOST = '0.0.0.0'
API_PORT = 5000
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

DEFAULT_MODEL = 'unsloth/llama-3-8b-bnb-4bit'
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True

DEFAULT_TRAINING_CONFIG = {
    'max_steps': 60,
    'learning_rate': 2e-4,
    'batch_size': 1,
    'gradient_accumulation_steps': 4,
    'warmup_steps': 5,
    'weight_decay': 0.01,
    'lr_scheduler_type': 'linear',
    'lora_r': 16,
    'lora_alpha': 16,
    'lora_dropout': 0,
}

MAX_UPLOAD_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {'json', 'jsonl', 'csv'}

CUDA_VISIBLE_DEVICES = os.environ.get('CUDA_VISIBLE_DEVICES', '0')
