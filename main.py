from app.data.db import connect_database, DATA_DIR
from app.data.schema import create_users_table, create_cyber_incidents_table, create_datasets_metadata_table, create_it_tickets_table
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents, delete_incident, update_incident_status, \
    get_incidents_by_type_count, get_high_severity_by_status
import pandas as pd


def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)

    # 1. Setup database
    conn = connect_database()
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)

    # 2. Migrate users
    migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt")

    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)

    success, msg = login_user("alice", "SecurePass123!")
    print(msg)

    # 4. Test CRUD
    incident_id = insert_incident("2024-11-05", "Phishing", "High", "Open", "Suspicious email detected", "test_user")
    print(f"Created incident #{incident_id}")

    # 5. Query data
    df = get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")


if __name__ == "__main__":
    main()

