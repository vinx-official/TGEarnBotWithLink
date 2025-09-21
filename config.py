import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

# MongoDB Connection URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set.")

# GP Links API Key
GPLINKS_API_KEY = os.getenv("GPLINKS_API_KEY")
if not GPLINKS_API_KEY:
    raise ValueError("GPLINKS_API_KEY environment variable not set.")

# Admin User IDs (Telegram user IDs)
# These should be integers, separated by commas if multiple. E.g., "123456789,987654321"
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(',') if x.strip().isdigit()]

if not ADMIN_IDS:
    print("WARNING: No ADMIN_IDS found in environment variables. Admin commands will not work.")
