import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  
    OPENROUTER_URL = os.getenv("OPENROUTER_URL")
    OPENROUTER_META_LLAMA_MODEL = os.getenv("OPENROUTER_META_LLAMA_MODEL")
    OPENROUTER_DEEPSEEK_MODEL = os.getenv("OPENROUTER_DEEPSEEK_MODEL")
    OPENROUTER_MISTRAL_MODEL = os.getenv("OPENROUTER_MISTRAL_MODEL")
    GEO_KEY = os.getenv("GEO_KEY")
    GEO_CODE_URL = os.getenv("GEO_CODE_URL")
    GEO_CATEGORIES = os.getenv("GEO_CATEGORIES")
    GEO_CONDITIONS = os.getenv("GEO_CONDITIONS")
    GEO_PLACES_URL = os.getenv("GEO_PLACES_URL")