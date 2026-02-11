from db.db import DB


class UserRepository:
    """All queries related to USER data."""

    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_user_recent_weight(self, user_id: int) -> float | None:
        statement = """
            SELECT t1.weight
            FROM user_weight AS t1
            INNER JOIN users AS t2 ON t1.user_id = t2.id
            WHERE t1.user_id = ?
            ORDER BY date DESC
            LIMIT 1
        """
        result = self.db.connection.execute(statement, (user_id,)).fetchone()
        return result[0] if result is not None else None

    def create_user_weight(self, user_id: int, weight: float, date: str) -> int:
        statement = """
            INSERT INTO user_weight (user_id, weight, date)
            VALUES (?, ?, ?)
        """
        cursor = self.db.connection.execute(statement, (user_id, weight, date))
        return cursor.lastrowid

    def get_user_weight_history(self, user_id: int) -> list[dict]:
        statement = """
            SELECT id, weight, date
            FROM user_weight
            WHERE user_id = ?
            ORDER BY date DESC
        """
        rows = self.db.connection.execute(statement, (user_id,)).fetchall()
        return [{"id": row[0], "weight": row[1], "date": row[2]} for row in rows]

    def delete_user_weight(self, weight_id: int) -> bool:
        statement = "DELETE FROM user_weight WHERE id = ?"
        cursor = self.db.connection.execute(statement, (weight_id,))
        return cursor.rowcount > 0
