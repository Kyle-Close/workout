from db.db import DB
from db.updates import update_many_exercise_logs
from views.exercise_log import ExerciseLog


def complete_day_logs(db: DB, exercises: list[ExerciseLog]):
    update_many_exercise_logs(db, exercises)
