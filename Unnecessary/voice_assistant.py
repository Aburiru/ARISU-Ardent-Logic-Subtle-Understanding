# voice_assistant.py

import speech_recognition as sr
import pyttsx3
import threading

class VoiceAssistant:
    def __init__(self, voice_id=1, rate=160, volume=0.9):
        """
        Initialize voice assistant for ARISU
        
        voice_id = which voice (0=male, 1=female usually)
        rate = speaking speed (150-200 is normal)
        volume = loudness (0.0 to 1.0)
        """
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        
        if voice_id < len(voices):
            self.tts_engine.setProperty('voice', voices[voice_id].id)
        
        self.tts_engine.setProperty('rate', rate)
        self.tts_engine.setProperty('volume', volume)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Calibrate microphone
        print("🎤 Calibrating microphone...")
        self.microphone = sr.Microphone()
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone calibrated!\n")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listen for user's voice
        
        timeout = seconds to wait for speech to START
        phrase_time_limit = max seconds of speech
        Returns: text string or None
        """
        try:
            print("🎤 Listening... (speak now)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔄 Processing speech...")
            
            # Google's free speech-to-text API
            text = self.recognizer.recognize_google(audio)
            print(f"✅ You said: \"{text}\"\n")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected\n")
            return None
            
        except sr.UnknownValueError:
            print("❌ Could not understand (try speaking louder)\n")
            return None
            
        except sr.RequestError as e:
            print(f"❌ Service error (check internet): {e}\n")
            return None
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
            return None
    
    def speak(self, text):
        """
        ARISU speaks the text out loud
        """
        print("🔊 ARISU is speaking...\n")
        
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"❌ Voice error: {e}")
        
        thread = threading.Thread(target=_speak)
        thread.start()
        thread.join()
    
    def list_available_voices(self):
        """
        Lists all voices on your system
        """
        voices = self.tts_engine.getProperty('voices')
        
        print("\n📢 Available Voices:")
        print("=" * 40)
        for i, voice in enumerate(voices):
            print(f"  [{i}] {voice.name}")
        print("=" * 40 + "\n")
    
    def test_voice(self, text="...This is ARISU. Can you hear me?"):
        """Test TTS"""
        print("🔊 Testing voice...\n")
        self.speak(text)