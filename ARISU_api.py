# ARISU_api.py - Flask API for ARISU HTA app
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import random

# Import shared modules
from chatbot import Chatbot
from ai_brain import AIBrain
from emotion_detector import EmotionDetector
from config import (
    API_HOST, API_PORT, 
    HISTORY_FILE, 
    ARISU_SYSTEM_PROMPT
)

app = Flask(__name__)
CORS(app)  # Allow HTA to access API

# Initialize ARISU components
arisu = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
brain = AIBrain()
detector = EmotionDetector()

def load_history():
    """Load conversation history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                arisu.conversation_history = data.get('messages', [])
                detector.message_count = data.get('message_count', 0)
                detector.emotion_history = data.get('emotions', [])
        except Exception as e:
            print(f"⚠️ History load error: {e}")

def save_history():
    """Save conversation history to file"""
    data = {
        'messages': arisu.conversation_history,
        'message_count': detector.message_count,
        'emotions': detector.emotion_history
    }
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ History save error: {e}")

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
        
        # 1. Detect emotion
        emotion, intensity, indicators = detector.detect_emotion(user_message)
        
        # 2. Add message to history
        arisu.add_message("user", user_message)
        
        # 3. Get response with context and emotion hint
        emotion_hint = None
        if emotion != 'neutral' and intensity > 0:
            emotion_hint = f"[User seems {emotion} (intensity: {intensity}). Respond accordingly.]"
        
        context = arisu.get_full_context(emotion_hint=emotion_hint)
        response = brain.chat(context)
        
        # 4. Add response to history
        arisu.add_message("assistant", response)
        
        # 5. Save and return
        save_history()
        
        return jsonify({
            'response': response,
            'emotion': emotion if emotion != 'neutral' else None,
            'intensity': intensity,
            'timestamp': datetime.now().strftime("%H:%M")
        })
    
    except Exception as e:
        print(f"❌ Error in /api/chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics (FIXED version)"""
    try:
        # Get stats directly from detector
        stats = detector.get_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Error in /api/stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        arisu.clear_history()
        detector.conversation_start = datetime.now()
        detector.message_count = 0
        detector.emotion_history = []
        save_history()
        return jsonify({'success': True})
    except Exception as e:
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

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     ✦ ARISU API Server (Refactored)")
    print("="*60)
    print(f"\n✅ API running on http://{API_HOST}:{API_PORT}")
    print("🚀 Now launch ARISU.hta\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=False)