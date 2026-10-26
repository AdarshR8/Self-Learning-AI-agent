import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default_user")

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            print("\n[!] WARNING: OPENAI_API_KEY is not set.")
            print("    Please create a .env file or export OPENAI_API_KEY in your environment.")
            print("    Refer to .env.example for details.\n")
