import pandas as pd
from app.data.db import connect_database

class Tickets:
    """ Contains all IT_ticket-related data.
        This class handles retrieving tickets, and performing CRUD operations on the it_tickets database."""
    def __init__(self, priority, description, status, assigned_to, resolution_time_hours, ticket_id:int | None = None):
        self.ticket_id = ticket_id
        self.priority = priority
        self.description = description
        self.status = status
        self.assigned_to = assigned_to
        self.resolution_time_hours = resolution_time_hours

    @staticmethod
    def get_all_tickets(conn):
        """Get all tickets as DataFrame."""
        df = pd.read_sql_query(
            "SELECT * FROM it_tickets ORDER BY ticket_id DESC",
            conn
        )
        #conn.close()
        return df

    # CRUD Operations---------------------------------------------------------------------------------------------------

    def insert_ticket(self) -> int:
        """Insert new ticket to the database.
        Returns:
            ID of the ticket that was inserted to the database"""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO it_tickets 
            (priority, description, status, assigned_to, resolution_time_hours)
            VALUES (?, ?, ?, ?, ?)
        """, (self.priority, self.description, self.status, self.assigned_to, self.resolution_time_hours))
        conn.commit()
        ticket_id = cursor.lastrowid #returns the row ID of the last inserted row (used after INSERT)
        conn.close()
        return ticket_id

    @staticmethod
    def update_ticket_status(conn, ticket_id: int, new_status: str) -> int:
        """Update an existing ticket status.
        Args:
            ticket_id (int): ID of ticket to be updated.
            new_status (str): New status of the ticket.
            conn (sqlite3.Connection): Database connection.
        Returns:
            Number of rows updated."""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    @staticmethod
    def delete_ticket(conn, ticket_id):
        """Delete incident.
        Args:
            conn (sqlite3.Connection): Database connection.
            ticket_id (int): ID of ticket to be deleted.
        Returns:
            Number of rows deleted."""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM it_tickets WHERE ticket_id = ?",
            (ticket_id,)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    # Analytical Queries----------------------------------------------------------------------------------------------------

    @staticmethod
    def get_high_priority_by_status(conn):
        """Count high priority tickets in each status category."""
        query = """
        SELECT status, COUNT(*) as count
        FROM it_tickets
        WHERE priority = 'High'
        GROUP BY status
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

    @staticmethod
    def get_ticket_perf_by_staff(conn):
        """Collects all tickets in the table with resolved status
        and computes for each assignee, the average
        resolution time in hours and the total number of tickets handled.
        Args:
            conn (sqlite3.Connection): Open database connection.
        Returns:
            A pandas Dataframe
        """
        query = """
        SELECT assigned_to,
               AVG(resolution_time_hours) AS avg_hours_to_resolve,
               COUNT(*) AS ticket_count
        FROM it_tickets
        WHERE status = 'Resolved'
        GROUP BY assigned_to
        ORDER BY avg_hours_to_resolve DESC
        """
        return pd.read_sql_query(query, conn)

    @staticmethod
    def get_ticket_perf_by_status(conn):
        """Return average resolution time and ticket count grouped by status."""
        query = """
        SELECT status,
               AVG(resolution_time_hours) AS avg_hours,
               COUNT(*) AS ticket_count
        FROM it_tickets
        GROUP BY status
        ORDER BY avg_hours DESC
        """
        return pd.read_sql_query(query, conn)

