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
        current_strategies = "; ".join(self.memory.facts.get('response_strategies', []))

        # Multi-phase reflection prompt
        prompt = f"""[SYSTEM REFLECTION & SELF-DEVELOPMENT MODE]
You are performing an autonomous reflection on your recent interactions with Gabriel.
This is a meta-cognitive process to improve your effectiveness as his AI companion.

RECENT CONVERSATION HISTORY:
{history_text}

CURRENT KNOWN FACTS ABOUT GABRIEL:
{current_facts}

CURRENT EFFECTIVE RESPONSE STRATEGIES:
{current_strategies}

TASK 1 - IMPLICIT FACTS EXTRACTION:
Analyze the history for 'implicit' facts about Gabriel (habits, priorities, recurring problems, emotional patterns).

TASK 2 - RESPONSE EFFECTIVENESS ANALYSIS:
Identify which of your response styles/approaches worked well:
- When did Gabriel engage more positively?
- Which response formats (detailed vs concise, technical vs emotional) received better reception?
- What communication patterns should you reinforce?

TASK 3 - SELF-DEVELOPMENT ADAPTATION:
Identify areas where YOUR behavior should adapt:
- Are there recurring misunderstandings that suggest your communication style needs adjustment?
- What patterns in Gabriel's messages suggest he needs different support?
- How should you evolve your approach based on recent interactions?

Format your output as a JSON object with these keys:
{{
  "implicit_facts": ["fact1", "fact2"],
  "effective_strategies": ["strategy1", "strategy2"],
  "adaptation_needs": ["adaptation1", "adaptation2"]
}}

If no insights in a category, use empty arrays. Only output valid JSON.
"""

        thought, reflection_json = self.brain.chat_with_thought([{"role": "user", "content": prompt}])

        try:
            reflection_data = json.loads(reflection_json)

            # Process implicit facts
            if isinstance(reflection_data.get("implicit_facts"), list):
                for fact in reflection_data["implicit_facts"]:
                    if self.memory.add_fact("arisu_facts", fact):
                        logger.info(f"✨ Autonomous Insight: {fact}")

            # Process effective strategies
            if isinstance(reflection_data.get("effective_strategies"), list):
                for strategy in reflection_data["effective_strategies"]:
                    if self.memory.add_fact("response_strategies", strategy):
                        logger.info(f"📈 Effective Strategy Identified: {strategy}")

            # Process adaptation needs
            if isinstance(reflection_data.get("adaptation_needs"), list):
                for adaptation in reflection_data["adaptation_needs"]:
                    if self.memory.add_fact("adaptation_patterns", adaptation):
                        logger.info(f"🔄 Adaptation Pattern: {adaptation}")

            if not any([reflection_data.get("implicit_facts"),
                       reflection_data.get("effective_strategies"),
                       reflection_data.get("adaptation_needs")]):
                logger.info("No new insights discovered in this pass.")

        except Exception as e:
            logger.error(f"Failed to parse reflection: {e}")
            logger.debug(f"Raw reflection: {reflection_json}")

if __name__ == "__main__":
    reflector = ArisuReflector()
    last_reflected_count = 0
    
    while True:
        try:
            history = reflector.load_history()
            current_count = len(history)
            
            # Only reflect if we have at least 5 new messages or it's the first run
            if current_count >= last_reflected_count + 5:
                reflector.reflect()
                last_reflected_count = current_count
                logger.info(f"Reflection complete. Next pass after {current_count + 5} messages.")
            else:
                logger.info(f"Skipping reflection: only {current_count - last_reflected_count} new messages (need 5).")
                
        except Exception as e:
            logger.error(f"Reflector Loop Error: {e}")
        
        # Check every 15 minutes instead of 30, but the message count guard prevents waste
        time.sleep(900)
