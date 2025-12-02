from utils.supabase_client import supabase

data = supabase.table("tokens").select("*").execute()
print("RESULT:", data)
