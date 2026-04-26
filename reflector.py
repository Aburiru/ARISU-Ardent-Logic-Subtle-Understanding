# reflector.py - Autonomous background reflection for ARISU
import time
import logging
import json
import os
from ai_brain import AIBrain
from memory_manager import MemoryManager
from config import HISTORY_FILE, LOG_FILE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (Reflector) %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ARISU_Reflector")

class ArisuReflector:
    def __init__(self):
        self.brain = AIBrain()
        self.memory = MemoryManager()
        
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('messages', [])
        return []

    def reflect(self):
        """Perform a reflection pass over the conversation history"""
        history = self.load_history()
        if not history:
            logger.info("No history to reflect on.")
            return

        logger.info("Starting autonomous reflection pass...")
        
        # Prepare context for reflection
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-30:]])
        current_facts = "; ".join(self.memory.facts.get('user_facts', []))
        
        prompt = f"""[SYSTEM REFLECTION MODE]
You are performing an autonomous reflection on your recent interactions with Gabriel.
Your goal is to identify new patterns, deeper facts, or logical connections that weren't explicitly stated but are evident from the dialogue.

RECENT HISTORY:
{history_text}

CURRENT KNOWN FACTS:
{current_facts}

TASK:
1. Analyze the history for 'implicit' facts about Gabriel (habits, priorities, recurring problems).
2. Identify any logical inconsistencies Gabriel might be facing that you should address later.
3. Formulate these as concise 'Arisu Notes' for your long-term memory.

Format your output as a JSON list of strings, like this:
["Gabriel tends to prioritize speed over accuracy when frustrated.", "The current project architecture has a bottleneck in the API layer."]
Only output the JSON list. If no new insights, output [].
"""
        
        # We use a direct chat call here to avoid the normal thought/response split for this internal task
        # But we can still use chat_with_thought if we want her to 'think' about her reflection
        thought, reflection_json = self.brain.chat_with_thought([{"role": "user", "content": prompt}])
        
        try:
            new_notes = json.loads(reflection_json)
            if isinstance(new_notes, list) and new_notes:
                for note in new_notes:
                    if self.memory.add_fact("arisu_facts", note):
                        logger.info(f"✨ Autonomous Insight: {note}")
            else:
                logger.info("No new insights discovered in this pass.")
        except Exception as e:
            logger.error(f"Failed to parse reflection: {e}")
            logger.debug(f"Raw reflection: {reflection_json}")

if __name__ == "__main__":
    reflector = ArisuReflector()
    while True:
        try:
            reflector.reflect()
        except Exception as e:
            logger.error(f"Reflector Loop Error: {e}")
        
        # Reflect every 30 minutes (1800 seconds)
        # In a real production environment, this could be longer or triggered by message counts
        logger.info("Reflector sleeping for 30 minutes...")
        time.sleep(1800)
