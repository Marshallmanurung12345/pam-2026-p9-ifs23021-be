import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = int(os.getenv("PORT") or os.getenv("APP_PORT", 5000))
    BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip().rstrip("/")
    LLM_TOKEN = os.getenv("GEMINI_API_KEY", os.getenv("LLM_TOKEN", "")).strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/data.db"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "samosir-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_TOKEN_EXPIRE_HOURS", 24)) * 3600
