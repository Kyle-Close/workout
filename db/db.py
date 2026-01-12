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

    def get_user(self, username: str):
        statement = "SELECT id FROM users WHERE username = (?)"
        _ = self.cursor.execute(statement, (username,))
        return self.cursor.fetchone()

    def get_program_workout_days_excercises_data(self, program_id: int):
        statement = """
            SELECT t1.id, t1.exercise_id, t1.workout_program_id, t1.workout_day, t1.target_sets, t1.target_reps, t1.intensity
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs as t2 ON t1.workout_program_id = t2.id
            WHERE t1.workout_program_id = (?)
        """
        _ = self.cursor.execute(statement, (program_id,))
        return self.cursor.fetchall()
