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
from arisu.response_handler import handle_chat
from arisu.voice import VoiceHandler

# Initialize components
voice = VoiceHandler()

def process_chat(message):
    # This includes emotion detection, memory integration, and personality processing
    response_text, thought, detected_emotion, intensity, indicators = handle_chat(message)
    
    # Generate audio with RVC conversion (Frieren voice)
    emotion = detected_emotion if detected_emotion else 'neutral'
    audio_path = voice.generate_and_convert(response_text, emotion)
    
    if audio_path and os.path.exists(audio_path):
        # Move to data/audio for static serving
        import shutil
        # Resolve audio_dir relative to the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        audio_dir = os.path.join(project_root, 'data', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        audio_filename = f"arisu_{int(time.time())}.wav"
        final_path = os.path.join(audio_dir, audio_filename)
        shutil.move(audio_path, final_path)
        audio_url = f"/audio/{audio_filename}"
    else:
        audio_url = None
    
    return {
        "text": response_text,
        "thought": thought,
        "audioUrl": audio_url
    }

if __name__ == "__main__":
    message = sys.argv[1]
    result = process_chat(message)
    print(f"__ARISU_JSON__{json.dumps(result)}")