import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_PROJECT_REF = "ynlxnxhxrdjcmxpalitn"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "recent_announcements_2"

WS_URL = f"wss://{SUPABASE_PROJECT_REF}.supabase.co/realtime/v1/websocket?apikey={SUPABASE_ANON_KEY}&vsn=1.0.0"
