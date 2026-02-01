from db.db import DB
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise
from views.user_one_rep_max_with_name import UserOneRepMaxWithName


class OneRepMaxRepository:
    """
    All queries related to ONE REP MAXES.
    """

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_user_one_rep_maxes_with_exercise_data(self, user_id: int) -> list[UserOneRepMaxWithExercise]:
        """
        Get all one rep maxes for a user with exercise data.
        """
        statement = """
            SELECT
                t1.exercise_id,
                t2.name,
                t2.weight_increment,
                t1.original_one_rep_max,
                t1.current_one_rep_max
            FROM user_one_rep_maxes AS t1
            INNER JOIN exercises AS t2 ON t1.exercise_id = t2.id
            WHERE t1.user_id = ?
        """
        rows = self.db.connection.execute(statement, (user_id,)).fetchall()
        return [UserOneRepMaxWithExercise(**dict(row)) for row in rows]

    def update_one_rep_max(self, user_id: int, exercise_id, max: float):
        statement = """
            UPDATE user_one_rep_maxes
            SET current_one_rep_max = ?
            WHERE user_id = ? AND exercise_id = ?
        """
        params = [max, user_id, exercise_id]

        _ = self.db.connection.execute(statement, params)

    def get_all_user_maxes(self, user_id: int):
        """
        Get all user one rep max table data
        """
        statement = """
            SELECT
                t1.*,
                t2.name as exercise_name
            FROM user_one_rep_maxes AS t1
            INNER JOIN exercises AS t2 ON t1.exercise_id = t2.id
            WHERE t1.user_id = ?
        """
        rows = self.db.connection.execute(statement, (user_id,)).fetchall()
        return [UserOneRepMaxWithName(**dict(row)) for row in rows]
