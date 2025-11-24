import sqlite3
from pathlib import Path

DATA_DIR = Path("C:/Users/Hanan/OneDrive/Documents/programming/CW2_M01088117_CST1510/DATA")

DB_PATH = DATA_DIR / "intelligence_platform.db"
# Create DATA folder if it doesn't exist
Path("C:/Users/Hanan/OneDrive/Documents/programming/CW2_M01088117_CST1510/DATA").mkdir(parents=False, exist_ok=True)

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))

