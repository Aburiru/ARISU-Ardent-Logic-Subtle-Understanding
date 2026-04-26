# ARISU_api.py - Flask API for ARISU HTA app
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import random
import logging

# Import shared modules
from chatbot import Chatbot
from ai_brain import AIBrain
from emotion_detector import EmotionDetector
from voice_handler import VoiceHandler
from memory_manager import MemoryManager
from config import (
    API_HOST, API_PORT, 
    HISTORY_FILE, FACTS_FILE, LOG_FILE,
    ARISU_SYSTEM_PROMPT
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ARISU_API")

app = Flask(__name__)
CORS(app)  # Allow HTA to access API

# Initialize ARISU components
arisu = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
brain = AIBrain()
detector = EmotionDetector()
voice = VoiceHandler()
memory = MemoryManager()

def extract_facts(user_message, ai_response):
    """Simple rule-based fact extraction"""
    import re
    # Patterns for user telling things to ARISU
    user_patterns = [
        r"(?:remember that|my favorite|i like|i love) (.*)",
        r"i am (?:a|an) (.*)",
        r"i work as (?:a|an) (.*)"
    ]
    
    for pattern in user_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            fact = match.group(1).strip()
            fact = re.sub(r'[?.!]$', '', fact)
            memory.add_fact("user_facts", fact)

def load_history():
    """Load conversation history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                arisu.conversation_history = data.get('messages', [])
                detector.message_count = data.get('message_count', 0)
                detector.emotion_history = data.get('emotions', [])
            logger.info(f"Successfully loaded history from {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"History load error: {e}")

def save_history():
    """Save conversation history to file"""
    data = {
        'messages': arisu.conversation_history,
        'message_count': detector.message_count,
        'emotions': detector.emotion_history,
        'last_updated': datetime.now().isoformat()
    }
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"History save error: {e}")

# Load history on startup
load_history()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        logger.info(f"User: {user_message[:50]}...")
        
        # 1. Detect emotion
        emotion, intensity, indicators = detector.detect_emotion(user_message)
        logger.info(f"Detected emotion: {emotion} (intensity: {intensity})")
        
        # 2. Add message to history
        arisu.add_message("user", user_message)
        
        # 3. Get response with context, memory, and emotion hint
        facts_summary = memory.get_facts_summary()
        
        emotion_hint = facts_summary # Inject facts first
        if emotion != 'neutral' and intensity >= 1.0:
            emotion_hint += f"\n[System Note: Gabriel appears {emotion}. Intensity: {intensity:.1f}. Respond with your systematic reasoning, maintaining your composed and analytical tone while addressing this state.]"
        
        context = arisu.get_full_context(emotion_hint=emotion_hint)
        thought, response = brain.chat_with_thought(context)
        
        if thought:
            logger.info(f"ARISU Thought: {thought}")
        
        # 4. Extract new facts to remember for next time
        extract_facts(user_message, response)
        
        # 4. Add response to history
        arisu.add_message("assistant", response)

        # 5. Speak response in background thread (so text appears first)
        import threading
        def handle_speech():
            try:
                voice.speak(response, emotion)
            except Exception as ve:
                logger.error(f"Voice error: {ve}")

        threading.Thread(target=handle_speech, daemon=True).start()

        # 6. Save and return
        save_history()
        
        logger.info(f"ARISU: {response[:50]}...")
        
        return jsonify({
            'response': response,
            'thought': thought,
            'emotion': emotion if emotion != 'neutral' else None,
            'intensity': round(intensity, 2),
            'timestamp': datetime.now().strftime("%H:%M"),
            'debug': {
                'indicators': indicators,
                'trend': detector.get_emotion_trend()
            }
        })
    
    except Exception as e:
        logger.exception(f"Error in /api/chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics"""
    try:
        stats = detector.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history and long-term memory"""
    try:
        # 1. Clear conversation history
        arisu.clear_history()
        detector.conversation_start = datetime.now()
        detector.message_count = 0
        detector.emotion_history = []
        save_history()
        
        # 2. Clear long-term facts
        memory.facts = {"user_facts": [], "arisu_facts": [], "shared_history": []}
        memory.save_facts()
        
        logger.info("Conversation history and long-term facts cleared.")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in /api/clear: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/greeting', methods=['GET'])
def get_greeting():
    """Get time-based greetings"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        greetings = ["...Morning. Early bird, aren't you?", "Hmph. Morning. Did you sleep?"]
    elif 12 <= hour < 17:
        greetings = ["...Afternoon. What took you so long?", "...It's the afternoon. Have you eaten?"]
    elif 17 <= hour < 21:
        greetings = ["...Evening. Long day?", "Evening. Don't work too hard."]
    else:
        greetings = ["...Why are you still awake?", "Can't sleep? Fine... I'll keep you company."]
    
    return jsonify({'greeting': random.choice(greetings)})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get full conversation history"""
    return jsonify({'messages': arisu.conversation_history})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Check API and Brain status"""
    # Simple check for Ollama would be good here but might be slow
    return jsonify({
        'status': 'online',
        'model': brain.model,
        'uptime': detector.get_conversation_duration()[1]
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update ARISU settings"""
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            if 'voice_mode' in data:
                mode = data['voice_mode']
                if mode == 'rvc':
                    if voice.rvc_inference:
                        voice.rvc_active = True
                    else:
                        return jsonify({'error': 'RVC model not loaded'}), 400
                elif mode == 'normal':
                    voice.rvc_active = False
                logger.info(f"Voice mode changed to: {mode}")
            return jsonify({'success': True, 'voice_mode': 'rvc' if voice.rvc_active else 'normal'})
        
        # GET request
        return jsonify({
            'voice_mode': 'rvc' if voice.rvc_active else 'normal',
            'rvc_available': voice.rvc_inference is not None
        })
    except Exception as e:
        logger.error(f"Error in /api/settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the API server and exit"""
    logger.info("Shutdown request received. Exiting...")
    os._exit(0) # Forcefully exit the process and all threads
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     ARISU API Server (Improved)")
    print("="*60)
    print(f"\nAPI running on http://{API_HOST}:{API_PORT}")
    print(f"Logs being written to {LOG_FILE}")
    print("Now launch ARISU.hta\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=False)
