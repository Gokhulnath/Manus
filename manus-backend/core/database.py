import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def get_supabase_client() -> Client:
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))