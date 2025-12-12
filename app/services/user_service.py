import sqlite3
import bcrypt
from pathlib import Path
from app.data import users
from app.data.db import connect_database, DATA_DIR
from app.data.schema import create_users_table, create_cyber_incidents_table, create_datasets_metadata_table, create_it_tickets_table


'''def register_user(username, password, role='user'):
    """Register new user in the database."""
    conn = connect_database()
    cursor = conn.cursor()

    # check if user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Insert into database
    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully."


def login_user(username, password):
    """Authenticate user against the database"""
    # Find user
    user = get_user_by_username(username)
    if not user:
        return False, "Username not found."

    # Verify password
    stored_hash = user[3]  # password_hash column
    #compares as bytes
    #internally extracts the salt from the hash, re-hashes the plain password, and checks for a match.
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."'''

def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    """Migrate users from text file to database."""
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