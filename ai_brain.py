# ai_brain.py

import requests
import json
import re
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
        thought, response = self.chat_with_thought(messages)
        return response

    def chat_with_thought(self, messages):
        """
        Send conversation to Ollama and get response with internal monologue
        
        messages = list of message dictionaries
        Returns: (thought_process, final_response)
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
                
                if "message" in result and "content" in result["message"]:
                    full_content = result["message"]["content"].strip()
                    
                    # Extract thought block
                    thought_match = re.search(r'<thought>(.*?)</thought>', full_content, re.DOTALL)
                    thought = thought_match.group(1).strip() if thought_match else ""
                    
                    # Remove thought block from final response
                    final_response = re.sub(r'<thought>.*?</thought>', '', full_content, flags=re.DOTALL).strip()
                    
                    return thought, final_response
                else:
                    return "", f"Unexpected format from Ollama: {result}"
            
            else:
                return "", f"Ollama Error {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "", "❌ Ollama isn't running. Please ensure Ollama is installed and running (`ollama serve`)."
        
        except requests.exceptions.Timeout:
            return "", "The AI is taking too long to respond. Ollama might be overloaded or the model is too large for your hardware."
        
        except Exception as e:
            return "", f"Brain Error: {str(e)}"
