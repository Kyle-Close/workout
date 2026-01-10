import sqlite3
from enums.equipment_type import EquipmentType


class db:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        try:
            connection = sqlite3.connect("./data/workout.db")
            cursor = connection.cursor()
        except Exception as e:
            raise Exception(f"Error connecting to DB: {e}")

        self.connection = connection
        self.cursor = cursor

    def create_user(self, name: str):
        statement = "INSERT INTO users (username) VALUES (?)"
        _ = self.cursor.execute(statement, (name,))
        self.connection.commit()
        return self.cursor.lastrowid  # returns the primary key of created row

    def create_exercise(
        self, name: str, equipment_type: EquipmentType, weight_increment: int
    ):
        statement = "INSERT INTO exercises (name, equipment_type, weight_increment) VALUES (?, ?, ?)"
        _ = self.cursor.execute(
            statement, (name, equipment_type.name, weight_increment)
        )
        self.connection.commit()
        return self.cursor.lastrowid  # returns the primary key of created row
