"""Response handler – orchestrates a full ARISU turn.

Keeps the heavy‑weight modules (EmotionDetector, AIBrain, MemoryManager, Chatbot) as
separate, testable units, but provides a single function `handle_chat(message)` that
covers the entire request flow.  This makes it easy to call from the Flask API,
from a CLI script, or from unit tests.
"""

import threading
import logging
import os
import json
from .chatbot   import Chatbot
from .brain     import AIBrain
from .emotions  import EmotionDetector
from .memory    import MemoryManager
from .config    import (
    ARISU_SYSTEM_PROMPT,
    HISTORY_SUMMARY_THRESHOLD,
    HISTORY_FILE, FACTS_FILE, LOG_FILE # These are needed for load/save
)
from datetime import datetime

logger = logging.getLogger("ARISU_ResponseHandler")

# Singleton instances – shared across the process
_arisu   = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
_brain   = AIBrain()
_detector= EmotionDetector()
_memory  = MemoryManager()

# ponytail: Original load_history from api.py, adapted for singletons
def load_history():
    """Load conversation history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _arisu.conversation_history = data.get('messages', [])
                _detector.message_count = data.get('message_count', 0)
                _detector.emotion_history = data.get('emotions', [])
            logger.info(f"Successfully loaded history from {HISTORY_FILE}")
        except Exception as e:
            logger.error(f"History load error: {e}")

# ponytail: Original save_history from api.py, adapted for singletons
def save_history():
    """Save conversation history to file"""
    data = {
        'messages': _arisu.conversation_history,
        'message_count': _detector.message_count,
        'emotions': _detector.emotion_history,
        'last_updated': datetime.now().isoformat()
    }
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"History save error: {e}")

# Load history on startup
load_history()

def _perform_memory_maintenance():
    """Mirror the original `perform_memory_maintenance` logic.
    Extracts new facts, adds them to memory, and summarises the conversation
    when the history grows beyond `HISTORY_SUMMARY_THRESHOLD`.
    """
    try:
        # 1. Extract facts from recent conversation
        recent_messages = _arisu.conversation_history[-10:]
        new_facts = _brain.extract_memories(recent_messages)
        if new_facts:
            for fact in new_facts:
                _memory.add_fact("user_facts", fact)
            logger.info(f"🧠 Extracted {len(new_facts)} new facts from conversation.")

        # 2. Summarise if needed
        if len(_arisu.conversation_history) >= HISTORY_SUMMARY_THRESHOLD:
            logger.info("📝 Conversation history reached threshold. Summarising…")
            summary = _brain.summarize_conversation(_arisu.conversation_history)
            _memory.add_summary(summary)
            # Keep a fraction of the history after summarisation
            keep = HISTORY_SUMMARY_THRESHOLD // 3
            _arisu.conversation_history = _arisu.conversation_history[-keep:]
            logger.info(f"✅ History summarised, kept last {keep} messages.")
            save_history() # ponytail: moved save_history here after summarization
    except Exception as e:
        logger.error(f"Memory maintenance error: {e}")

def handle_chat(user_message: str):
    """Process a single user message.

    Returns a tuple `(response_text, thought_block, detected_emotion)`.
    The function is deliberately small – it just wires the existing components
    together, preserving their original behaviour.
    """
    # 1️⃣ Detect emotion
    emotion, intensity, indicators = _detector.detect_emotion(user_message)

    # 2️⃣ Store user message
    _arisu.add_message("user", user_message)

    # 3️⃣ Build context – include long‑term facts and optional emotion hint
    facts_summary = _memory.get_facts_summary()
    emotion_hint = facts_summary
    if emotion != "neutral" and intensity >= 1.0:
        emotion_hint += f"\n[System Note: Gabriel appears {emotion}. Intensity: {intensity:.1f}. " \
                       "Respond with systematic reasoning, staying composed.]"
    
    # Build adaptation context from learned patterns (copied from api.py)
    adaptation_context = None
    recent_adaptations = _memory.get_adaptation_history()[-3:]  # Last 3 adaptations
    effective_strategies = _memory.get_effective_strategies()[-3:]  # Last 3 effective strategies
    if recent_adaptations or effective_strategies:
        adaptation_context = "[ADAPTATION GUIDANCE BASED ON PAST INTERACTIONS]\n"
        if effective_strategies:
            adaptation_context += "Strategies that worked well: " + "; ".join(effective_strategies) + "\n"
        if recent_adaptations:
            adaptation_context += "Areas needing adjustment: " + "; ".join(recent_adaptations) + "\n"
        adaptation_context += "[Use these insights to adapt your communication style while maintaining your core personality.]"


    # 4️⃣ Get full context from Chatbot (history + system prompt)
    context = _arisu.get_full_context(emotion_hint=emotion_hint, adaptation_context=adaptation_context)

    # 5️⃣ Call Ollama via AIBrain
    thought, response = _brain.chat_with_thought(context)

    # 6️⃣ Store AI response
    _arisu.add_message("assistant", response)

    # 7️⃣ Fire off async memory maintenance (non‑blocking)
    threading.Thread(target=_perform_memory_maintenance, daemon=True).start()

    # Return the pieces the Flask route (or tests) care about
    return response, thought, emotion if emotion != "neutral" else None, intensity, indicators