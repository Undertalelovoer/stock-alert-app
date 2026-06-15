import os
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

DATA_DIR = "data"
COMPANIES_FILE = f"{DATA_DIR}/companies.json"
WATCHLIST_FILE = f"{DATA_DIR}/watchlist.json"
LAST_NOTIFIED_FILE = f"{DATA_DIR}/last_notified.json"
LINE_USERS_FILE = f"{DATA_DIR}/line_users.json"