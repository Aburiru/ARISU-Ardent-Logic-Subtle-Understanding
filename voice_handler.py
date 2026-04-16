# voice_handler.py
import speech_recognition as sr
import edge_tts
import asyncio
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from playsound import playsound
import re

class VoiceHandler:
    def __init__(self, voice="en-US-AnaNeural", rate="+0%", volume="+0%"):
        """
        Initialize high-quality voice with Edge-TTS
        """
        self.voice = voice # AnaNeural is often more expressive
        self.volume = volume
        self.recognizer = sr.Recognizer()
        self.sample_rate = 44100

    def clean_text(self, text):
        """Remove asterisks and text between them (actions/narration)"""
        cleaned = re.sub(r'\*.*?\*', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _get_emotion_settings(self, emotion):
        """Return custom rate and pitch based on detected emotion"""
        rate, pitch = "+0%", "+0Hz"
        if emotion in ['stressed', 'frustrated']:
            rate, pitch = "+15%", "+2Hz"
        elif emotion in ['sad', 'lonely']:
            rate, pitch = "-10%", "-3Hz"
        elif emotion in ['happy', 'excited']:
            rate, pitch = "+10%", "+5Hz"
        elif emotion in ['tired', 'sleepy']:
            rate, pitch = "-15%", "-1Hz"
        return rate, pitch

    def listen(self, duration=5):
        """Record audio and convert to text"""
        try:
            print(f"🎤 Listening for {duration} seconds...")
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()
            temp_filename = "temp_voice_in.wav"
            wav.write(temp_filename, self.sample_rate, recording)
            with sr.AudioFile(temp_filename) as source:
                audio_data = self.recognizer.record(source)
                print("🔍 Processing speech...")
                text = self.recognizer.recognize_google(audio_data)
            if os.path.exists(temp_filename): os.remove(temp_filename)
            print(f"✅ You said: \"{text}\"")
            return text
        except Exception as e:
            print(f"❌ Voice Recognition error: {e}")
            return None

    async def _generate_speech(self, text, output_file, emotion='neutral'):
        speech_text = self.clean_text(text)
        if not speech_text: return False
        rate, pitch = self._get_emotion_settings(emotion)
        communicate = edge_tts.Communicate(speech_text, self.voice, rate=rate, volume=self.volume, pitch=pitch)
        await communicate.save(output_file)
        return True

    def speak(self, text, emotion='neutral'):
        """ARISU speaks using Edge-TTS with emotional variety"""
        print(f"🔊 ARISU is speaking ({emotion})...")
        temp_audio = "temp_arisu_voice.mp3"
        try:
            success = asyncio.run(self._generate_speech(text, temp_audio, emotion))
            if success and os.path.exists(temp_audio):
                playsound(temp_audio)
                if os.path.exists(temp_audio): os.remove(temp_audio)
            else:
                print("🔇 (Only actions detected, skipping voice output)")
        except Exception as e:
            print(f"❌ Voice Output error: {e}")
            print(f"🔊 ARISU (Text only): {text}")
