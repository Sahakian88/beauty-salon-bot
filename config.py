import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_PORT = int(os.getenv("API_PORT", "8000"))
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID", "").strip() else None
MINI_APP_URL = os.getenv("MINI_APP_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in the .env file")
