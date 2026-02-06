from datetime import date

from db.db import DB
from views.detailed_exercise_log_info import DetailedExerciseLog
from views.exercise_history import ExerciseHistoryEntry
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
                t3.id AS exercise_id,
                t3.name AS exercise_name,
                t1.program_week,
                t2.workout_day,
                t1.weight,
                t2.target_sets,
                t2.target_reps,
                t1.sets_completed,
                t1.reps_in_reserve,
                t2.optional,
                t2.id AS workout_day_exercise_id,
                t1.completed,
                t3.equipment_type,
                (t1.weight - prev.weight) AS weight_change
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            INNER JOIN exercises AS t3 ON t2.exercise_id = t3.id
            LEFT JOIN exercise_log AS prev
                ON prev.workout_day_exercise_id = t1.workout_day_exercise_id
                AND prev.user_id = t1.user_id
                AND prev.program_week = t1.program_week - 1
            WHERE t1.user_id = ? AND t2.workout_program_id = ? AND t1.program_week = ?
        """
        params = (user_id, program_id, week_num)
        rows = self.db.connection.execute(statement, params).fetchall()
        return [ExerciseEntryForDayView(**dict(row)) for row in rows]

    def get_current_workout_day_of_week(self, user_id: int, program_id: int, week_num: int) -> int:
        statement = """
            SELECT MIN(t2.workout_day)
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            WHERE t1.user_id = ? AND t2.workout_program_id = ? AND t1.program_week = ? AND t1.completed = 0 AND t2.optional = 0
        """
        params = (user_id, program_id, week_num)
        result = self.db.connection.execute(statement, params).fetchone()
        return result[0] if result is not None and result[0] is not None else 0

    def create_exercise_log_entry(self, user_id: int, workout_day_exercise_id: int, program_week: int, weight: float):
        statement = """
            INSERT INTO exercise_log (user_id, workout_day_exercise_id, program_week, weight)
            VALUES (?, ?, ?, ?)
        """
        _ = self.db.connection.execute(statement, (user_id, workout_day_exercise_id, program_week, weight))

    def update_many_exercise_logs(self, exercise_logs: list[ExerciseLog]):
        statement = """
                UPDATE exercise_log
                SET program_week = ?, weight = ?, sets_completed = ?, reps_in_reserve = ?, notes = ?, completed = ?, completed_at = ?
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
                date.today().isoformat() if log.completed else None,
                log.id,
            )
            for log in exercise_logs
        ]

        _ = self.db.connection.executemany(statement, updates)

    def get_count_of_incomplete_mandatory_logs_by_week(self, user_id: int, program_id: int, week_num: int) -> int:
        statement = """
            SELECT COUNT(*)
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            WHERE t1.user_id = ? AND t1.program_week = ? AND t2.workout_program_id = ? AND t2.optional = 0 AND t1.completed = 0
        """
        params = (user_id, week_num, program_id)
        result = self.db.connection.execute(statement, params).fetchone()
        return int(result[0]) if result is not None else 0

    def get_detailed_log_info(self, log_ids: list[int]) -> list[DetailedExerciseLog]:
        if not log_ids:
            return []
        placeholders = ",".join("?" for _ in log_ids)
        statement = f"""
            SELECT
                t1.id AS exercise_log_id,
                t1.user_id,
                t1.workout_day_exercise_id,
                t1.program_week,
                t1.weight,
                t1.sets_completed,
                t1.reps_in_reserve,
                t1.notes,
                t1.completed,
                t2.workout_program_id,
                t2.workout_day,
                t2.target_sets,
                t2.target_reps,
                t2.intensity,
                t2.optional,
                t3.id AS exercise_id,
                t3.name AS exercise_name,
                t3.equipment_type,
                t3.weight_increment,
                t4.name AS workout_program_name
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
            INNER JOIN exercises AS t3 ON t2.exercise_id = t3.id
            INNER JOIN workout_programs AS t4 ON t2.workout_program_id = t4.id
            WHERE t1.id IN ({placeholders})
        """
        params = (*log_ids,)
        rows = self.db.connection.execute(statement, params).fetchall()
        return [DetailedExerciseLog(**dict(row)) for row in rows]

    def get_exercise_history(self, user_id: int, exercise_id: int) -> tuple[str | None, list[ExerciseHistoryEntry]]:
        statement = """
            SELECT
                e.name AS exercise_name,
                el.completed_at AS date,
                el.weight,
                el.sets_completed,
                wde.target_sets,
                el.reps_in_reserve
            FROM exercise_log el
            INNER JOIN workout_day_exercises wde ON el.workout_day_exercise_id = wde.id
            INNER JOIN exercises e ON wde.exercise_id = e.id
            WHERE el.user_id = ? AND wde.exercise_id = ? AND el.completed = 1 AND el.completed_at IS NOT NULL
            ORDER BY el.completed_at ASC
        """
        rows = self.db.connection.execute(statement, (user_id, exercise_id)).fetchall()
        if not rows:
            return None, []
        exercise_name = rows[0]["exercise_name"]
        entries = [ExerciseHistoryEntry(**{k: row[k] for k in ("date", "weight", "sets_completed", "target_sets", "reps_in_reserve")}) for row in rows]
        return exercise_name, entries
