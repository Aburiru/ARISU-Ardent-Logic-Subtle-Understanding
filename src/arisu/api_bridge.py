import sys
import json
import os
import time # Added for time.time()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project's 'src' directory to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Import required modules
from arisu.brain import AIBrain
from arisu.memory import MemoryManager
from arisu.voice import VoiceHandler
from arisu.response_handler import handle_chat

# Initialize components
brain = AIBrain()
memory = MemoryManager()
voice = VoiceHandler()

def process_chat(message):
    # This includes emotion detection, memory integration, and personality processing
    response_text, thought, detected_emotion, intensity, indicators = handle_chat(message)
    
    # Generate audio
    audio_filename = f"arisu_{int(time.time())}.wav"
    audio_path = os.path.join("data", "audio", audio_filename)
    
    return {
        "text": response_text,
        "thought": thought,
        "audioUrl": f"/audio/{audio_filename}"
    }

if __name__ == "__main__":
    message = sys.argv[1]
    result = process_chat(message)
    print(json.dumps(result))