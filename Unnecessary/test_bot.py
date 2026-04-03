# test_bot.py

from chatbot import Chatbot

# Create a bot named "Buddy"
my_bot = Chatbot("Buddy")

# Make it remember something
my_bot.remember("Hello! I'm learning to code.")
my_bot.remember("This is exciting!")

# Ask it what it remembers
print(f"{my_bot.name} remembers: {my_bot.recall_last()}")
print(f"All memories: {my_bot.memory}")

# ## **What happens when you run this:**

# 1. Line 5: Creates a NEW chatbot using our blueprint
# 2. `my_bot` is now a chatbot object with name "Buddy" and empty memory
# 3. Lines 8-9: Adds two messages to its memory list
# 4. Line 12: Prints the LAST thing it remembered
# 5. Line 13: Prints the ENTIRE memory list

# **Output:**

# Buddy remembers: This is exciting!
# All memories: ['Hello! I'm learning to code.', 'This is exciting!']

