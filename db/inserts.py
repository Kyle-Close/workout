from db.db import DB


def create_exercise_log_entry(
    db: DB, user_id: int, workout_day_exercise_id: int, program_week: int, weight: int
):
    statement = """
        INSERT INTO exercise_log (user_id, workout_day_exercise_id, program_week, weight)
        VALUES (?, ?, ?, ?)
    """
    _ = db.connection.execute(
        statement, (user_id, workout_day_exercise_id, program_week, weight)
    )
    db.connection.commit()
