import os
import requests
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# Two different Helius values:
# -------------------------------
HELIUS_RPC = os.getenv("HELIUS_RPC")          # RPC URL (for getAccountInfo, etc.)
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")  # REST API key (for metadata endpoint)

if not HELIUS_RPC:
    raise ValueError("Missing HELIUS_RPC in .env file")

if not HELIUS_API_KEY:
    raise ValueError("Missing HELIUS_API_KEY in .env file")

# -------------------------------
# Generic RPC caller
# -------------------------------
def helius_rpc(method: str, params):
    """
    Generic helper for calling Helius RPC
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        response = requests.post(HELIUS_RPC, json=payload, timeout=10)
        data = response.json()

        if "error" in data:
            print(f"[Helius RPC Error] {data['error']}")
            return None

        return data.get("result")

    except Exception as e:
        print(f"[Helius Exception] {e}")
        return None
