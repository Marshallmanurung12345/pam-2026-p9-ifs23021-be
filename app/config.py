import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = int(os.getenv("APP_PORT", 5000))
    BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_TOKEN = os.getenv("LLM_TOKEN", "")
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
