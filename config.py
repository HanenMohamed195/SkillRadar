
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "skillradar.db"

API_URL = "https://remotive.com/api/remote-jobs"

SAMPLE_LIMIT = 20
