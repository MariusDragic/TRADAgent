from dotenv import load_dotenv
import os

load_dotenv()

from pydantic import SecretStr
import os

MISTRAL_API_KEY = (
    SecretStr(os.environ["MISTRAL_API_KEY"])
    if "MISTRAL_API_KEY" in os.environ
    else None
)


if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is not set in the environment variables .env")

FINNHUB_API_KEY = (
    SecretStr(os.environ["FINNHUB_API_KEY"])
    if "FINNHUB_API_KEY" in os.environ
    else None
)

if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY is not set in the environment variables (.env)")