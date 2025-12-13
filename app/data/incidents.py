import pandas as pd
from app.services.database_manager import DatabaseManager


class Incident:
    """ Contains all incident-related data.
    This class handles retrieving incidents, and performing CRUD operations on the cyber_indidents database."""
    def __init__(self, severity, category, status, description, incident_id:int | None = None):
        self.incident_id = incident_id
        self.severity = severity
        self.category = category
        self.status = status
        self.description = description

    # CRUD Operations---------------------------------------------------------------------------------------------

    @staticmethod
    def get_all_incidents(conn):
        """Returns all incidents as a DataFrame."""
        df = pd.read_sql_query(
            "SELECT * FROM cyber_incidents ORDER BY incident_id DESC",
            conn
        )
        return df

    def insert_incident(self) -> int:
        """Insert new incident row
        Returns:
            ID of the inserted incident"""

        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cyber_incidents 
            (severity, category, status, description)
            VALUES (?, ?, ?, ?)
        """, (self.severity, self.category, self.status, self.description))
        conn.commit()
        incident_id = cursor.lastrowid #returns the row ID of the last inserted row (used after INSERT)
        return incident_id

    @staticmethod
    def update_incident_status(conn, incident_id: int, new_status: str) -> int:
        """Update existing incident status.
        Args:
            conn (sqlite3.Connection): Database connection
            incident_id: ID of the incident to update
            new_status: New status
        Returns:
            Number of rows updated"""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
            (new_status, incident_id)
        )
        conn.commit()
        return cursor.rowcount
        # After you run an UPDATE, DELETE, or INSERT statement: cursor.rowcount tells you how many rows were changed

    @staticmethod
    def delete_incident(incident_id) -> int:
        """Delete an incident.
        Args:
            incident_id: ID of the incident to delete
        Returns:
            Number of rows deleted"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM cyber_incidents WHERE incident_id = ?",
            (incident_id,)
        )
        conn.commit()
        return cursor.rowcount

    # Analytical queries--------------------------------------------------------------------------

    @staticmethod
    def get_incidents_by_type_count(conn):
        """Counts number of incidents in each category
        Returns:
            Dataframe of the query"""
        query = """
        SELECT category, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY category
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

    @staticmethod
    def get_daily_phishing_counts(conn):
        """Counts number of phishing attacks each day
        Returns:
            Dataframe of the query"""
        query = """
        SELECT DATE(timestamp) AS date, COUNT(*) AS count
        FROM cyber_incidents
        WHERE category = 'Phishing'
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
        """
        df = pd.read_sql_query(query, conn)
        return df

    @staticmethod
    def compute_incident_metrics(conn):
        """Calculates key incident summary metrics.
        Reads severity, status and category columns from the database.
        Derives a collection of counts
        Returns:
            A tuple containing the calculated values
            """
        df = pd.read_sql_query("SELECT severity, status, category FROM cyber_incidents", conn)

        total = len(df)
        open_count = (df["status"] != "Closed").sum()
        critical = (df["severity"] == "Critical").sum()
        phishing = (df["category"] == "Phishing").sum()
        return total, open_count, critical, phishing

    @staticmethod
    def get_high_severity_by_status(conn):
        """Count high severity incidents by status.
        Returns:
            A dataframe of the query"""
        query = """
        SELECT status, COUNT(*) as count
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

    @staticmethod
    def get_incident_types_with_many_cases(conn, min_count=5):
        """Find incident types with more than min_count cases.
        Returns:
            Dataframe of the query"""
        query = """
        SELECT category, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY category
        HAVING COUNT(*) > ?
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn, params=(min_count,))
        return df
        # "?" is a parameter placeholder

