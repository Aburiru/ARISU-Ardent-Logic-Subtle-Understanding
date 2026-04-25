# ai_brain.py

import requests
import json
from config import MODEL_NAME, OLLAMA_API_URL, OLLAMA_TIMEOUT

class AIBrain:
    def __init__(self):
        """
        Initialize connection to Ollama (runs locally on your computer)
        No API key needed!
        """
        self.api_url = OLLAMA_API_URL
        self.model = MODEL_NAME
    
    def chat(self, messages):
        """
        Send conversation to Ollama and get response
        
        messages = list of message dictionaries
        Returns: ARISU's response as a string
        """
        
        # Prepare the request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ollama returns: {"message": {"role": "assistant", "content": "..."}}
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"].strip()
                else:
                    return f"Unexpected format from Ollama: {result}"
            
            else:
                return f"Ollama Error {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "❌ Ollama isn't running. Please ensure Ollama is installed and running (`ollama serve`)."
        
        except requests.exceptions.Timeout:
            return "The AI is taking too long to respond. Ollama might be overloaded or the model is too large for your hardware."
        
        except Exception as e:
            return f"Brain Error: {str(e)}"
