import pytest

from repositories.exercise_log_repository import ExerciseLogRepository
from views.exercise_log import ExerciseLog


class TestExerciseLogRepository:
    """Tests for ExerciseLogRepository."""

    def test_get_user_program_exercise_logs_by_week(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        logs = repo.get_user_program_exercise_logs_by_week(
            user_id=1, program_id=1, week_num=1
        )

        assert len(logs) == 4
        assert logs[0].exercise_name == "Bench Press"
        assert logs[0].program_week == 1

    def test_get_user_program_exercise_logs_by_week_empty(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        logs = repo.get_user_program_exercise_logs_by_week(
            user_id=1, program_id=1, week_num=99
        )

        assert len(logs) == 0

    def test_get_current_workout_day_of_week(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        # Day 1 exercises are completed, Day 2 has incomplete mandatory exercises
        day = repo.get_current_workout_day_of_week(
            user_id=1, program_id=1, week_num=1
        )

        assert day == 2  # Deadlift on day 2 is not completed

    def test_get_current_workout_day_of_week_all_complete(self, seeded_db_with_logs):
        # Complete the remaining mandatory exercise
        seeded_db_with_logs.connection.execute(
            "UPDATE exercise_log SET completed = 1 WHERE id = 3"
        )
        seeded_db_with_logs.connection.commit()

        repo = ExerciseLogRepository(seeded_db_with_logs)
        day = repo.get_current_workout_day_of_week(
            user_id=1, program_id=1, week_num=1
        )

        assert day == 0  # All mandatory done

    def test_create_exercise_log_entry(self, seeded_db):
        repo = ExerciseLogRepository(seeded_db)
        repo.create_exercise_log_entry(
            user_id=1, workout_day_exercise_id=1, program_week=1, weight=150
        )
        seeded_db.connection.commit()

        result = seeded_db.connection.execute(
            "SELECT * FROM exercise_log WHERE user_id = 1"
        ).fetchall()

        assert len(result) == 1
        assert result[0]["weight"] == 150
        assert result[0]["program_week"] == 1

    def test_update_many_exercise_logs(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        logs = [
            ExerciseLog(
                id=1,
                user_id=1,
                workout_day_exercise_id=1,
                program_week=1,
                weight=160,
                sets_completed=3,
                reps_in_reserve=1,
                notes="Updated",
                completed=True,
            )
        ]

        repo.update_many_exercise_logs(logs)
        seeded_db_with_logs.connection.commit()

        result = seeded_db_with_logs.connection.execute(
            "SELECT * FROM exercise_log WHERE id = 1"
        ).fetchone()

        assert result["weight"] == 160
        assert result["notes"] == "Updated"
        assert result["reps_in_reserve"] == 1

    def test_get_count_of_incomplete_mandatory_logs_by_week(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        count = repo.get_count_of_incomplete_mandatory_logs_by_week(
            user_id=1, program_id=1, week_num=1
        )

        # Deadlift is the only incomplete mandatory exercise
        assert count == 1

    def test_get_detailed_log_info(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        logs = repo.get_detailed_log_info([1, 2])

        assert len(logs) == 2
        assert logs[0].exercise_name in ["Bench Press", "Squat"]
        assert logs[0].workout_program_name == "Test Program"
        assert logs[0].workout_program_id == 1

    def test_get_detailed_log_info_empty_list(self, seeded_db_with_logs):
        repo = ExerciseLogRepository(seeded_db_with_logs)
        logs = repo.get_detailed_log_info([])

        assert len(logs) == 0
