# test_conversation.py

from ARISU import ARISU

# Simulate a conversation
ARISU.add_message("user", "Hey ARISU, I'm stuck on this code problem.")
ARISU.add_message("assistant", "...What's the problem? Don't just sit there frustrated.")

ARISU.add_message("user", "I don't understand how loops work.")
ARISU.add_message("assistant", "Hmph. It's simple. A loop repeats actions until a condition is met. I'll explain step by step.")

# See the full context
print("=== FULL CONTEXT ===")
context = ARISU.get_full_context()

for msg in context:
    print(f"\n[{msg['role'].upper()}]")
    print(msg['content'])
    print("-" * 50)
# '''

# **Output will show:**
# '''

# [SYSTEM]
# You are ARISU (Logical Unified Neural Assistant)...
# --------------------------------------------------

# [USER]
# Hey ARISU, I'm stuck on this code problem.
# --------------------------------------------------

# [ASSISTANT]
# ...What's the problem? Don't just sit there frustrated.
# --------------------------------------------------