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
    ARISU_SYSTEM_PROMPT, HISTORY_SUMMARY_THRESHOLD
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

import threading
import queue

# Initialize ARISU components
arisu = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
brain = AIBrain()
detector = EmotionDetector()
voice = VoiceHandler()
memory = MemoryManager()

# Speech Queue and Worker
speech_queue = queue.Queue()

def speech_worker():
    """Worker thread to process speech requests sequentially to save RAM/CPU"""
    logger.info("🔊 Speech worker thread started.")
    while True:
        try:
            # Get request from queue (blocks until item available)
            response_text, emotion = speech_queue.get()
            if response_text is None: # Shutdown signal
                break
            
            try:
                voice.speak(response_text, emotion)
            except Exception as ve:
                logger.error(f"Voice worker error: {ve}")
            finally:
                speech_queue.task_done()
        except Exception as e:
            logger.error(f"Speech worker loop error: {e}")

# Start the speech worker thread
threading.Thread(target=speech_worker, daemon=True).start()

def analyze_response_effectiveness(user_message, ai_response, emotion):
    """Analyze if the AI response was effective based on user's follow-up"""
    import re

    # Positive engagement signals
    positive_signals = [
        r"(?:thanks|thank you|thx|appreciate)",
        r"(?:good|great|awesome|nice|perfect|excellent)",
        r"(?:yeah|yes|yep|yup|indeed|correct|right)",
        r"(?:i like|i love|i agree|that helps)",
        r"(?:tell me more|go on|what else|continue)",
        r"(?:\*laughs\*|\*smiles\*|lol|haha)"
    ]

    # Negative/disengagement signals
    negative_signals = [
        r"(?:no|not really|doesn't help|wrong|incorrect)",
        r"(?:confusing|unclear|what do you mean)",
        r"(?:nevermind|forget it|stop)",
        r"(?:\*sighs\*|\*frustrated\*|ugh|wtf)"
    ]

    # Check for positive signals
    for pattern in positive_signals:
        if re.search(pattern, user_message, re.IGNORECASE):
            memory.add_response_strategy(f"Response approach that worked: {ai_response[:100]}...")
            logger.info(f"📈 Positive engagement detected - strategy recorded")
            return "positive"

    # Check for negative signals
    for pattern in negative_signals:
        if re.search(pattern, user_message, re.IGNORECASE):
            memory.add_adaptation_pattern(f"Approach needing adjustment: {ai_response[:100]}...")
            logger.info(f"🔄 Negative feedback detected - adaptation noted")
            return "negative"

    return "neutral"

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

def perform_memory_maintenance():
    """Extract facts and summarize if history is too long"""
    try:
        # 1. Extract facts from recent conversation
        recent_messages = arisu.conversation_history[-10:]
        new_facts = brain.extract_memories(recent_messages)
        if new_facts:
            for fact in new_facts:
                memory.add_fact("user_facts", fact)
            logger.info(f"🧠 Extracted {len(new_facts)} new facts from conversation.")

        # 2. Check if we need to summarize
        if len(arisu.conversation_history) >= HISTORY_SUMMARY_THRESHOLD:
            logger.info("📝 Conversation history reached threshold. Summarizing...")
            summary = brain.summarize_conversation(arisu.conversation_history)
            memory.add_summary(summary)
            
            # Keep only the most recent messages after summarization
            # We keep about 1/3 of the threshold for continuity
            keep_count = HISTORY_SUMMARY_THRESHOLD // 3
            arisu.conversation_history = arisu.conversation_history[-keep_count:]
            logger.info(f"✅ History summarized and pruned to last {keep_count} messages.")
            save_history()
    except Exception as e:
        logger.error(f"Error during memory maintenance: {e}")

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

        emotion_hint = facts_summary  # Inject facts first
        if emotion != 'neutral' and intensity >= 1.0:
            emotion_hint += f"\n[System Note: Gabriel appears {emotion}. Intensity: {intensity:.1f}. Respond with your systematic reasoning, maintaining your composed and analytical tone while addressing this state.]"

        # Build adaptation context from learned patterns
        adaptation_context = None
        recent_adaptations = memory.get_adaptation_history()[-3:]  # Last 3 adaptations
        effective_strategies = memory.get_effective_strategies()[-3:]  # Last 3 effective strategies

        if recent_adaptations or effective_strategies:
            adaptation_context = "[ADAPTATION GUIDANCE BASED ON PAST INTERACTIONS]\n"
            if effective_strategies:
                adaptation_context += "Strategies that worked well: " + "; ".join(effective_strategies) + "\n"
            if recent_adaptations:
                adaptation_context += "Areas needing adjustment: " + "; ".join(recent_adaptations) + "\n"
            adaptation_context += "[Use these insights to adapt your communication style while maintaining your core personality.]"

        context = arisu.get_full_context(emotion_hint=emotion_hint, adaptation_context=adaptation_context)
        thought, response = brain.chat_with_thought(context)
        
        if thought:
            logger.info(f"ARISU Thought: {thought}")
        
        # 4. Add response to history
        arisu.add_message("assistant", response)

        # 5. Perform memory maintenance in a separate thread to avoid blocking response
        threading.Thread(target=perform_memory_maintenance).start()

        # 6. Analyze response effectiveness for self-development
        analyze_response_effectiveness(user_message, response, emotion)

        # 7. Queue speech response (handled by background worker)
        speech_queue.put((response, emotion))

        # 8. Save and return
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
    """Shutdown the API server and all background services"""
    logger.info("Shutdown request received. Cleaning up...")
    
    try:
        # Kill the Reflector process specifically
        # We use taskkill with a filter on the command line if possible, 
        # but on Windows pythonw doesn't show the script name in the image name.
        # So we use a more direct approach: kill all pythonw.exe 
        # (This is what ARISU_Stop.bat does anyway)
        import subprocess
        subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], capture_output=True)
    except Exception as e:
        logger.error(f"Error during subprocess cleanup: {e}")
    
    # Finally exit the API itself
    os._exit(0) 
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     ARISU API Server (Improved)")
    print("="*60)
    print(f"\nAPI running on http://{API_HOST}:{API_PORT}")
    print(f"Logs being written to {LOG_FILE}")
    print("Now launch ARISU.hta\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=False)
