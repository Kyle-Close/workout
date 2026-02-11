from repositories.one_rep_max_repository import OneRepMaxRepository


class TestOneRepMaxRepository:
    """Tests for OneRepMaxRepository."""

    def test_get_user_one_rep_maxes_with_exercise_data(self, seeded_db):
        repo = OneRepMaxRepository(seeded_db)
        maxes = repo.get_user_one_rep_maxes_with_exercise_data(user_id=1)

        assert len(maxes) == 4
        bench_max = next((m for m in maxes if m.name == "Bench Press"), None)
        assert bench_max is not None
        assert bench_max.current_one_rep_max == 200.0
        assert bench_max.weight_increment == 5.0

    def test_get_user_one_rep_maxes_with_exercise_data_no_user(self, seeded_db):
        repo = OneRepMaxRepository(seeded_db)
        maxes = repo.get_user_one_rep_maxes_with_exercise_data(user_id=999)

        assert len(maxes) == 0

    def test_update_one_rep_max(self, seeded_db):
        repo = OneRepMaxRepository(seeded_db)
        repo.update_one_rep_max(user_id=1, exercise_id=1, max=210.0)
        seeded_db.connection.commit()

        result = seeded_db.connection.execute(
            "SELECT current_one_rep_max FROM user_one_rep_maxes WHERE user_id = 1 AND exercise_id = 1"
        ).fetchone()

        assert result[0] == 210.0

    def test_update_one_rep_max_preserves_other_maxes(self, seeded_db):
        repo = OneRepMaxRepository(seeded_db)
        repo.update_one_rep_max(user_id=1, exercise_id=1, max=210.0)
        seeded_db.connection.commit()

        result = seeded_db.connection.execute(
            "SELECT current_one_rep_max FROM user_one_rep_maxes WHERE user_id = 1 AND exercise_id = 2"
        ).fetchone()

        assert result[0] == 300.0  # Squat unchanged
