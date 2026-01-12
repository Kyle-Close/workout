import sqlite3
from typing import cast
from views.user import User
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise
from views.user_one_rep_maxes import UserOneRepMaxes
from views.workout_day_exercise import WorkoutDayExercise


class db:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        try:
            connection = sqlite3.connect("./data/workout.db")
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
        except Exception as e:
            raise Exception(f"Error connecting to DB: {e}")

        self.connection = connection
        self.cursor = cursor

    def get_user(self, username: str) -> User:
        statement = "SELECT * FROM users WHERE username = (?)"
        _ = self.cursor.execute(statement, (username,))
        user = cast(User, self.cursor.fetchone())
        return user

    def get_program_workout_days_excercises_data(self, program_id: int):
        statement = """
            SELECT t1.id, t1.exercise_id, t1.workout_program_id, t1.workout_day, t1.target_sets, t1.target_reps, t1.intensity
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs as t2 ON t1.workout_program_id = t2.id
            WHERE t1.workout_program_id = (?)
        """
        _ = self.cursor.execute(statement, (program_id,))
        rows = cast(
            list[tuple[int, int, int, int, int, int, float]], self.cursor.fetchall()
        )

        return [WorkoutDayExercise(row) for row in rows]

    def get_user_one_rep_maxes(self, user_id: int) -> list[UserOneRepMaxes]:
        statement = """
            SELECT t1.name,  FROM user_one_rep_maxes WHERE user_id = (?)
        """
        _ = self.cursor.execute(statement, (user_id,))
        rows = cast(list[tuple[int, int, int, float]], self.cursor.fetchall())
        return [UserOneRepMaxes(row) for row in rows]

    def get_user_one_rep_maxes_with_exercise_data(
        self, user_id: int
    ) -> list[UserOneRepMaxWithExercise]:
        statement = """
            SELECT *
            FROM user_one_rep_maxes AS t1
            INNER JOIN exercises AS t2 ON t1.exercise_id = t2.id
            WHERE t1.user_id = (?)
        """
        _ = self.cursor.execute(statement, (user_id,))
        rows = cast(
            list[tuple[int, int, int, float, int, str, str, float]],
            self.cursor.fetchall(),
        )
        return [UserOneRepMaxWithExercise(row) for row in rows]

    def latest_program_week_entry(self, user_id: int, program_id: int) -> int:
        statement = """
            SELECT MAX(program_week) AS largest_program_week
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            WHERE t1.user_id = (?) AND t2.workout_program_id = (?)
        """
        _ = self.cursor.execute(statement, (user_id, program_id))
        value = self.cursor.fetchone()[0]
        return value if value is not None else 0

    def create_exercise_log_entry(
        self, user_id: int, workout_day_exercise_id: int, program_week: int, weight: int
    ):
        statement = """
            INSERT INTO exercise_log (user_id, workout_day_exercise_id, program_week, weight)
            VALUES (?, ?, ?, ?)
        """
        _ = self.cursor.execute(
            statement, (user_id, workout_day_exercise_id, program_week, weight)
        )
        return self.connection.commit()
