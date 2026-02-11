from db.db import DB


class ExerciseRepository:
    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db

    def get_all(self) -> list[dict]:
        statement = "SELECT id, name, equipment_type, weight_increment FROM exercises ORDER BY name"
        rows = self.db.connection.execute(statement).fetchall()
        return [dict(row) for row in rows]

    def find_by_name(self, name: str) -> dict | None:
        statement = "SELECT id, name, equipment_type, weight_increment FROM exercises WHERE name = ?"
        row = self.db.connection.execute(statement, (name,)).fetchone()
        return dict(row) if row else None

    def get_id_map_by_name(self, names: list[str]) -> dict[str, int]:
        placeholders = ",".join("?" for _ in names)
        statement = f"SELECT id, name FROM exercises WHERE name IN ({placeholders})"
        rows = self.db.connection.execute(statement, names).fetchall()
        return {row["name"]: row["id"] for row in rows}

    def create_exercise(self, name: str, equipment_type: str, weight_increment: float) -> int:
        statement = "INSERT INTO exercises (name, equipment_type, weight_increment) VALUES (?, ?, ?)"
        cursor = self.db.connection.execute(statement, (name, equipment_type, weight_increment))
        return cursor.lastrowid
