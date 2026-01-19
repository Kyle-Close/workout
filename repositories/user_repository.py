from db.db import DB


class UserRepository:
    """All queries related to USER data."""

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_user_recent_weight(self, user_id: int):
        statement = """
            SELECT t1.weight
            FROM user_weight AS t1
            INNER JOIN users AS t2 ON t1.user_id = t2.id
            WHERE t1.user_id = ? 
            ORDER BY date DESC
            LIMIT 1
        """
        value = self.db.connection.execute(statement, (user_id,)).fetchone()[0]
        return value if value is not None else -1
