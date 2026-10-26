import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "adarsh")

    @classmethod
    def get_active_provider(cls) -> str:
        if cls.GEMINI_API_KEY:
            return "gemini"
        elif cls.OPENAI_API_KEY:
            return "openai"
        return "none"

    @classmethod
    def validate(cls):
        provider = cls.get_active_provider()
        if provider == "none":
            print("\n[!] WARNING: No API key found.")
            print("    Please set GEMINI_API_KEY in your .env file.")
            print("    You can get a free key at: https://aistudio.google.com/app/apikey\n")
