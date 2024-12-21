import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_PROJECT_REF = "ynlxnxhxrdjcmxpalitn"
SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_URL = "https://ynlxnxhxrdjcmxpalitn.supabase.co"
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")
# SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlubHhueGh4cmRqY214cGFsaXRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkzNDkxMDIsImV4cCI6MjA0NDkyNTEwMn0.KXqCRYfFgMWME7QZoNOkSKr4aMLFGHx_XU9ev5R3NPM"
TABLE_NAME = "recent_announcements_2"

WS_URL = f"wss://{SUPABASE_PROJECT_REF}.supabase.co/realtime/v1/websocket?apikey={SUPABASE_ANON_KEY}&vsn=1.0.0"
