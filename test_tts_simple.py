import pyttsx3

def test_voices():
    print("Checking for available voices...")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if not voices:
            print("❌ No voices found on this system.")
            return

        print(f"✅ Found {len(voices)} voices:")
        for i, voice in enumerate(voices):
            print(f"  [{i}] ID: {voice.id} | Name: {voice.name}")
        
        # Test speaking with the first available voice
        print(f"\nTesting voice [0]...")
        engine.setProperty('voice', voices[0].id)
        engine.say("Hello. I am checking if you can hear me.")
        engine.runAndWait()
        print("✅ Test command sent. Did you hear anything?")

    except Exception as e:
        print(f"❌ Error during TTS initialization: {e}")

if __name__ == "__main__":
    test_voices()
