from typing import final
from venv import logger

from fastapi import HTTPException
from db.db import DB
from helpers.Round import round_to_nearest
from repositories.exercise_log_repository import ExerciseLogRepository
from repositories.one_rep_max_repository import OneRepMaxRepository
from repositories.user_repository import UserRepository
from repositories.workout_program_repository import WorkoutProgramRepository
from views.exercise_log import ExerciseLog


@final
class WorkoutService:
    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db
        self.exercise_log_repository = ExerciseLogRepository(db)
        self.workout_program_repository = WorkoutProgramRepository(db)
        self.one_rep_max_repository = OneRepMaxRepository(db)
        self.user_repository = UserRepository(db)

    def get_current_week(self, user_id: int, workout_program_id: int):
        return self.workout_program_repository.get_latest_program_week_entry(
            user_id, workout_program_id
        )

    def update_exercise_logs(self, logs: list[ExerciseLog]):
        try:
            self.exercise_log_repository.update_many_exercise_logs(logs)
        except Exception as e:
            logger.error(f"Failed to update logs: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update exercise logs"
            )

    def populate_exercise_logs_week(self, user_id: int, program_id: int):
        workout_day_entries = (
            self.workout_program_repository.get_program_workout_days_excercises_data(
                program_id
            )
        )
        one_rep_maxes_with_exercise = (
            self.one_rep_max_repository.get_user_one_rep_maxes_with_exercise_data(
                user_id
            )
        )
        new_week_num = (
            self.workout_program_repository.get_latest_program_week_entry(
                user_id, program_id
            )
            + 1
        )

        for entry in workout_day_entries:
            exercise_data = next(
                (
                    e
                    for e in one_rep_maxes_with_exercise
                    if e.exercise_id == entry.exercise_id
                ),
                None,
            )

            if exercise_data is None:
                raise Exception("Could not find exercise data for workout day entry")

            max = exercise_data.one_rep_max
            weight_increment = exercise_data.weight_increment
            intensity = entry.intensity / 100
            weight = 0

            if "assisted" in entry.exercise_name.lower():
                current_body_weight = self.user_repository.get_user_recent_weight(
                    user_id
                )
                weight = round_to_nearest(
                    current_body_weight - (max * intensity), weight_increment
                )
            else:
                weight = round_to_nearest(max * intensity, weight_increment)

            self.exercise_log_repository.create_exercise_log_entry(
                user_id, entry.id, new_week_num, weight
            )
