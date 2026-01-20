from typing import final
from db.db import DB
from repositories.exercise_log_repository import ExerciseLogRepository


@final
class ExerciseLogService:
    def __init__(self, db: DB) -> None:
        self.db = db
        self.exercise_log_repository = ExerciseLogRepository(db)

    def get_exercise_logs_by_week(self, user_id: int, program_id: int, week_num: int):
        return self.exercise_log_repository.get_user_program_exercise_logs_by_week(
            user_id, program_id, week_num
        )

    def get_current_day_of_week(
        self, user_id: int, workout_program_id: int, week_num: int
    ):
        return self.exercise_log_repository.get_current_workout_day_of_week(
            user_id, workout_program_id, week_num
        )
