# mood_example.py

from chatbot import Chatbot

bot = Chatbot(
    name="ARISU",
    personality="Moody artist who swings between excited and melancholic",
    backstory="Struggling painter trying to find her style"
)

# At the start
print(bot.mood)  # "curious"

# After user shares something sad
bot.update_mood("empathetic and gentle")
print(f"ARISU is now feeling: {bot.mood}")

# After user shares good news
bot.update_mood("excited and energetic!!")
print(f"ARISU is now feeling: {bot.mood}")

# The system prompt will reflect the current mood!
print(bot.get_system_prompt())
