from repositories.workout_program_repository import WorkoutProgramRepository


class TestWorkoutProgramRepository:
    """Tests for WorkoutProgramRepository."""

    def test_get_latest_program_week_entry(self, seeded_db_with_logs):
        repo = WorkoutProgramRepository(seeded_db_with_logs)
        week = repo.get_latest_program_week_entry(user_id=1, program_id=1)

        assert week == 1

    def test_get_latest_program_week_entry_no_logs(self, seeded_db):
        repo = WorkoutProgramRepository(seeded_db)
        week = repo.get_latest_program_week_entry(user_id=1, program_id=1)

        assert week == 0

    def test_get_latest_program_week_entry_multiple_weeks(self, seeded_db_with_logs):
        # Add logs for week 2
        seeded_db_with_logs.connection.execute(
            """INSERT INTO exercise_log
               (user_id, workout_day_exercise_id, program_week, weight, completed)
               VALUES (1, 1, 2, 155, 0)"""
        )
        seeded_db_with_logs.connection.commit()

        repo = WorkoutProgramRepository(seeded_db_with_logs)
        week = repo.get_latest_program_week_entry(user_id=1, program_id=1)

        assert week == 2

    def test_get_program_workout_days_exercise_data(self, seeded_db):
        repo = WorkoutProgramRepository(seeded_db)
        exercises = repo.get_program_workout_days_exercise_data(program_id=1)

        assert len(exercises) == 4
        exercise_names = [e.exercise_name for e in exercises]
        assert "Bench Press" in exercise_names
        assert "Squat" in exercise_names
        assert "Deadlift" in exercise_names

    def test_get_program_workout_days_exercise_data_empty_program(self, seeded_db):
        # Create empty program
        seeded_db.connection.execute(
            "INSERT INTO workout_programs (id, user_id, name) VALUES (2, 1, 'Empty Program')"
        )
        seeded_db.connection.commit()

        repo = WorkoutProgramRepository(seeded_db)
        exercises = repo.get_program_workout_days_exercise_data(program_id=2)

        assert len(exercises) == 0

    def test_get_number_of_days_in_program_week(self, seeded_db):
        repo = WorkoutProgramRepository(seeded_db)
        days = repo.get_number_of_days_in_program_week(program_id=1)

        assert days == 2  # Days 1 and 2

    def test_get_number_of_days_in_program_week_empty(self, seeded_db):
        seeded_db.connection.execute(
            "INSERT INTO workout_programs (id, user_id, name) VALUES (2, 1, 'Empty Program')"
        )
        seeded_db.connection.commit()

        repo = WorkoutProgramRepository(seeded_db)
        days = repo.get_number_of_days_in_program_week(program_id=2)

        assert days == 0
