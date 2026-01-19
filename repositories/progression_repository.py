from db.db import DB
from views.one_rep_max_with_user_id_and_exercise_id import CompleteDayCalcOneRepMaxView


class ProgressionRepository:
    """
    Queries specifically for progression/1RM calculation logic.

    This is domain-specific: it's all about tracking user progress.
    """

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_exercise_data_for_updating_maxes(
        self, user_id: int, exercise_log_ids: list[int]
    ) -> list[CompleteDayCalcOneRepMaxView]:
        if not exercise_log_ids:
            return []

        placeholders = ",".join("?" for _ in exercise_log_ids)

        statement = f"""
            SELECT t1.user_id, t2.exercise_id, t3.one_rep_max, t2.target_sets, t1.sets_completed, t1.reps_in_reserve, t2.workout_day, t2.workout_program_id, t2.id, t4.name
            FROM exercise_log AS t1
            INNER JOIN workout_day_exercises AS t2
                ON t1.workout_day_exercise_id = t2.id
            INNER JOIN user_one_rep_maxes AS t3
                ON t1.user_id = t3.user_id
               AND t2.exercise_id = t3.exercise_id
            INNER JOIN exercises AS t4
                ON t2.exercise_id = t4.id
            WHERE t3.user_id = ?
              AND t1.id IN ({placeholders});
        """

        params = [user_id, *exercise_log_ids]

        rows = self.db.connection.execute(statement, params).fetchall()
        return [CompleteDayCalcOneRepMaxView(row) for row in rows]
