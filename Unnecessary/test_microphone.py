# test_microphone.py

from voice_assistant import VoiceAssistant

print("="*60)
print("     TESTING YOUR MICROPHONE")
print("="*60 + "\n")

va = VoiceAssistant()

print("When you see '🎤 Listening...', say something like:")
print("  - 'Hello ARISU'")
print("  - 'Testing one two three'")
print("  - Any sentence you want\n")

input("Press ENTER when ready to speak...")

# Listen for speech
text = va.listen(timeout=10)

if text:
    print(f"\n✅ SUCCESS! I heard: \"{text}\"")
    print("\nNow ARISU will repeat what you said:\n")
    va.speak(f"You said: {text}")
else:
    print("\n❌ Microphone test failed.")
    print("Troubleshooting:")
    print("  1. Check if your microphone is plugged in")
    print("  2. Check Windows sound settings")
    print("  3. Make sure you have internet (uses Google API)")
    print("  4. Try speaking louder and clearer")