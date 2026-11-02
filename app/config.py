import os
from pathlib import Path
from dotenv import load_dotenv

# Φόρτωση .env αρχείου
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    MAX_RESULTS_PER_SOURCE: int = int(os.getenv("MAX_RESULTS_PER_SOURCE", "30"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 PriceWatcher/1.0"
    )

    ENABLE_INSOMNIA: bool = os.getenv("ENABLE_INSOMNIA", "true").lower() in ("true", "1", "yes")
    ENABLE_VENDORA: bool = os.getenv("ENABLE_VENDORA", "true").lower() in ("true", "1", "yes")
    ENABLE_ZER: bool = os.getenv("ENABLE_ZER", "true").lower() in ("true", "1", "yes")
    ENABLE_EBYTE: bool = os.getenv("ENABLE_EBYTE", "true").lower() in ("true", "1", "yes")
    ENABLE_PCARENA: bool = os.getenv("ENABLE_PCARENA", "true").lower() in ("true", "1", "yes")
    ENABLE_FACEBOOK_DIRECT: bool = os.getenv("ENABLE_FACEBOOK_DIRECT", "true").lower() in ("true", "1", "yes")

settings = Settings()
