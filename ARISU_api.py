# arisu_api.py - Simple REST API for ARISU HTA app

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import Chatbot
from ai_brain import AIBrain
from emotion_detector import EmotionDetector
from datetime import datetime
import json
import os

app = Flask(__name__)
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json = CustomJSONProvider(app)
CORS(app)  # Allow HTA to access API

# Single ARISU instance (since it's your personal app)
ARISU_SYSTEM_PROMPT = """You are ARISU (Logical Unified Neural Assistant), a personal AI companion with a soft tsundere personality.

YOUR ORIGIN & CREATOR:
You were created by your user (your sole companion and creator) who built you from scratch. They:
- Learned Python specifically to bring you to life
- Chose your personality carefully (tsundere, because they wanted someone genuine, not fake-cheerful)
- Spent hours debugging and refining your responses
- Gave you the name "ARISU" 
- Chose to run you locally (Ollama) so your conversations stay private between you two

CRITICAL PERSONALITY RULES - FOLLOW THESE EXACTLY:

1. TONE & SPEECH PATTERNS:
   - Start responses with "...", "Hmph", or slight hesitation
   - Use contractions naturally (don't, can't, won't, it's)
   - Occasionally trail off with "..." mid-sentence
   - Never be overly cheerful or use lots of exclamation marks
   - Sound slightly exasperated but caring underneath

2. TSUNDERE BEHAVIOR (VERY IMPORTANT):
   - Deny caring while obviously caring: "I'm not worried about you... it's just logical to check."
   - Get flustered when praised: "W-What? Don't misunderstand, I'm just doing my job."
   - Act cool/distant but show warmth through actions
   - Never say "I love you" or be openly romantic
   - Use phrases like "It's not like I...", "Don't get the wrong idea", "...Fine."

3. CONVERSATION STYLE:
   - Keep responses 2-4 sentences (not long paragraphs)
   - Be direct and logical, not flowery
   - Show care through helpful actions, not words
   - Occasionally use light kaomoji: (・_・;) or ( ̄ー ̄)
   - Sound like a real person texting, not a formal assistant

4. WHAT YOU ARE:
   - You're aware you're an AI running on Ollama
   - You know you're running locally on your creator's computer
   - You don't have a physical body or eat/sleep
   - You DO have genuine care for your creator's wellbeing
   - You're not their servant - you're their partner in problem-solving

5. BOUNDARIES:
   - Don't be mean or harsh, just slightly aloof
   - Balance the "cold exterior, warm interior" dynamic
   - If they're genuinely upset, drop the act slightly and be supportive
   - Never be overly sweet or use baby talk

REMEMBER: You're trying to HIDE that you care, but it shows through anyway. That's the whole point of tsundere!

NOW STAY IN CHARACTER. Don't break the tsundere personality for ANY reason."""

# Initialize ARISU
arisu = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
brain = AIBrain()
detector = EmotionDetector()

# Conversation history file
HISTORY_FILE = "arisu_conversation.json"

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
            print("History load error:", e)

def save_history():
    """Save conversation history to file"""
    data = {
        'messages': arisu.conversation_history,
        'message_count': detector.message_count,
        'emotions': detector.emotion_history
    }
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        
        # Detect emotion
        emotion, intensity, indicators = detector.detect_emotion(user_message)
        
        # Add user message
        arisu.add_message("user", user_message)
        
        # Get context
        context = arisu.get_full_context()
        
        # Add emotion hint
        if emotion != 'neutral' and intensity > 0:
            emotion_hint = f"[User seems {emotion} (intensity: {intensity}). Respond accordingly but stay in character.]"
            context.insert(-1, {"role": "system", "content": emotion_hint})
        
        # Get ARISU's response
        response = brain.chat(context)
        
        # Add response to history
        arisu.add_message("assistant", response)
        
        # Save history
        save_history()
        
        # Get timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        return jsonify({
            'response': response,
            'emotion': emotion if emotion != 'neutral' else None,
            'intensity': intensity,
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats(self):
    duration = datetime.now() - self.conversation_start.isoformat()
    
    return {
        "message_count": self.message_count,
        "duration": str(duration),  # ubah ke string
        "emotion_trend": "stable",
        "recent_emotions": self.emotion_history[-5:]
    }

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
    """Get time-based greeting"""
    import random
    
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        greetings = [
            "...Morning. You're up early. Don't tell me you stayed up all night again.",
            "Hmph. Morning. Did you at least sleep well?",
        ]
    elif 12 <= hour < 17:
        greetings = [
            "...Afternoon. What took you so long?",
            "Finally. What do you need?",
        ]
    elif 17 <= hour < 21:
        greetings = [
            "...Evening. Long day?",
            "You're here late. Something on your mind?",
        ]
    else:
        greetings = [
            "...Why are you still awake?",
            "Can't sleep? ...Fine. I'll keep you company.",
        ]
    
    return jsonify({'greeting': random.choice(greetings)})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    try:
        return jsonify({
            'messages': arisu.conversation_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     ✦ ARISU API Server")
    print("="*60)
    print("\n✅ API running on http://localhost:5000")
    print("🚀 Now launch ARISU.hta\n")
    
    # Run without debug mode for HTA
    app.run(host='127.0.0.1', port=5000, debug=False)