import os
import sqlite3


class DB:
    connection: sqlite3.Connection

    def __init__(self):
        try:
            db_path = os.getenv("DATABASE_PATH", "/app/data/workout.db")
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
        except Exception as e:
            raise Exception(f"Error connecting to DB: {e}")

        self.connection = connection

    def close(self):
        self.connection.close()
