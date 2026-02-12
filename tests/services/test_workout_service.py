import pytest

from services.workout_service import WorkoutService


class TestWorkoutService:
    """Tests for WorkoutService."""

    def test_get_latest_program_week_entry(self, seeded_db_with_logs):
        service = WorkoutService(seeded_db_with_logs)
        week = service.get_latest_program_week_entry(user_id=1, workout_program_id=1)

        assert week == 1

    def test_check_is_week_complete_false(self, seeded_db_with_logs):
        service = WorkoutService(seeded_db_with_logs)
        is_complete = service.check_is_week_complete(
            user_id=1, program_id=1, week_num=1
        )

        assert is_complete is False  # Deadlift not completed

    def test_check_is_week_complete_true(self, seeded_db_with_logs):
        # Complete all mandatory exercises
        seeded_db_with_logs.connection.execute(
            "UPDATE exercise_log SET completed = 1 WHERE id = 3"
        )
        seeded_db_with_logs.connection.commit()

        service = WorkoutService(seeded_db_with_logs)
        is_complete = service.check_is_week_complete(
            user_id=1, program_id=1, week_num=1
        )

        assert is_complete is True

    def test_is_assisted_exercise(self, seeded_db):
        service = WorkoutService(seeded_db)

        assert service._is_assisted_exercise("Assisted Pull-up") is True
        assert service._is_assisted_exercise("assisted dip") is True
        assert service._is_assisted_exercise("Bench Press") is False
        assert service._is_assisted_exercise("Squat") is False

    def test_populate_exercise_logs_week(self, seeded_db):
        service = WorkoutService(seeded_db)
        service.populate_exercise_logs_week(user_id=1, program_id=1)
        seeded_db.connection.commit()

        logs = seeded_db.connection.execute(
            "SELECT * FROM exercise_log WHERE user_id = 1"
        ).fetchall()

        assert len(logs) == 4  # 4 exercises in the program

    def test_populate_exercise_logs_week_calculates_weight(self, seeded_db):
        service = WorkoutService(seeded_db)
        service.populate_exercise_logs_week(user_id=1, program_id=1)
        seeded_db.connection.commit()

        log = seeded_db.connection.execute(
            """SELECT el.weight, wde.exercise_id
               FROM exercise_log el
               JOIN workout_day_exercises wde ON el.workout_day_exercise_id = wde.id
               WHERE el.user_id = 1 AND wde.exercise_id = 1"""
        ).fetchone()

        # Bench Press: 200 * 0.75 = 150, rounded to nearest 5
        assert log["weight"] == 150

    def test_populate_exercise_logs_week_assisted_exercise(self, seeded_db):
        service = WorkoutService(seeded_db)
        service.populate_exercise_logs_week(user_id=1, program_id=1)
        seeded_db.connection.commit()

        log = seeded_db.connection.execute(
            """SELECT el.weight, wde.exercise_id
               FROM exercise_log el
               JOIN workout_day_exercises wde ON el.workout_day_exercise_id = wde.id
               WHERE el.user_id = 1 AND wde.exercise_id = 4"""
        ).fetchone()

        # Assisted Pull-up: body_weight(180) - (1RM(50) * intensity(0.70)) = 180 - 35 = 145
        assert log["weight"] == 145

    def test_populate_exercise_logs_week_missing_exercise_data(self, seeded_db):
        # Remove one rep max for an exercise — service should skip it with a warning
        seeded_db.connection.execute(
            "DELETE FROM user_one_rep_maxes WHERE exercise_id = 1"
        )
        seeded_db.connection.commit()

        service = WorkoutService(seeded_db)
        service.populate_exercise_logs_week(user_id=1, program_id=1)

        # Verify logs were created for the remaining exercises but not the deleted one
        rows = seeded_db.connection.execute(
            "SELECT workout_day_exercise_id FROM exercise_log WHERE user_id = 1 AND program_week = 1"
        ).fetchall()
        wde_ids = [r[0] for r in rows]
        # workout_day_exercise_id=1 maps to exercise_id=1, which should be skipped
        assert 1 not in wde_ids

    def test_populate_exercise_logs_week_missing_user_weight(self, seeded_db):
        # Remove user weight - needed for assisted exercises
        seeded_db.connection.execute("DELETE FROM user_weight WHERE user_id = 1")
        seeded_db.connection.commit()

        service = WorkoutService(seeded_db)

        with pytest.raises(ValueError, match="No weight recorded for user"):
            service.populate_exercise_logs_week(user_id=1, program_id=1)

    def test_populate_exercise_logs_week_increments_week(self, seeded_db_with_logs):
        service = WorkoutService(seeded_db_with_logs)
        service.populate_exercise_logs_week(user_id=1, program_id=1)
        seeded_db_with_logs.connection.commit()

        logs = seeded_db_with_logs.connection.execute(
            "SELECT DISTINCT program_week FROM exercise_log WHERE user_id = 1 ORDER BY program_week"
        ).fetchall()

        weeks = [log[0] for log in logs]
        assert weeks == [1, 2]  # Week 1 existed, week 2 was created
