from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
from werkzeug.utils import secure_filename
import train
import inference
import config
import database

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = config.DATA_PATH
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'json', 'jsonl', 'csv'}

training_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Unsloth API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload-data', methods=['POST'])
def upload_data():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if filename.endswith('.json'):
                data = json.load(f)
                rows = len(data) if isinstance(data, list) else 1
            elif filename.endswith('.jsonl'):
                rows = sum(1 for line in f)
            else:
                rows = sum(1 for line in f) - 1
        
        return jsonify({
            'success': True,
            'message': 'Data uploaded successfully',
            'file_id': file_id,
            'filename': filename,
            'rows': rows,
            'uploaded_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start-training', methods=['POST'])
def start_training():
    try:
        data = request.get_json()
        
        required_fields = ['file_id', 'model_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing: {field}'}), 400
        
        file_id = data['file_id']
        model_name = data['model_name']
        max_steps = data.get('max_steps', 60)
        learning_rate = data.get('learning_rate', 2e-4)
        batch_size = data.get('batch_size', 1)
        output_name = data.get('output_name', f'model_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        training_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        training_status[training_id] = {
            'status': 'initializing',
            'progress': 0,
            'current_step': 0,
            'total_steps': max_steps,
            'loss': None,
            'started_at': datetime.now().isoformat()
        }
        
        def run_training():
            try:
                train.train_model(
                    data_path=filepath,
                    model_name=model_name,
                    output_dir=os.path.join(config.MODEL_PATH, output_name),
                    max_steps=max_steps,
                    learning_rate=learning_rate,
                    batch_size=batch_size,
                    training_id=training_id,
                    status_dict=training_status
                )
            except Exception as e:
                training_status[training_id]['status'] = 'failed'
                training_status[training_id]['error'] = str(e)
        
        thread = threading.Thread(target=run_training)
        thread.start()
        
        return jsonify({
            'success': True,
            'training_id': training_id,
            'message': 'Training started',
            'model_output': output_name
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/training-status/<training_id>', methods=['GET'])
def get_training_status(training_id):
    if training_id not in training_status:
        return jsonify({'success': False, 'error': 'Training ID not found'}), 404
    return jsonify(training_status[training_id])

@app.route('/api/models', methods=['GET'])
def list_models():
    try:
        models = []
        model_path = config.MODEL_PATH
        
        if not os.path.exists(model_path):
            return jsonify({'models': []})
        
        for model_dir in os.listdir(model_path):
            full_path = os.path.join(model_path, model_dir)
            if os.path.isdir(full_path):
                stat_info = os.stat(full_path)
                size_mb = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(full_path)
                    for filename in filenames
                ) / (1024 * 1024)
                
                models.append({
                    'id': model_dir,
                    'name': model_dir,
                    'created_at': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    'size_mb': round(size_mb, 2),
                    'path': full_path
                })
        
        return jsonify({'models': sorted(models, key=lambda x: x['created_at'], reverse=True)})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if 'model_id' not in data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
        model_id = data['model_id']
        message = data['message']
        max_tokens = data.get('max_tokens', 256)
        temperature = data.get('temperature', 0.7)
        session_id = data.get('session_id', None)
        
        model_path = os.path.join(config.MODEL_PATH, model_id)
        if not os.path.exists(model_path):
            return jsonify({'success': False, 'error': 'Model not found'}), 404
        
        response_text = inference.generate_response(
            model_path=model_path,
            prompt=message,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # 🔥 SAVE CONVERSATION TO DATABASE
        database.save_conversation(
            user_message=message,
            ai_response=response_text,
            model_id=model_id,
            session_id=session_id
        )
        
        return jsonify({
            'success': True,
            'response': response_text,
            'model_id': model_id,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        model_path = os.path.join(config.MODEL_PATH, model_id)
        
        if not os.path.exists(model_path):
            return jsonify({'success': False, 'error': 'Model not found'}), 404
        
        import shutil
        shutil.rmtree(model_path)
        
        return jsonify({
            'success': True,
            'message': f'Model {model_id} deleted'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/base-models', methods=['GET'])
def get_base_models():
    base_models = [
        {
            'id': 'unsloth/llama-3-8b-bnb-4bit',
            'name': 'Llama 3 8B (4-bit)',
            'description': 'Meta Llama 3 8B optimized for 4-bit',
            'size': '4.5GB',
            'recommended': True
        },
        {
            'id': 'unsloth/mistral-7b-bnb-4bit',
            'name': 'Mistral 7B (4-bit)',
            'description': 'Mistral 7B optimized for 4-bit',
            'size': '4GB',
            'recommended': True
        }
    ]
    return jsonify({'models': base_models})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = database.get_conversation_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/retrain', methods=['POST'])
def trigger_retrain():
    try:
        data = request.get_json()
        model_id = data.get('model_id')
        
        if not model_id:
            return jsonify({'success': False, 'error': 'model_id required'}), 400
        
        # Export conversations as training data
        training_file = database.export_training_data()
        
        # Start training in background
        training_id = f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        training_status[training_id] = {
            'status': 'initializing',
            'progress': 0,
            'current_step': 0,
            'total_steps': 50,
            'loss': None,
            'started_at': datetime.now().isoformat()
        }
        
        def run_retraining():
            try:
                # Train with new conversations
                train.train_model(
                    data_path=training_file,
                    model_name='unsloth/llama-3-8b-bnb-4bit',
                    output_dir=os.path.join(config.MODEL_PATH, model_id),
                    max_steps=50,
                    learning_rate=2e-4,
                    batch_size=1,
                    training_id=training_id,
                    status_dict=training_status
                )
                
                # Mark conversations as trained
                database.mark_conversations_trained()
                
            except Exception as e:
                training_status[training_id]['status'] = 'failed'
                training_status[training_id]['error'] = str(e)
        
        thread = threading.Thread(target=run_retraining)
        thread.start()
        
        return jsonify({
            'success': True,
            'training_id': training_id,
            'message': 'Retraining started with new conversations'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(config.DATA_PATH, exist_ok=True)
    os.makedirs(config.MODEL_PATH, exist_ok=True)
    os.makedirs(config.CHECKPOINT_PATH, exist_ok=True)
    os.makedirs(os.path.join('data', 'auto_generated'), exist_ok=True)
    
    print("🚀 Starting Unsloth Web API...")
    print(f"📁 Data: {config.DATA_PATH}")
    print(f"🤖 Models: {config.MODEL_PATH}")
    print(f"💾 Database: conversations.db")
    app.run(debug=True, host='0.0.0.0', port=5000)