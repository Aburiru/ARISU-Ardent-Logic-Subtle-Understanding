# memory_manager.py - Long-term fact storage for ARISU
import json
import os
import logging
from config import FACTS_FILE

logger = logging.getLogger("ARISU_Memory")

class MemoryManager:
    def __init__(self):
        self.facts_file = FACTS_FILE
        self.facts = self._load_facts()

    def _load_facts(self):
        if os.path.exists(self.facts_file):
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading facts: {e}")
        return {"user_facts": [], "arisu_facts": [], "shared_history": []}

    def save_facts(self):
        try:
            with open(self.facts_file, 'w', encoding='utf-8') as f:
                json.dump(self.facts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving facts: {e}")

    def add_fact(self, category, fact):
        """Add a unique fact to a category"""
        if category not in self.facts:
            self.facts[category] = []
        
        if fact not in self.facts[category]:
            self.facts[category].append(fact)
            self.save_facts()
            logger.info(f"New fact stored in {category}: {fact}")
            return True
        return False

    def get_facts_summary(self):
        """Returns a string summary of all known facts to inject into AI context"""
        if not any(self.facts.values()):
            return ""

        summary = "\n[LONG-TERM MEMORY & KNOWN FACTS]\n"
        if self.facts["user_facts"]:
            summary += "What I know about Gabriel: " + "; ".join(self.facts["user_facts"]) + "\n"
        if self.facts["arisu_facts"]:
            summary += "My own notes: " + "; ".join(self.facts["arisu_facts"]) + "\n"
        
        return summary
