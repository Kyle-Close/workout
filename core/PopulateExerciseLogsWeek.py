from db.db import DB
from helpers.Round import round_to_nearest
from db.selects import (
    get_program_workout_days_excercises_data,
    get_user_one_rep_maxes_with_exercise_data,
    latest_program_week_entry,
)
from db.inserts import create_exercise_log_entry


def populate_exercise_logs_week(db: DB, user_id: int, program_id: int):
    workout_day_entries = get_program_workout_days_excercises_data(db, program_id)
    one_rep_maxes_with_exercise = get_user_one_rep_maxes_with_exercise_data(db, user_id)
    new_week_num = latest_program_week_entry(db, user_id, program_id) + 1

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

        weight = round_to_nearest(max * intensity, weight_increment)
        create_exercise_log_entry(db, user_id, entry.id, new_week_num, weight)
