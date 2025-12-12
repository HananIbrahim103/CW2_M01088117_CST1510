from app.data.db import connect_database, DATA_DIR
from app.data.schema import create_users_table, create_cyber_incidents_table, create_datasets_metadata_table, create_it_tickets_table
from app.services.user_service import migrate_users_from_file
from app.data.users import User
from app.data.incidents import Incident
from app.data.datasets import Dataset
from app.data.it_tickets import Tickets


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
    user = User.register(username="Matt",
                         raw_password="MattPass123!",
                         role="admin")
    print(f"Registered user: {user.username} with role {user.role}")

    user = User.authenticate(username="Matt", raw_password="MattPass123!")
    if user:
        print(f"Login successful for {user.username} (role={user.role})")
    else:
        print(f"Login failed for {user.username}")

    # 4. Test CRUD
    incident_id = Incident(severity="High", category="Phishing", status="Open", description="Suspicious email detected").insert_incident()
    print(f"Created incident #{incident_id}")

    incident_id = Incident.delete_incident(1000)
    print(f"Deleted incident #{incident_id}")

    # 5. Query data
    df = Incident.get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")

    print("\nTest: Run analytical queries")
    conn = connect_database()

    print("\n Incidents by Type:")
    df_by_type = Incident.get_incidents_by_type_count(conn)
    print(df_by_type)

    print("\n High Severity Incidents by Status:")
    df_high_severity = Incident.get_high_severity_by_status(conn)
    print(df_high_severity)

    print("\n Incident Types with Many Cases (>5):")
    df_many_cases = Incident.get_incident_types_with_many_cases(conn, min_count=5)
    print(df_many_cases)

    print("\n Number of Datasets uploaded by each role")
    df_many_cases = Dataset.count_datasets_grouped_by_uploaded_by(conn)
    print(df_many_cases)

    print("\n High Priority Tickets by Status:")
    df_many_cases = Tickets.get_high_priority_by_status(conn)
    print(df_many_cases)

if __name__ == "__main__":
    main()

