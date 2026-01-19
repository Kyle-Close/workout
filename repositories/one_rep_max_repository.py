from typing import cast
from db.db import DB
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise


class OneRepMaxRepository:
    """
    All queries related to ONE REP MAXES.
    """

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_user_one_rep_maxes_with_exercise_data(
        self, user_id: int
    ) -> list[UserOneRepMaxWithExercise]:
        statement = """
            SELECT *
            FROM user_one_rep_maxes AS t1
            INNER JOIN exercises AS t2 ON t1.exercise_id = t2.id
            WHERE t1.user_id = (?)
        """
        rows = cast(
            list[tuple[int, int, int, float, int, str, str, float]],
            self.db.connection.execute(statement, (user_id,)).fetchall(),
        )
        return [UserOneRepMaxWithExercise(row) for row in rows]

    def update_one_rep_max(self, user_id: int, exercise_id, max: float):
        statement = """
            UPDATE user_one_rep_maxes
            SET one_rep_max = ?
            WHERE user_id = ? AND exercise_id = ?
        """
        params = [max, user_id, exercise_id]

        _ = self.db.connection.execute(statement, params)
