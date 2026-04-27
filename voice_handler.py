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
import logging
from config import (
    DEFAULT_VOICE, VOICE_RATE, VOICE_VOLUME,
    RVC_ENABLED, RVC_MODEL_PATH, RVC_INDEX_PATH, RVC_PITCH, RVC_DEVICE
)

# Setup logging
logger = logging.getLogger("ARISU_Voice")

class VoiceHandler:
    def __init__(self, voice=DEFAULT_VOICE, rate=VOICE_RATE, volume=VOICE_VOLUME):
        """
        Initialize high-quality voice with Edge-TTS and optional RVC conversion
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.recognizer = sr.Recognizer()
        self.sample_rate = 44100
        
        # Initialize RVC if enabled or if model exists for later use
        self.rvc_inference = None
        self.rvc_active = RVC_ENABLED
        
        # We no longer load the model immediately to save RAM at startup.
        # Loading will happen in rvc_convert if active.
        if self.rvc_active:
            logger.info("RVC is enabled in config but will be lazy-loaded on first use.")

    def _load_rvc(self):
        """Lazy load RVC models and torch to save RAM"""
        if self.rvc_inference is not None:
            return True
            
        if not os.path.exists(RVC_MODEL_PATH):
            logger.warning(f"RVC Model not found at {RVC_MODEL_PATH}. Disabling RVC.")
            self.rvc_active = False
            return False

        try:
            logger.info("📦 Loading RVC/Torch dependencies (this may take a moment)...")
            import torch
            from rvc_python.infer import RVCInference
            
            self.rvc_inference = RVCInference(device=RVC_DEVICE)
            idx_p = RVC_INDEX_PATH if os.path.exists(RVC_INDEX_PATH) else ""
            self.rvc_inference.load_model(RVC_MODEL_PATH, index_path=idx_p)

            try:
                from config import RVC_METHOD
                method = RVC_METHOD
            except ImportError:
                method = "pm"

            self.rvc_inference.f0method = method
            self.rvc_inference.f0up_key = RVC_PITCH
            logger.info(f"✅ RVC Model loaded successfully using {method}.")
            return True
        except ImportError:
            logger.error("rvc-python or torch not installed. Disabling RVC.")
            self.rvc_active = False
            return False
        except Exception as e:
            logger.error(f"Failed to initialize RVC: {e}")
            self.rvc_active = False
            return False

    def clean_text(self, text):
        """Remove asterisks and text between them (actions/narration)"""
        # Remove asterisks and content between them (*sigh*)
        cleaned = re.sub(r'\*.*?\*', '', text)
        # Remove common kaomoji that might sound weird
        cleaned = re.sub(r'\([^\)]+\)', '', cleaned)
        # Clean extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _get_emotion_settings(self, emotion):
        """Return custom rate and pitch based on detected emotion"""
        rate, pitch = self.rate, "+0Hz"
        if emotion in ['stressed', 'frustrated', 'angry']:
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
            logger.info(f"🎤 Listening for {duration} seconds...")
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()
            temp_filename = "temp_voice_in.wav"
            wav.write(temp_filename, self.sample_rate, recording)
            
            with sr.AudioFile(temp_filename) as source:
                audio_data = self.recognizer.record(source)
                logger.info("🔍 Processing speech...")
                text = self.recognizer.recognize_google(audio_data)
            
            if os.path.exists(temp_filename): 
                os.remove(temp_filename)
            
            logger.info(f"✅ You said: \"{text}\"")
            return text
        except Exception as e:
            logger.error(f"Voice Recognition error: {e}")
            return None

    async def _generate_speech(self, text, output_file, emotion='neutral'):
        speech_text = self.clean_text(text)
        if not speech_text: 
            return False
            
        rate, pitch = self._get_emotion_settings(emotion)
        logger.debug(f"Generating TTS: rate={rate}, pitch={pitch}, text='{speech_text}'")
        
        communicate = edge_tts.Communicate(speech_text, self.voice, rate=rate, volume=self.volume, pitch=pitch)
        await communicate.save(output_file)
        return True

    def _safe_delete(self, file_path, retries=3):
        """Try to delete a file multiple times to handle Windows locks"""
        if not os.path.exists(file_path):
            return
        
        for i in range(retries):
            try:
                # Small sleep to let the OS release any lock (playsound is slow)
                time.sleep(0.5)
                os.remove(file_path)
                logger.debug(f"Deleted temp file: {file_path}")
                return
            except Exception as e:
                if i == retries - 1:
                    logger.warning(f"Could not delete {file_path}: {e}")
                else:
                    time.sleep(0.5)

    def rvc_convert(self, input_path):
        """Convert voice using RVC model with lazy loading and memory cleanup"""
        if not self.rvc_active:
            return input_path
            
        # Lazy load if not already loaded
        if not self._load_rvc():
            return input_path
            
        logger.info("🎭 Converting voice with RVC...")
        base_name = os.path.splitext(input_path)[0].replace("_rvc", "")
        output_path = f"{base_name}_rvc.wav"
        
        try:
            model_info = self.rvc_inference.models[self.rvc_inference.current_model]
            file_index = model_info.get("index", "")
            
            result = self.rvc_inference.vc.vc_single(
                sid=0,
                input_audio_path=input_path,
                f0_up_key=RVC_PITCH,
                f0_file=None,
                f0_method=self.rvc_inference.f0method,
                file_index=file_index,
                file_index2="",
                index_rate=self.rvc_inference.index_rate,
                filter_radius=self.rvc_inference.filter_radius,
                resample_sr=self.rvc_inference.resample_sr,
                rms_mix_rate=self.rvc_inference.rms_mix_rate,
                protect=self.rvc_inference.protect
            )
            
            if isinstance(result, tuple):
                audio_data = result[0]
            else:
                audio_data = result

            import scipy.io.wavfile as wavfile
            wavfile.write(output_path, self.rvc_inference.vc.tgt_sr, audio_data)
            
            # Clean up input immediately after conversion
            self._safe_delete(input_path)
            
            # Memory Cleanup
            try:
                import torch
                import gc
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
            except:
                pass
                
            return output_path
            
        except Exception as e:
            logger.error(f"❌ RVC conversion failed: {e}")
            return input_path

    def speak(self, text, emotion='neutral'):
        """ARISU speaks using Edge-TTS and RVC (if enabled)"""
        logger.info(f"🔊 ARISU is speaking ({emotion})...")
        
        timestamp = int(time.time())
        temp_audio = f"temp_arisu_{timestamp}.mp3"
        final_audio = None
        
        try:
            success = asyncio.run(self._generate_speech(text, temp_audio, emotion))
            if success and os.path.exists(temp_audio):
                # Apply RVC if enabled
                final_audio = self.rvc_convert(temp_audio)
                
                # Double check the file exists and has content before playing
                if os.path.exists(final_audio) and os.path.getsize(final_audio) > 0:
                    playsound(final_audio)
                else:
                    logger.warning("Audio file is empty or missing, skipping playback.")
            else:
                logger.info("🔇 (Only actions detected, skipping voice output)")
        except Exception as e:
            logger.error(f"Voice Output error: {e}")
            print(f"🔊 ARISU (Text only): {text}")
        finally:
            # ALWAYS clean up both files
            if temp_audio: self._safe_delete(temp_audio)
            if final_audio and final_audio != temp_audio: self._safe_delete(final_audio)
