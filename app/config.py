import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_PORT = int(os.getenv("PORT") or os.getenv("APP_PORT", 5000))
    BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_TOKEN = os.getenv("LLM_TOKEN", "")
    SQLALCHEMY_DATABASE_URI = "sqlite:///db/data.db"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "samosir-dev-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_TOKEN_EXPIRE_HOURS", 24)) * 3600