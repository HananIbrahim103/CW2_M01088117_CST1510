import pandas as pd
from app.services.database_manager import DatabaseManager

class Dataset:
    """ Contains all dataset-related data.
    This class handles retrieving datasets, and performing CRUD operations on the datasets_metadata database."""
    def __init__(self, name, rows, columns, uploaded_by, upload_date, dataset_id:int | None = None):
        self.dataset_id = dataset_id
        self.name = name
        self.rows = rows
        self.columns = columns
        self.uploaded_by = uploaded_by
        self.upload_date = upload_date

    # CRUD Operations-----------------------------------------------------------------------------------------------------

    @staticmethod
    def get_all_datasets(conn):
        """Get all datasets as DataFrame.
        """
        df = pd.read_sql_query(
            "SELECT * FROM datasets_metadata ORDER BY dataset_id DESC",
            conn
        )
        #conn.close()
        return df

    def insert_dataset(self) -> int:
        """Insert new dataset into database.
        Returns:
            ID of the newly inserted dataset"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO datasets_metadata 
            (name, rows, columns, uploaded_by, upload_date)
            VALUES (?, ?, ?, ?, ?)
        """, (self.name, self.rows, self.columns, self.uploaded_by, self.upload_date))
        conn.commit()
        dataset_id = cursor.lastrowid #returns the row ID of the last inserted row (used after INSERT)
        conn.close()
        return dataset_id

    @staticmethod
    def update_dataset_rows_and_columns(conn, dataset_id, new_rows, new_columns) -> int:
        """Update existing dataset status.
        Args:
            conn (sqlite3.Connection): Open database connection.
            dataset_id = ID of the dataset
            new_rows = Updated number of rows
            new_columns = Updated number of columns
        Returns:
            Number of rows that have been updated"""
        cursor = conn.cursor()
        cursor.execute(
            """
                    UPDATE datasets_metadata
                    SET rows = ?, columns = ?
                    WHERE dataset_id = ?
                    """,
            (new_rows, new_columns, dataset_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    @staticmethod
    def delete_dataset(conn, dataset_id: int) ->int:
        """Delete a dataset.
        Args:
            conn (sqlite3.Connection): Open database connection.
            dataset_id = ID of the row to be deleted
        Returns:
            Number of rows that were deleted"""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM datasets_metadata WHERE dataset_id = ?",
            (dataset_id,)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    # Analytics Queries-------------------------------------------------------------------------------------

    @staticmethod
    def get_dataset_metrics(conn):
        """Load dataset metadata and compute summary metrics.
        Args:
            conn (sqlite3.Connection): Open database connection.
        Returns:
            A tuple containing:
                - df (pandas.DataFrame): Full contents of ``datasets_metadata``.
                - total_datasets (int): Number of datasets in the table.
                - total_rows (int): Sum of the ``rows`` field across all datasets.
                - avg_columns (float): Mean of the ``columns`` field across all datasets.
        """
        df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)

        total_datasets = len(df)
        total_rows = int(df["rows"].sum())
        avg_columns = float(df["columns"].mean())
        return df, total_datasets, total_rows, avg_columns

    @staticmethod
    def count_datasets_grouped_by_uploaded_by(conn):
        """Count number of datasets uploaded by each department
        Returns:
            Dataframe of the query"""
        query = """
        SELECT uploaded_by, COUNT(*) as count
        FROM datasets_metadata
        GROUP BY uploaded_by
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

