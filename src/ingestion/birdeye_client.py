import requests
import os
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

# Load key from environment
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

if not BIRDEYE_API_KEY:
    raise ValueError("Missing BIRDEYE_API_KEY in .env")

# Correct NEW base API URL
BIRDEYE_BASE_URL = "https://api.birdeye.so"

# Headers now including API key
HEADERS = {
    "accept": "application/json",
    "x-api-key": BIRDEYE_API_KEY,
    "x-chain": "solana"
}

def get_token_price(address: str):
    """
    Fetch token price using BDS authenticated price endpoint.
    """

    url = f"{BIRDEYE_BASE_URL}/defi/price?address={address}"

    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        print("Birdeye API Error:", response.text)
        return None

    data = response.json().get("data", {})

    return {
        "price": data.get("value"),
        "liquidity": data.get("liquidity"),
        "change_24h": data.get("priceChange24h"),
        "updated": data.get("updateHumanTime")
    }

