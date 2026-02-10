from db.db import DB
from views.program_summary import ProgramSummary
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
        result = self.db.connection.execute(statement, (user_id, program_id)).fetchone()
        return result[0] if result is not None and result[0] is not None else 0

    def get_program_workout_days_exercise_data(self, program_id: int) -> list[WorkoutDayExercise]:
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
        rows = self.db.connection.execute(statement, (program_id,)).fetchall()
        return [WorkoutDayExercise(**dict(row)) for row in rows]

    def get_user_programs(self, user_id: int) -> list[ProgramSummary]:
        statement = "SELECT id, name FROM workout_programs WHERE user_id = ?"
        rows = self.db.connection.execute(statement, (user_id,)).fetchall()
        return [ProgramSummary(id=row["id"], name=row["name"]) for row in rows]

    def get_program_detail(self, program_id: int) -> list[dict]:
        statement = """
            SELECT
                t1.workout_day,
                t3.name AS exercise_name,
                t1.target_sets,
                t1.target_reps,
                t1.intensity,
                t1.optional,
                t3.equipment_type,
                t2.id AS program_id,
                t2.name AS program_name
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs AS t2 ON t1.workout_program_id = t2.id
            INNER JOIN exercises AS t3 ON t1.exercise_id = t3.id
            WHERE t1.workout_program_id = ?
            ORDER BY t1.workout_day, t1.id
        """
        rows = self.db.connection.execute(statement, (program_id,)).fetchall()
        return [dict(row) for row in rows]

    def get_number_of_days_in_program_week(self, program_id: int) -> int:
        statement = """
            SELECT MAX(t1.workout_day)
            FROM workout_day_exercises AS t1
            INNER JOIN workout_programs AS t2 ON t1.workout_program_id = t2.id
            WHERE t1.workout_program_id = ?
        """
        params = (program_id,)
        result = self.db.connection.execute(statement, params).fetchone()
        return result[0] if result is not None and result[0] is not None else 0

    def update_program(self, program_id: int, name: str):
        statement = """
            UPDATE workout_programs
            SET name = ?
            WHERE id = ?
        """

        cursor = self.db.connection.execute(statement, (name, program_id))
        self.db.connection.commit()
        return cursor.rowcount

    def create_program(self, user_id: int, name: str) -> int:
        statement = "INSERT INTO workout_programs (user_id, name) VALUES (?, ?)"
        cursor = self.db.connection.execute(statement, (user_id, name))
        return cursor.lastrowid

    def create_workout_day_exercises(self, program_id: int, exercises: list[dict]) -> None:
        statement = """
            INSERT INTO workout_day_exercises
            (workout_program_id, exercise_id, workout_day, target_sets, target_reps, intensity, optional)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (program_id, e["exercise_id"], e["workout_day"], e["target_sets"],
             e["target_reps"], e["intensity"], int(e["optional"]))
            for e in exercises
        ]
        self.db.connection.executemany(statement, rows)
