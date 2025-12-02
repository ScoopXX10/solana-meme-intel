from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

client = create_client(url, key)

print("Testing connection + tokens table...")

try:
    data = client.table("tokens").select("*").execute()
    print("SUCCESS — Tokens table response:")
    print(data)
except Exception as e:
    print("ERROR:")
    print(e)

