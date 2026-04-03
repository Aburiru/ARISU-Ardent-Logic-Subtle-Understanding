# ai_brain.py

import requests
import json

class AIBrain:
    def __init__(self):
        """
        Initialize connection to Ollama (runs locally on your computer)
        No API key needed!
        """
        self.api_url = "http://localhost:11434/api/chat"
        self.model = "llama3.2"
    
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
            print(end="", flush=True)
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # AI running locally can take time
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ollama returns: {"message": {"role": "assistant", "content": "..."}}
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"].strip()
                else:
                    return f"Unexpected format: {result}"
            
            else:
                return f"Error {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "❌ Ollama isn't running. Open Command Prompt and type: ollama serve"
        
        except requests.exceptions.Timeout:
            return "The response took too long. Ollama might be processing."
        
        except Exception as e:
            return f"Error: {str(e)}"