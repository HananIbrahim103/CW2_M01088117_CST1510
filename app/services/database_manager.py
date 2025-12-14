import sqlite3
from pathlib import Path
import pandas as pd
from app.data.db import DB_PATH, connect_database, DATA_DIR
from app.data.schema import create_all_tables

class DatabaseManager:
    """Service class to Handle SQLite connections and to Manage and setup Database"""
    def __init__(self, db_path: Path | str = DB_PATH, data_dir: Path | None = None):
        self.db_path = Path(db_path)
        self.data_dir = data_dir or DATA_DIR

    @staticmethod
    def get_connection():
        """Return a new database connection."""
        return connect_database()

    def migrate_users_from_file(self, conn, filename="users.txt"):
        """Migrate users from text file into the users table.
        Returns number of users migrated."""

        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            print(" No users to migrate.")
            return

        cursor = conn.cursor()
        migrated_count = 0

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse line: username,password_hash
                parts = line.split(',',2)
                if len(parts) == 3:
                    username = parts[0]
                    role = parts[1]
                    password_hash = parts[2]

                    # Insert user (ignore if already exists)
                    try:
                        cursor.execute("INSERT OR IGNORE INTO users (username, role, password_hash) VALUES (?, ?, ?)",
                                       (username, role, password_hash))
                        if cursor.rowcount > 0:
                            migrated_count += 1
                    except sqlite3.Error as e:
                        print(f"Error migrating user {username}: {e}")

        conn.commit()
        print(f"✅ Migrated {migrated_count} users from {filepath.name}")

        # Verify users were migrated
        conn = connect_database()
        cursor = conn.cursor()

        # Query all users
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()

        print(" Users in database:")
        print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
        print("-" * 35)
        for user in users:
            print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

        print(f"\nTotal users: {len(users)}")

    def load_csv_to_table(self, csv_path, table_name):
        """Load csv to table.
        Returns number of rows inserted, or 0 if file missing"""
        if not Path(csv_path).exists():
            print(f"❌ File not found: {csv_path}")
            return False

        conn = self.get_connection()

        # Read CSV into DataFrame
        df = pd.read_csv(csv_path)
        # if the table exists, append otherwise pandas creates. DataFrame's index will not be added as a separate column
        df.to_sql(table_name, con=conn, if_exists='append', index=False)
        print(f"✅ Loaded {len(df)} rows from {csv_path} into table '{table_name}'.")
        conn.close() # closes the database. Frees resources and ensures no further operations are made using this connection.
        return len(df)

    def load_all_csv_data(self):
        """Load all csv files into table."""
        PATH_DATA = Path("C:/Users/Hanan/OneDrive/Documents/programming/CW2_M01088117_CST1510/DATA")

        csv_table_map = {
            "cyber_incidents.csv": "cyber_incidents",
            "datasets_metadata.csv": "datasets_metadata",
            "it_tickets.csv": "it_tickets"
        }

        for csv_file, table_name in csv_table_map.items():
            csv_path = str(PATH_DATA / csv_file)
            self.load_csv_to_table(csv_path, table_name)

    def setup_database_complete(self):
        """
        Complete database setup:
        1. Connect to database
        2. Create all tables
        3. Migrate users from users.txt
        4. Load CSV data for all domains
        5. Verify setup
        """
        print("\n" + "=" * 60)
        print("STARTING COMPLETE DATABASE SETUP")
        print("=" * 60)

        # Step 1: Connect
        print("\n[1/5] Connecting to database...")
        conn = connect_database()
        print("       Connected")

        # Step 2: Create tables
        print("\n[2/5] Creating database tables...")
        create_all_tables(conn)

        # Step 3: Migrate users
        print("\n[3/5] Migrating users from users.txt...")
        user_count = self.migrate_users_from_file(conn)
        print(f"       Migrated {user_count} users")

        # Step 4: Load CSV data
        print("\n[4/5] Loading CSV data...")
        self.load_all_csv_data()

        # Step 5: Verify
        print("\n[5/5] Verifying database setup...")
        cursor = conn.cursor()

        # Count rows in each table
        tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
        print("\n Database Summary:")
        print(f"{'Table':<25} {'Row Count':<15}")
        print("-" * 40)

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<25} {count:<15}")

        conn.close()

        print("\n" + "=" * 60)
        print(" DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print(f"\n Database location: {DB_PATH.resolve()}")
