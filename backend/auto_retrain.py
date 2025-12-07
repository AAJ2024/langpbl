import time
import database
import requests
from datetime import datetime

RETRAIN_THRESHOLD = 50  # Retrain after 50 new conversations
CHECK_INTERVAL = 3600   # Check every hour (3600 seconds)

def should_retrain():
    """Check if we have enough conversations to retrain"""
    stats = database.get_conversation_stats()
    return stats['pending_training'] >= RETRAIN_THRESHOLD

def trigger_retrain(model_id):
    """Trigger retraining via API"""
    try:
        response = requests.post(
            'http://localhost:5000/api/retrain',
            json={'model_id': model_id}
        )
        if response.status_code == 200:
            print(f"✅ Auto-retrain started at {datetime.now()}")
            return True
        else:
            print(f"❌ Retrain failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error triggering retrain: {e}")
        return False

def run_auto_retrain(model_id):
    """Main loop for auto-retraining"""
    print(f"🤖 Auto-retrain monitor started for model: {model_id}")
    print(f"📊 Will retrain after {RETRAIN_THRESHOLD} new conversations")
    print(f"⏰ Checking every {CHECK_INTERVAL} seconds\n")
    
    while True:
        try:
            if should_retrain():
                print(f"🚀 Threshold reached! Starting retrain...")
                trigger_retrain(model_id)
            else:
                stats = database.get_conversation_stats()
                print(f"📊 Status: {stats['pending_training']}/{RETRAIN_THRESHOLD} conversations")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Auto-retrain monitor stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto_retrain.py <model_id>")
        sys.exit(1)
    
    model_id = sys.argv[1]
    run_auto_retrain(model_id)