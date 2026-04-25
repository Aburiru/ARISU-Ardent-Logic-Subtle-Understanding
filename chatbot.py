# chatbot.py - Data container for ARISU's conversation
from config import ARISU_SYSTEM_PROMPT, MAX_HISTORY_MESSAGES

class Chatbot:
    def __init__(self, name="ARISU", system_prompt=None):
        """
        Initialize the chatbot with a name and system prompt.
        If no prompt is provided, use the default from config.
        """
        self.name = name
        self.system_prompt = system_prompt or ARISU_SYSTEM_PROMPT
        self.conversation_history = []  # List of {"role": "...", "content": "..."}
    
    def add_message(self, role, content):
        """Adds a message to the conversation history and prunes if necessary."""
        self.conversation_history.append({"role": role, "content": content})
        
        # Prune history to keep it within context limits
        if len(self.conversation_history) > MAX_HISTORY_MESSAGES:
            self.conversation_history = self.conversation_history[-MAX_HISTORY_MESSAGES:]
    
    def get_full_context(self, emotion_hint=None):
        """
        Prepares the list of messages for the AI model with pruning.
        If emotion_hint is provided, it's inserted as a system message.
        Includes a strict reminder of the user's name.
        """
        name_reminder = "[System Note: The person you are talking to is strictly named 'abril'. Never call them April or anything else.]"
        
        system_content = self.system_prompt + f"\n\n{name_reminder}"
        messages = [{"role": "system", "content": system_content}]
        
        # Copy history so we don't accidentally mutate the original
        history = list(self.conversation_history)
        
        # Insert emotion hint if provided
        if emotion_hint and len(history) > 0:
            # Insert before the last user message if possible to guide the AI's response
            if history[-1]["role"] == "user":
                history.insert(-1, {"role": "system", "content": emotion_hint})
            else:
                history.append({"role": "system", "content": emotion_hint})
        
        messages.extend(history)
        return messages
    
    def clear_history(self):
        """Clears the history for a fresh start."""
        self.conversation_history = []
    
    def get_recent_context(self, num_messages=10):
        """Returns only the most recent N messages to save tokens."""
        messages = [{"role": "system", "content": self.system_prompt}]
        recent = self.conversation_history[-num_messages:]
        messages.extend(recent)
        return messages
