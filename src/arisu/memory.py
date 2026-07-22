# memory_manager.py - Long-term fact storage for ARISU
import json
import os
import logging
from config import FACTS_FILE, MAX_FACTS_TO_INJECT

logger = logging.getLogger("ARISU_Memory")

class MemoryManager:
    def __init__(self):
        self.facts_file = FACTS_FILE
        self.facts = self._load_facts()
        # Ensure all categories exist
        self._ensure_categories()

    def _ensure_categories(self):
        """Ensure all memory categories exist"""
        default_categories = ["user_facts", "arisu_facts", "shared_history",
                             "adaptation_patterns", "response_strategies", "user_preferences",
                             "conversation_summaries"]
        for cat in default_categories:
            if cat not in self.facts:
                self.facts[cat] = []

    def _load_facts(self):
        if os.path.exists(self.facts_file):
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading facts: {e}")
        return {"user_facts": [], "arisu_facts": [], "shared_history": [],
                "adaptation_patterns": [], "response_strategies": [], "user_preferences": [],
                "conversation_summaries": []}

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
        
        # Ensure fact is a string
        if not isinstance(fact, str):
            fact = str(fact)
            
        if fact not in self.facts[category]:
            self.facts[category].append(fact)
            self.save_facts()
            logger.info(f"New fact stored in {category}: {fact}")
            return True
        return False

    def add_summary(self, summary_text):
        """Store a summary of past conversations"""
        if "conversation_summaries" not in self.facts:
            self.facts["conversation_summaries"] = []
        
        self.facts["conversation_summaries"].append({
            "date": os.path.getmtime(self.facts_file) if os.path.exists(self.facts_file) else 0,
            "content": summary_text
        })
        self.save_facts()
        logger.info("New conversation summary added to long-term memory.")

    def get_facts_summary(self):
        """Returns a string summary of all known facts to inject into AI context"""
        if not any(self.facts.values()):
            return ""

        summary = "\n[LONG-TERM MEMORY & KNOWN FACTS]\n"

        # Inject recent summaries if available
        if self.facts.get("conversation_summaries"):
            last_summaries = self.facts["conversation_summaries"][-3:]
            summary += "Previous context: " + " | ".join([s["content"] for s in last_summaries]) + "\n"

        # Helper to join only strings with a limit
        def safe_join(fact_list, limit=MAX_FACTS_TO_INJECT):
            recent_facts = fact_list[-limit:]
            return "; ".join([str(f) for f in recent_facts if f])

        if self.facts.get("user_facts"):
            summary += "What I know about Gabriel: " + safe_join(self.facts["user_facts"]) + "\n"
        if self.facts.get("arisu_facts"):
            summary += "My own notes: " + safe_join(self.facts["arisu_facts"]) + "\n"
        if self.facts.get("user_preferences"):
            summary += "Communication preferences: " + safe_join(self.facts["user_preferences"]) + "\n"
        
        return summary

    def add_adaptation_pattern(self, pattern):
        """Store a pattern about system adaptation or behavior adjustment"""
        return self.add_fact("adaptation_patterns", pattern)

    def add_response_strategy(self, strategy):
        """Store an effective response strategy"""
        return self.add_fact("response_strategies", strategy)

    def add_user_preference(self, preference):
        """Store a user communication preference"""
        return self.add_fact("user_preferences", preference)

    def get_adaptation_history(self):
        """Return all adaptation patterns for context injection"""
        return self.facts.get("adaptation_patterns", [])

    def get_effective_strategies(self):
        """Return response strategies that have worked well"""
        return self.facts.get("response_strategies", [])
