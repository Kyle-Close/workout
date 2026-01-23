import pytest


class TestGetCurrentWeekDataEndpoint:
    """Integration tests for GET /get-current-week-data."""

    def test_get_current_week_data_success(self, client):
        response = client.get(
            "/get-current-week-data",
            params={"user_id": 1, "workout_program_id": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert "currentDayOfWeek" in data
        assert "weekData" in data
        assert data["currentDayOfWeek"] == 2  # Day 2 has incomplete mandatory
        assert len(data["weekData"]) == 4

    def test_get_current_week_data_exercise_details(self, client):
        response = client.get(
            "/get-current-week-data",
            params={"user_id": 1, "workout_program_id": 1},
        )

        data = response.json()
        week_data = data["weekData"]

        # Verify exercise details are present
        exercise_names = [e["exercise_name"] for e in week_data]
        assert "Bench Press" in exercise_names
        assert "Squat" in exercise_names
        assert "Deadlift" in exercise_names

    def test_get_current_week_data_no_logs(self, client, seeded_db_with_logs):
        # Clear logs to test empty state
        seeded_db_with_logs.connection.execute("DELETE FROM exercise_log")
        seeded_db_with_logs.connection.commit()

        response = client.get(
            "/get-current-week-data",
            params={"user_id": 1, "workout_program_id": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currentDayOfWeek"] == 0
        assert data["weekData"] == []

    def test_get_current_week_data_missing_params(self, client):
        response = client.get("/get-current-week-data")

        assert response.status_code == 422  # Validation error


class TestGenerateLogsWeekEndpoint:
    """Integration tests for POST /generate-logs-week."""

    def test_generate_logs_week_success(self, client, seeded_db_with_logs):
        # Complete all mandatory exercises first so we can generate a new week
        seeded_db_with_logs.connection.execute(
            "UPDATE exercise_log SET completed = 1"
        )
        seeded_db_with_logs.connection.commit()

        response = client.post(
            "/generate-logs-week",
            json={"user_id": 1, "workout_program_id": 1},
        )

        assert response.status_code == 200

        # Verify new week was created
        logs = seeded_db_with_logs.connection.execute(
            "SELECT DISTINCT program_week FROM exercise_log ORDER BY program_week"
        ).fetchall()
        weeks = [log[0] for log in logs]
        assert 2 in weeks

    def test_generate_logs_week_creates_correct_exercises(self, client, seeded_db_with_logs):
        seeded_db_with_logs.connection.execute(
            "UPDATE exercise_log SET completed = 1"
        )
        seeded_db_with_logs.connection.commit()

        response = client.post(
            "/generate-logs-week",
            json={"user_id": 1, "workout_program_id": 1},
        )

        assert response.status_code == 200

        # Verify correct number of logs for week 2
        count = seeded_db_with_logs.connection.execute(
            "SELECT COUNT(*) FROM exercise_log WHERE program_week = 2"
        ).fetchone()[0]
        assert count == 4  # 4 exercises in the program

    def test_generate_logs_week_missing_params(self, client):
        response = client.post("/generate-logs-week", json={})

        assert response.status_code == 422


class TestUpdateLogsEndpoint:
    """Integration tests for PATCH /update-logs."""

    def test_update_logs_success(self, client, seeded_db_with_logs):
        response = client.patch(
            "/update-logs",
            json=[
                {
                    "id": 3,
                    "user_id": 1,
                    "workout_day_exercise_id": 3,
                    "program_week": 1,
                    "weight": 340,
                    "sets_completed": 3,
                    "reps_in_reserve": 2,
                    "notes": "Felt strong",
                    "completed": True,
                }
            ],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["logs_updated"] == 1
        assert "maxes_updated" in data
        assert "generated_new_week" in data

    def test_update_logs_triggers_new_week_generation(self, client, seeded_db_with_logs):
        # Update the only incomplete mandatory log to completed
        response = client.patch(
            "/update-logs",
            json=[
                {
                    "id": 3,
                    "user_id": 1,
                    "workout_day_exercise_id": 3,
                    "program_week": 1,
                    "weight": 340,
                    "sets_completed": 3,
                    "reps_in_reserve": 2,
                    "notes": None,
                    "completed": True,
                }
            ],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["generated_new_week"] is True

        # Verify week 2 was created
        count = seeded_db_with_logs.connection.execute(
            "SELECT COUNT(*) FROM exercise_log WHERE program_week = 2"
        ).fetchone()[0]
        assert count == 4

    def test_update_logs_empty_payload(self, client):
        response = client.patch("/update-logs", json=[])

        assert response.status_code == 400
        assert "No exercise logs provided" in response.json()["detail"]

    def test_update_logs_updates_one_rep_max(self, client, seeded_db_with_logs):
        # Get original max
        original_max = seeded_db_with_logs.connection.execute(
            "SELECT one_rep_max FROM user_one_rep_maxes WHERE user_id = 1 AND exercise_id = 3"
        ).fetchone()[0]

        # Complete with high RIR (should increase max)
        response = client.patch(
            "/update-logs",
            json=[
                {
                    "id": 3,
                    "user_id": 1,
                    "workout_day_exercise_id": 3,
                    "program_week": 1,
                    "weight": 340,
                    "sets_completed": 3,
                    "reps_in_reserve": 3,  # High RIR = +5%
                    "notes": None,
                    "completed": True,
                }
            ],
        )

        assert response.status_code == 200

        # Verify max was updated
        new_max = seeded_db_with_logs.connection.execute(
            "SELECT one_rep_max FROM user_one_rep_maxes WHERE user_id = 1 AND exercise_id = 3"
        ).fetchone()[0]

        assert new_max > original_max
        assert new_max == original_max * 1.05  # +5%

    def test_update_multiple_logs(self, client, seeded_db_with_logs):
        response = client.patch(
            "/update-logs",
            json=[
                {
                    "id": 1,
                    "user_id": 1,
                    "workout_day_exercise_id": 1,
                    "program_week": 1,
                    "weight": 155,
                    "sets_completed": 3,
                    "reps_in_reserve": 1,
                    "notes": "Updated 1",
                    "completed": True,
                },
                {
                    "id": 2,
                    "user_id": 1,
                    "workout_day_exercise_id": 2,
                    "program_week": 1,
                    "weight": 245,
                    "sets_completed": 3,
                    "reps_in_reserve": 2,
                    "notes": "Updated 2",
                    "completed": True,
                },
            ],
        )

        assert response.status_code == 200
        data = response.json()
        assert data["logs_updated"] == 2
