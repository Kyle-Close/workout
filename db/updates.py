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


def update_one_rep_max(db: DB, user_id: int, exercise_id, max: float):
    statement = """
        UPDATE user_one_rep_maxes
        SET one_rep_max = ?
        WHERE user_id = ? AND exercise_id = ?
    """
    params = [max, user_id, exercise_id]

    _ = db.connection.execute(statement, params)
    db.connection.commit()
