from app.data.db import connect_database
from app.services.auth_manager import Authentication
from app.services.database_manager import DatabaseManager
from app.data.incidents import Incident
from app.data.datasets import Dataset
from app.data.it_tickets import Tickets


def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    # 1. Setup database
    manager = DatabaseManager()
    conn = manager.get_connection()
    manager.setup_database_complete()

    # 2. Migrate users
    manager.migrate_users_from_file(conn, filename="users.txt")

    # 3. Test authentication
    print("\n\nTest authentication")
    print("=" * 60)
    user = Authentication.register(username="Matt",
                         raw_password="MattPass123!",
                         role="admin")
    print(f"Registered user: {user.username} with role {user.role}")

    user = Authentication.authenticate(username="Matt", raw_password="MattPass123!")
    if user:
        print(f"Login successful for {user.username} (role={user.role})")
    else:
        print(f"Login failed for {user.username}")

    # 4. Test CRUD
    print("\n\nTest CRUD Operations")
    print("=" * 60)
    incident_id = Incident(severity="High", category="Phishing", status="Open", description="Suspicious email detected").insert_incident()
    print(f"Created incident #{incident_id}")

    Incident.delete_incident(incident_id)
    print(f"Deleted incident #{incident_id}")

    # Update
    Incident.update_incident_status(conn, 1101, "Resolved")
    print(f"Update:  Status updated")

    # 5. Query data
    print("\nTest: Run analytical queries")
    print("=" * 60)
    conn = connect_database()

    df = Incident.get_all_incidents(conn)
    print(f"Total incidents: {len(df)}")

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

