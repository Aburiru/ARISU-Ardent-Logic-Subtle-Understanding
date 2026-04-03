# test_api_key.py

import requests

API_KEY = "[ENCRYPTION_KEY]"  

headers = {"Authorization": f"Bearer {API_KEY}"}

# Test if key works
response = requests.get(
    "https://huggingface.co/api/whoami-v2",
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    print("\n✅ API key is VALID!")
else:
    print("\n❌ API key has a problem!")