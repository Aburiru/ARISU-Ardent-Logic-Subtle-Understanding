# chatbot.py

class Chatbot:
    def __init__(self, name, system_prompt):
        self.name = name
        self.system_prompt = system_prompt  # ARISU's full personality
        self.conversation_history = []      # Stores back-and-forth messages
    
    def add_message(self, role, content):
        """
        Adds a message to conversation history
        role = either "user" or "assistant"
        content = the actual message text
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_full_context(self):
        """
        Prepares the full conversation for the AI
        Returns: list of message dictionaries
        """
        # Start with ARISU's system prompt
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add all conversation history
        messages.extend(self.conversation_history)
        
        return messages
    
    def clear_history(self):
        """Clears conversation history (fresh start)"""
        self.conversation_history = []
    
    def get_recent_context(self, num_messages=10):
        """
        Gets only recent messages to save tokens
        num_messages = how many recent exchanges to keep
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Get last N messages
        recent = self.conversation_history[-num_messages:]
        messages.extend(recent)
        
        return messages