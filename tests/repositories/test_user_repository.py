from repositories.user_repository import UserRepository


class TestUserRepository:
    """Tests for UserRepository."""

    def test_get_user_recent_weight(self, seeded_db):
        repo = UserRepository(seeded_db)
        weight = repo.get_user_recent_weight(user_id=1)

        assert weight == 180.0

    def test_get_user_recent_weight_no_user(self, seeded_db):
        repo = UserRepository(seeded_db)
        weight = repo.get_user_recent_weight(user_id=999)

        assert weight is None

    def test_get_user_recent_weight_most_recent(self, seeded_db):
        # Add older and newer weight entries
        seeded_db.connection.executemany(
            "INSERT INTO user_weight (user_id, weight, date) VALUES (?, ?, ?)",
            [
                (1, 175.0, "2023-12-01"),  # Older
                (1, 185.0, "2024-02-01"),  # Newer
            ],
        )
        seeded_db.connection.commit()

        repo = UserRepository(seeded_db)
        weight = repo.get_user_recent_weight(user_id=1)

        assert weight == 185.0  # Most recent by date
