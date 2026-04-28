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
        Supports streaming for better perceived performance.
        
        messages = list of message dictionaries
        Returns: (thought_process, final_response)
        """
        
        # Prepare the request
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,  # Enable streaming
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        full_content = ""
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT,
                stream=True
            )
            
            if response.status_code == 200:
                print("🧠 ARISU is thinking...", end="", flush=True)
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk and 'content' in chunk['message']:
                            content_chunk = chunk['message']['content']
                            full_content += content_chunk
                            # Optional: print dots for progress
                            if len(full_content) % 50 == 0:
                                print(".", end="", flush=True)
                print(" Done.")
                
                full_content = full_content.strip()

                # Extract thought block (robust pattern with flexible whitespace)
                thought_match = re.search(r'<thought\s*>(.*?)</thought\s*>', full_content, re.DOTALL | re.IGNORECASE)
                thought = thought_match.group(1).strip() if thought_match else ""

                # Remove ALL thought-related tags from final response
                # Pattern 1: Complete <thought>...</thought> blocks
                final_response = re.sub(r'<thought\s*>.*?</thought\s*>', '', full_content, flags=re.DOTALL | re.IGNORECASE)
                # Pattern 2: Orphaned opening tags (model sometimes forgets to close)
                final_response = re.sub(r'<thought\s*>', '', final_response, flags=re.IGNORECASE)
                # Pattern 3: Orphaned closing tags
                final_response = re.sub(r'</thought\s*>', '', final_response, flags=re.IGNORECASE)
                # Clean up any leading/trailing whitespace
                final_response = final_response.strip()

                return thought, final_response
            
            else:
                return "", f"Ollama Error {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "", "❌ Ollama isn't running. Please ensure Ollama is installed and running (`ollama serve`)."
        
        except requests.exceptions.Timeout:
            return "", "The AI is taking too long to respond. Ollama might be overloaded or the model is too large for your hardware."
        
        except Exception as e:
            return "", f"Brain Error: {str(e)}"

    def extract_memories(self, messages):
        """
        Use the LLM to extract key facts and preferences from the recent conversation.
        """
        if len(messages) < 2:
            return []

        extraction_prompt = {
            "role": "system",
            "content": "Analyze the conversation above. Extract any NEW key facts about the user (Gabriel), their preferences, or important notes about ARISU. Format each as a single concise sentence. Return ONLY a JSON list of strings, e.g., [\"User likes coffee\", \"ARISU should be more direct\"]. If nothing new, return []."
        }
        
        # We only want to analyze the last few exchanges
        recent_context = messages[-6:] + [extraction_prompt]
        
        try:
            _, response_text = self.chat_with_thought(recent_context)
            # Try to find JSON list in response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Memory extraction error: {e}")
        return []

    def summarize_conversation(self, messages):
        """
        Create a concise summary of the conversation to be stored in long-term memory.
        """
        summarization_prompt = {
            "role": "system",
            "content": "Summarize the core topics and conclusions of this conversation in 2-3 concise sentences. Focus on what was achieved or decided. This summary will be used as long-term context."
        }
        
        context = messages + [summarization_prompt]
        
        try:
            _, summary = self.chat_with_thought(context)
            return summary.strip()
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Conversation continued on various topics."
