import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load from .env if present (local dev only)
load_dotenv()


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "")
    admin_token: str = os.getenv("ADMIN_TOKEN", "")
    refresh_hours: int = int(os.getenv("REFRESH_HOURS", "8"))

    # Optional API keys (all FREE)
    alphavantage_api_key: str = os.getenv("ALPHAVANTAGE_API_KEY", "")
    fred_api_key: str = os.getenv("FRED_API_KEY", "")
    eia_api_key: str = os.getenv("EIA_API_KEY", "")
    usda_api_key: str = os.getenv("USDA_API_KEY", "")
    cftc_api_key: str = os.getenv("CFTC_API_KEY", "")

    # Additional free API keys for comprehensive data
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")


settings = Settings()
