# test_voice.py

from voice_assistant import VoiceAssistant

print("="*60)
print("     TESTING ARISU'S VOICE SYSTEM")
print("="*60 + "\n")

# Create voice assistant
va = VoiceAssistant(voice_id=1)

# Show available voices
print("Let's see what voices are available:\n")
va.list_available_voices()

# Test the current voice
print("\n" + "="*60)
print("Testing ARISU's voice - you should HEAR her speak:")
print("="*60 + "\n")

va.test_voice("...This is ARISU speaking. Can you hear me?")

print("\n✅ If you heard ARISU speak, the voice system works!")
print("📝 Note which voice number sounded best from the list above.\n")