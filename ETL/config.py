
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCRAPING_DATA = PROJECT_ROOT / "Scraping" / "data"

ETL_DATA = Path(__file__).resolve().parent / "data"

BRONZE_DATA = ETL_DATA / "bronze"
SILVER_DATA = ETL_DATA / "silver"
GOLD_DATA = ETL_DATA / "gold"

JOBSPY_FILE = SCRAPING_DATA / "jobspy_jobs.json"
REMOTIVE_FILE = SCRAPING_DATA / "remotive_jobs.json"
