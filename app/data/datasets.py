from pathlib import Path
import pandas as pd
from app.data.incidents import connect_database

def load_csv_to_table(csv_path, table_name):
    """Load csv to table."""
    conn = connect_database()
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=conn, if_exists='append', index=False)
    print(f"✅ Loaded {len(df)} rows from {csv_path} into table '{table_name}'.")
    conn.close()
    return len(df)

PATH_DATA = Path("C:/Users/Hanan/OneDrive/Documents/programming/CW2_M01088117_CST1510/DATA")
csv_path = str(PATH_DATA / "cyber_incidents.csv")
load_csv_to_table(csv_path, "cyber_incidents")

