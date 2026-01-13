from db.db import DB
from views.exercise_log import ExerciseLog


def update_many_exercise_logs(db: DB, exercise_logs: list[ExerciseLog]):
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

    _ = db.connection.executemany(statement, updates)
    db.connection.commit()
