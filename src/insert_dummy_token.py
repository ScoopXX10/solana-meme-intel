from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

# Load .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

def insert_dummy_token():
    token = {
        "symbol": "DUMMY",
        "name": "Dummy Token",
        "address": "DuMmY1111111111111111111111111111111111111",
        "supply": 123456,
        "volume_24h": 7890,
        "score": 42,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    print("Inserting dummy token...")

    result = supabase.table("tokens").insert(token).execute()

    print("Insert result:")
    print(result)

if __name__ == "__main__":
    insert_dummy_token()
