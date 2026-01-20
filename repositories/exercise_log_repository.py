from db.db import DB
from views.exercise_log import ExerciseLog
from views.get_current_week_view import ExerciseEntryForDayView

class ExerciseLogRepository:
    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_user_program_exercise_logs_by_week(
        self, user_id: int, program_id: int, week_num: int
    ) -> list[ExerciseEntryForDayView]:
        statement = """
            SELECT        
                t1.id  AS exercise_log_id,
                t3.name AS exercise_name,
                t1.program_week,
                t2.workout_day,
                t1.weight,
                t2.target_sets,
                t2.target_reps,
                t1.sets_completed,
                t1.reps_in_reserve,
                t2.optional,
                t2.id AS workout_day_exercise_id
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            INNER JOIN exercises AS t3 ON t2.exercise_id = t3.id
            WHERE t1.user_id = ? AND t2.workout_program_id = ? AND t1.program_week = ?
        """
        params = (user_id, program_id, week_num)
        rows = self.db.connection.execute(statement, params).fetchall()
        return [ExerciseEntryForDayView(**dict(row)) for row in rows]

    def get_current_workout_day_of_week(
        self, user_id: int, program_id: int, week_num: int
    ):
        statement = """
            SELECT MIN(t2.workout_day)
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            WHERE t1.user_id = ? AND t2.workout_program_id = ? AND t1.program_week = ? AND t1.completed = 0 AND t2.optional = 0
        """
        params = (user_id, program_id, week_num)
        value = self.db.connection.execute(statement, params).fetchone()[0]
        return value if value is not None else 0

    def create_exercise_log_entry(
        self, user_id: int, workout_day_exercise_id: int, program_week: int, weight: int
    ):
        statement = """
            INSERT INTO exercise_log (user_id, workout_day_exercise_id, program_week, weight)
            VALUES (?, ?, ?, ?)
        """
        _ = self.db.connection.execute(
            statement, (user_id, workout_day_exercise_id, program_week, weight)
        )

    def update_many_exercise_logs(self, exercise_logs: list[ExerciseLog]):
        statement = """
                UPDATE exercise_log
                SET program_week = ?, weight = ?, sets_completed = ?, reps_in_reserve = ?, notes = ?, completed = ?
                WHERE id = ?
        """
        updates = [
            (
                log.program_week,
                log.weight,
                log.sets_completed,
                log.reps_in_reserve,
                log.notes,
                log.completed,
                log.id,
            )
            for log in exercise_logs
        ]

        _ = self.db.connection.executemany(statement, updates)
