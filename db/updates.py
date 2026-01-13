from db.db import DB


def complete_exercise_log_entry(
    db: DB,
    exercise_log_id: int,
    sets_completed: int,
    reps_in_reserve: int,
    notes: str = "",
):
    statement = """
            UPDATE exercise_log
            SET sets_completed = ?, reps_in_reserve = ?, notes = ?, completed = 1
            WHERE id = ?
        """
    _ = db.connection.execute(
        statement, (sets_completed, reps_in_reserve, notes, exercise_log_id)
    )
    db.connection.commit()
