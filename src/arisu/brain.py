# ai_brain.py

import requests
import json
import re
import sys # Added for sys.stderr
from .config import MODEL_NAME, ARISU_BASE_URL, ARISU_API_KEY, OLLAMA_TIMEOUT

class AIBrain:
    def __init__(self):
        """
        Initialize connection to 9router cloud AI bridge.
        """
        self.api_url = ARISU_BASE_URL + "/chat/completions"  # OpenAI-compatible endpoint
        self.api_key = ARISU_API_KEY
        self.model = MODEL_NAME
    
    def chat(self, messages):
        thought, response = self.chat_with_thought(messages)
        return response

    def chat_with_thought(self, messages):
        """
        Send conversation to 9router and get response with internal monologue.
        Supports streaming for better perceived performance.
        
        messages = list of message dictionaries
        Returns: (thought_process, final_response)
        """
        
        # Prepare the request (model optional for 9router combined API)
        payload = {
            "messages": messages,
            "stream": True,
            "temperature": 0.7
        }
        if self.model:
            payload["model"] = self.model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        full_content = ""
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=OLLAMA_TIMEOUT,
                stream=True
            )
            
            if response.status_code == 200:
                print("ARISU is thinking...", end="", file=sys.stderr, flush=True)
                for line in response.iter_lines():
                        if line:
                            # print(f"DEBUG: Raw line: {line}", file=sys.stderr) # Remove debug print
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                decoded_line = decoded_line[len('data: '):].strip()
                            if not decoded_line: # Skip empty lines after stripping
                                continue
                            
                            chunk = json.loads(decoded_line)
                            if 'choices' in chunk:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content_chunk = delta['content']
                                    full_content += content_chunk
                                    if len(full_content) % 50 == 0:
                                        print(".", end="", file=sys.stderr, flush=True)
                print(" Done.", file=sys.stderr)
                
                full_content = full_content.strip()

                # Extract thought block
                thought_match = re.search(r'<thought\s*>(.*?)</thought\s*>', full_content, re.DOTALL | re.IGNORECASE)
                thought = thought_match.group(1).strip() if thought_match else ""

                # Remove thought tags from final response
                final_response = re.sub(r'<thought\s*>.*?</thought\s*>', '', full_content, flags=re.DOTALL | re.IGNORECASE)
                final_response = re.sub(r'<thought\s*>', '', final_response, flags=re.IGNORECASE)
                final_response = re.sub(r'</thought\s*>', '', final_response, flags=re.IGNORECASE)
                final_response = final_response.strip()

                return thought, final_response
            
            else:
                return "", f"API Error {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return "", "9router bridge is not running. Please ensure the bridge is active at localhost:20128."
        
        except requests.exceptions.Timeout:
            return "", "The AI is taking too long to respond. The model might be overloaded."
        
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
