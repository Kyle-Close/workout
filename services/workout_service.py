from venv import logger

from fastapi import HTTPException
from db.db import DB
from db.inserts import create_exercise_log_entry
from db.selects import (
    get_latest_program_week_entry,
    get_program_workout_days_excercises_data,
    get_user_one_rep_maxes_with_exercise_data,
    get_user_recent_weight,
)
from db.updates import update_many_exercise_logs
from helpers.Round import round_to_nearest
from views.exercise_log import ExerciseLog


class WorkoutService:
    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def update_exercise_logs(self, logs: list[ExerciseLog]):
        try:
            update_many_exercise_logs(self.db, logs)
        except Exception as e:
            logger.error(f"Failed to update logs: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update exercise logs"
            )

    def populate_exercise_logs_week(self, user_id: int, program_id: int):
        workout_day_entries = get_program_workout_days_excercises_data(
            self.db, program_id
        )
        one_rep_maxes_with_exercise = get_user_one_rep_maxes_with_exercise_data(
            self.db, user_id
        )
        new_week_num = get_latest_program_week_entry(self.db, user_id, program_id) + 1

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
                current_body_weight = get_user_recent_weight(self.db, user_id)
                weight = round_to_nearest(
                    current_body_weight - (max * intensity), weight_increment
                )
            else:
                weight = round_to_nearest(max * intensity, weight_increment)

            create_exercise_log_entry(self.db, user_id, entry.id, new_week_num, weight)
