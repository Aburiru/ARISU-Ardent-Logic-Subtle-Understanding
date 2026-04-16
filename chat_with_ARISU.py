# chat_with_ARISU.py - CLI Interface for ARISU
import sys
import time
import random
from colorama import Fore, Style, init

# Import shared modules
from chatbot import Chatbot
from ai_brain import AIBrain
from emotion_detector import EmotionDetector
from config import ARISU_SYSTEM_PROMPT
from voice_handler import VoiceHandler

# Initialize colorama
init(autoreset=True)

# Initialize ARISU components
arisu = Chatbot("ARISU", ARISU_SYSTEM_PROMPT)
brain = AIBrain()
detector = EmotionDetector()
vh = VoiceHandler()

voice_enabled = False

def get_greeting():
    """Returns a time-based greeting from ARISU's tsundere repertoire."""
    import datetime
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return random.choice([
            "...Morning. You're up early. Don't tell me you stayed up all night again.",
            "Hmph. Morning. Did you at least sleep well?",
            "...You're awake. I was starting to think you'd sleep through the day."
        ])
    elif 12 <= hour < 17:
        return random.choice([
            "...Afternoon. What took you so long to talk to me?",
            "Finally decided to show up? What do you need?",
            "...It's the afternoon. Have you eaten? Don't skip meals."
        ])
    elif 17 <= hour < 21:
        return random.choice([
            "...Evening. Long day? You look tired... not that I care or anything.",
            "You're here late. Something on your mind?",
            "Evening... Don't stay up too late tonight, okay? It's just logical rest."
        ])
    else:
        return random.choice([
            "...Why are you still awake? It's late.",
            "Hmph. Can't sleep? ...Fine. I'll keep you company for a bit.",
            "It's past midnight. Don't blame me if you're tired tomorrow."
        ])

def show_typing_indicator(duration=1.5):
    """Animated 'thinking' indicator for CLI realism."""
    print(f"{Fore.CYAN}ARISU is thinking", end="", flush=True)
    start_time = time.time()
    dots = 0
    while time.time() - start_time < duration:
        dots = (dots + 1) % 4
        print(f"\r{Fore.CYAN}ARISU is thinking" + "." * dots + "   ", end="", flush=True)
        time.sleep(0.3)
    print("\r" + " " * 30 + "\r", end="", flush=True)

def chat_step(user_message):
    """Single chat interaction logic."""
    # Detect emotion
    emotion, intensity, _ = detector.detect_emotion(user_message)
    
    # Optional debug for emotion
    if emotion != 'neutral':
        print(f"{Fore.YELLOW}[Detected: {emotion} (intensity: {intensity})]{Style.RESET_ALL}")
    
    # Add to history
    arisu.add_message("user", user_message)
    
    # Prepare context
    emotion_hint = None
    if emotion != 'neutral' and intensity > 0:
        emotion_hint = f"[User seems {emotion} (intensity: {intensity}). Respond accordingly.]"
    
    context = arisu.get_full_context(emotion_hint=emotion_hint)
    response = brain.chat(context)
    
    # Add AI response to history
    arisu.add_message("assistant", response)
    return response, emotion

def show_stats():
    """Display session stats with personality."""
    stats = detector.get_stats()
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"           CONVERSATION STATISTICS")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"Messages: {stats['message_count']}")
    print(f"Duration: {stats['duration']}")
    print(f"Trend:    {stats['emotion_trend']}")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}ARISU: ...You've been bothering me for {stats['duration']}. ")
    print(f"       Don't you have better things to do?{Style.RESET_ALL}\n")

def main():
    global voice_enabled
    print("=" * 70)
    print("           ARISU - Ardent Logic & Subtle Understanding")
    print("=" * 70)
    print("\nCommands: 'quit', 'exit', 'clear', 'stats', 'voice on/off', 'listen'")
    print("=" * 70)
    
    greeting = get_greeting()
    print(f"\n{Fore.CYAN}ARISU: {greeting}{Style.RESET_ALL}\n")
    
    while True:
        try:
            user_input = input(f"{Fore.YELLOW}You: {Style.RESET_ALL}").strip()
            
            # Handle voice triggers
            if user_input.lower() == 'listen':
                voice_input = vh.listen(duration=7)
                if voice_input:
                    user_input = voice_input
                    print(f"{Fore.YELLOW}You (Voice): {Style.RESET_ALL}{user_input}")
                else:
                    print(f"{Fore.RED}ARISU: ...I couldn't hear you clearly.{Style.RESET_ALL}")
                    continue

            if not user_input: continue
            
            cmd = user_input.lower()
            if cmd in ['quit', 'exit', 'cya']:
                farewell = "...Hmph. Going already? Fine. Don't overwork yourself."
                print(f"\n{Fore.CYAN}ARISU: {farewell}{Style.RESET_ALL}")
                if voice_enabled: vh.speak(farewell)
                break
            elif cmd == 'clear':
                arisu.clear_history()
                print(f"{Fore.CYAN}\nARISU: ...Fine. Fresh start. What do you need?\n")
                continue
            elif cmd == 'stats':
                show_stats()
                continue
            elif cmd == 'voice on':
                voice_enabled = True
                msg = "...Fine. I'll talk to you now. Satisfied?"
                print(f"{Fore.CYAN}\nARISU: {msg}\n")
                vh.speak(msg)
                continue
            elif cmd == 'voice off':
                voice_enabled = False
                print(f"{Fore.CYAN}\nARISU: ...Quiet time it is then.\n")
                continue
            
            # Normal chat
            show_typing_indicator(duration=1.5)
            response, emotion = chat_step(user_input)
            print(f"\n{Fore.CYAN}ARISU: {response}{Style.RESET_ALL}\n")
            
            if voice_enabled:
                vh.speak(response, emotion=emotion)
            
        except KeyboardInterrupt:
            print("\n\nARISU: ...Leaving already? Take care.")
            break

if __name__ == "__main__":
    main()