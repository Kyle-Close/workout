from db.db import db
from helpers.Round import round_to_nearest


def populate_exercise_logs_week(db: db, user_id: int, program_id: int):
    workout_day_entries = db.get_program_workout_days_excercises_data(program_id)
    one_rep_maxes_with_exercise = db.get_user_one_rep_maxes_with_exercise_data(user_id)
    new_week_num = db.latest_program_week_entry(user_id, program_id) + 1

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
        db.create_exercise_log_entry(user_id, entry.id, new_week_num, weight)
