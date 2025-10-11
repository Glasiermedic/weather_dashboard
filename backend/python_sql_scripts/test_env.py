import os

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("WEATHER_API_KEY")

if api_key:
    print(f"API key loaded : {api_key[:5]}...{api_key[-5:]}")
else:
    print("API key not found")