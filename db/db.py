import os
import sqlite3


class DatabaseConnectionError(Exception):
    """Raised when unable to connect to the database."""
    pass


class DB:
    connection: sqlite3.Connection

    def __init__(self):
        db_path = os.getenv("DATABASE_PATH", "/app/data/workout.db")
        try:
            connection = sqlite3.connect(db_path, check_same_thread=False)
            connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Error connecting to DB at {db_path}: {e}") from e

        self.connection = connection

    def close(self):
        self.connection.close()
