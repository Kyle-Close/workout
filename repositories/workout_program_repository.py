import sqlite3
from db.db import DB
from views.workout_day_exercise import WorkoutDayExercise


class WorkoutProgramRepository:
    """
    All queries related to WORKOUT PROGRAMS and their structure.
    """

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_latest_program_week_entry(self, user_id: int, program_id: int) -> int:
        """
        Get what week the user is on for a program.
        """

        statement = """
            SELECT MAX(program_week) AS largest_program_week
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            WHERE t1.user_id = (?) AND t2.workout_program_id = (?)
        """
        value = self.db.connection.execute(statement, (user_id, program_id)).fetchone()[
            0
        ]
        return value if value is not None else 0

    def get_program_workout_days_excercise_data(self, program_id: int):
        """
        Get all exercises for a program.
        """
        statement = """
            SELECT 
                t1.id, 
                t1.exercise_id, 
                t1.workout_program_id AS program_id, 
                t1.workout_day, 
                t1.target_sets, 
                t1.target_reps, 
                t1.intensity, 
                t3.name AS exercise_name
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs AS t2 ON t1.workout_program_id = t2.id
            INNER JOIN exercises AS t3 ON t1.exercise_id = t3.id
            WHERE t1.workout_program_id = (?)
        """
        self.db.connection.row_factory = sqlite3.Row
        rows = self.db.connection.execute(statement, (program_id,)).fetchall()
        return [WorkoutDayExercise(**dict(row)) for row in rows]

    def get_number_of_days_in_program_week(self, program_id: int):
        statement = """
            SELECT MAX(t1.workout_day)
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs AS t2 ON t1.workout_program_id = t2.id
            WHERE t1.workout_program_id = ?
        """
        params = (program_id,)
        return self.db.connection.execute(statement, params).fetchone()[0]
