from services.exercise_log_service import ExerciseLogService


class TestExerciseLogService:
    """Tests for ExerciseLogService."""

    def test_get_exercise_logs_by_week(self, seeded_db_with_logs):
        service = ExerciseLogService(seeded_db_with_logs)
        logs = service.get_exercise_logs_by_week(
            user_id=1, program_id=1, week_num=1
        )

        assert len(logs) == 4

    def test_get_exercise_logs_by_week_empty(self, seeded_db_with_logs):
        service = ExerciseLogService(seeded_db_with_logs)
        logs = service.get_exercise_logs_by_week(
            user_id=1, program_id=1, week_num=99
        )

        assert len(logs) == 0

    def test_get_current_day_of_week(self, seeded_db_with_logs):
        service = ExerciseLogService(seeded_db_with_logs)
        day = service.get_current_day_of_week(
            user_id=1, workout_program_id=1, week_num=1
        )

        assert day == 2  # Day 2 has incomplete mandatory

    def test_get_detailed_log_info(self, seeded_db_with_logs):
        service = ExerciseLogService(seeded_db_with_logs)
        logs = service.get_detailed_log_info([1])

        assert len(logs) == 1
        assert logs[0].exercise_name == "Bench Press"
        assert logs[0].workout_program_id == 1

    def test_get_detailed_log_info_multiple(self, seeded_db_with_logs):
        service = ExerciseLogService(seeded_db_with_logs)
        logs = service.get_detailed_log_info([1, 2, 3])

        assert len(logs) == 3
