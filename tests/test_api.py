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

    def test_get_current_week_data_weight_change_null_for_week_1(self, client):
        response = client.get(
            "/get-current-week-data",
            params={"user_id": 1, "workout_program_id": 1},
        )

        data = response.json()
        week_data = data["weekData"]

        # Week 1 has no previous week, so weight_change should be null
        for entry in week_data:
            assert entry["weight_change"] is None

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


class TestWeightChange:
    """Tests for weight_change field in get-current-week-data."""

    def test_weight_change_with_previous_week(self, multi_week_client):
        response = multi_week_client.get(
            "/get-current-week-data",
            params={"user_id": 1, "workout_program_id": 1},
        )

        assert response.status_code == 200
        data = response.json()
        week_data = data["weekData"]

        # Build a lookup by exercise name
        by_name = {e["exercise_name"]: e for e in week_data}

        # Bench Press: week2=155, week1=150 -> +5
        assert by_name["Bench Press"]["weight_change"] == 5
        # Squat: week2=240, week1=240 -> 0
        assert by_name["Squat"]["weight_change"] == 0
        # Deadlift: week2=335, week1=340 -> -5
        assert by_name["Deadlift"]["weight_change"] == -5
        # Assisted Pull-up: week2=145, week1=145 -> 0
        assert by_name["Assisted Pull-up"]["weight_change"] == 0


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


class TestGetPrograms:
    """Integration tests for GET /programs."""

    def test_get_programs_success(self, client):
        response = client.get("/programs", params={"user_id": 1})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "Test Program"

    def test_get_programs_filters_by_user(self, client):
        response = client.get("/programs", params={"user_id": 999})

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_programs_missing_params(self, client):
        response = client.get("/programs")

        assert response.status_code == 422


class TestGetProgramDetail:
    """Integration tests for GET /programs/{program_id}."""

    def test_get_program_detail_success(self, client):
        response = client.get("/programs/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Program"
        assert len(data["days"]) == 2  # Day 1 and Day 2

    def test_get_program_detail_day_grouping(self, client):
        response = client.get("/programs/1")

        data = response.json()
        days = data["days"]

        # Day 1: Bench Press and Squat
        day1 = days[0]
        assert day1["day"] == 1
        assert len(day1["exercises"]) == 2
        exercise_names = [e["exercise_name"] for e in day1["exercises"]]
        assert "Bench Press" in exercise_names
        assert "Squat" in exercise_names

        # Day 2: Deadlift and Assisted Pull-up
        day2 = days[1]
        assert day2["day"] == 2
        assert len(day2["exercises"]) == 2
        exercise_names = [e["exercise_name"] for e in day2["exercises"]]
        assert "Deadlift" in exercise_names
        assert "Assisted Pull-up" in exercise_names

    def test_get_program_detail_exercise_fields(self, client):
        response = client.get("/programs/1")

        data = response.json()
        # Find the Bench Press exercise in Day 1
        day1 = data["days"][0]
        bench = next(e for e in day1["exercises"] if e["exercise_name"] == "Bench Press")

        assert bench["target_sets"] == 3
        assert bench["target_reps"] == 8
        assert bench["intensity"] == 75.0
        assert bench["optional"] is False
        assert bench["equipment_type"] == "BARBELL"

    def test_get_program_detail_optional_exercise(self, client):
        response = client.get("/programs/1")

        data = response.json()
        day2 = data["days"][1]
        pullup = next(e for e in day2["exercises"] if e["exercise_name"] == "Assisted Pull-up")

        assert pullup["optional"] is True

    def test_get_program_detail_not_found(self, client):
        response = client.get("/programs/999")

        assert response.status_code == 404


class TestGetExercises:
    """Integration tests for GET /exercises."""

    def test_get_exercises_returns_all(self, client):
        response = client.get("/exercises")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        names = [e["name"] for e in data]
        assert "Bench Press" in names
        assert "Squat" in names
        assert "Deadlift" in names
        assert "Assisted Pull-up" in names

    def test_get_exercises_fields(self, client):
        response = client.get("/exercises")

        data = response.json()
        exercise = data[0]
        assert "id" in exercise
        assert "name" in exercise
        assert "equipment_type" in exercise
        assert "weight_increment" in exercise

    def test_get_exercises_ordered_by_name(self, client):
        response = client.get("/exercises")

        data = response.json()
        names = [e["name"] for e in data]
        assert names == sorted(names)


class TestCreateExercise:
    """Integration tests for POST /exercises."""

    def test_create_exercise_success(self, client):
        response = client.post(
            "/exercises",
            json={
                "name": "Overhead Press",
                "equipment_type": "BARBELL",
                "weight_increment": 5.0,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Overhead Press"
        assert data["equipment_type"] == "BARBELL"
        assert data["weight_increment"] == 5.0
        assert "id" in data

    def test_create_exercise_duplicate_name_returns_409(self, client):
        response = client.post(
            "/exercises",
            json={
                "name": "Bench Press",
                "equipment_type": "BARBELL",
                "weight_increment": 5.0,
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_exercise_invalid_equipment_type(self, client):
        response = client.post(
            "/exercises",
            json={
                "name": "Some Exercise",
                "equipment_type": "INVALID",
                "weight_increment": 5.0,
            },
        )

        assert response.status_code == 422


class TestCreateProgram:
    """Integration tests for POST /programs."""

    def test_create_program_success(self, client):
        response = client.post(
            "/programs",
            json={
                "user_id": 1,
                "name": "New Program",
                "exercises": [
                    {
                        "exercise_id": 1,
                        "workout_day": 1,
                        "target_sets": 3,
                        "target_reps": 5,
                        "intensity": 82.5,
                    },
                    {
                        "exercise_id": 2,
                        "workout_day": 1,
                        "target_sets": 4,
                        "target_reps": 8,
                        "intensity": 70.0,
                        "optional": True,
                    },
                    {
                        "exercise_id": 3,
                        "workout_day": 2,
                        "target_sets": 3,
                        "target_reps": 3,
                        "intensity": 90.0,
                    },
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Program"
        assert len(data["days"]) == 2

    def test_create_program_response_matches_program_detail_structure(self, client):
        response = client.post(
            "/programs",
            json={
                "user_id": 1,
                "name": "Structured Program",
                "exercises": [
                    {
                        "exercise_id": 1,
                        "workout_day": 1,
                        "target_sets": 3,
                        "target_reps": 5,
                        "intensity": 82.5,
                    },
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Verify ProgramDetail structure
        assert "id" in data
        assert "name" in data
        assert "days" in data

        day = data["days"][0]
        assert "day" in day
        assert "exercises" in day

        exercise = day["exercises"][0]
        assert exercise["exercise_name"] == "Bench Press"
        assert exercise["target_sets"] == 3
        assert exercise["target_reps"] == 5
        assert exercise["intensity"] == 82.5
        assert exercise["optional"] is False
        assert "equipment_type" in exercise

    def test_create_program_with_optional_and_mandatory(self, client):
        response = client.post(
            "/programs",
            json={
                "user_id": 1,
                "name": "Mixed Program",
                "exercises": [
                    {
                        "exercise_id": 1,
                        "workout_day": 1,
                        "target_sets": 3,
                        "target_reps": 5,
                        "intensity": 80.0,
                        "optional": False,
                    },
                    {
                        "exercise_id": 4,
                        "workout_day": 1,
                        "target_sets": 3,
                        "target_reps": 10,
                        "intensity": 65.0,
                        "optional": True,
                    },
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        day1 = data["days"][0]
        assert len(day1["exercises"]) == 2

        exercises_by_name = {e["exercise_name"]: e for e in day1["exercises"]}
        assert exercises_by_name["Bench Press"]["optional"] is False
        assert exercises_by_name["Assisted Pull-up"]["optional"] is True


class TestDeleteProgram:
    """Integration tests for DELETE /programs/{program_id}."""

    def test_delete_program_success(self, client, seeded_db_with_logs):
        response = client.delete("/programs/1", params={"user_id": 1})

        assert response.status_code == 204

        # Program is gone
        assert client.get("/programs/1").status_code == 404

        # Exercise logs for this program are gone
        count = seeded_db_with_logs.connection.execute(
            "SELECT COUNT(*) FROM exercise_log"
        ).fetchone()[0]
        assert count == 0

        # Workout day exercises are gone
        count = seeded_db_with_logs.connection.execute(
            "SELECT COUNT(*) FROM workout_day_exercises"
        ).fetchone()[0]
        assert count == 0

    def test_delete_program_not_found(self, client):
        response = client.delete("/programs/999", params={"user_id": 1})

        assert response.status_code == 404

    def test_delete_program_wrong_user(self, client):
        response = client.delete("/programs/1", params={"user_id": 999})

        assert response.status_code == 403
        assert "do not own" in response.json()["detail"]


class TestUpdateProgramExercises:
    """Integration tests for PATCH /programs/{program_id}/exercises."""

    def test_update_program_exercises_success(self, client):
        response = client.patch(
            "/programs/1/exercises",
            json={
                "exercises": [
                    {"id": 1, "target_sets": 5, "target_reps": 5, "intensity": 80.0},
                    {"id": 2, "target_sets": 4, "target_reps": 6, "intensity": 77.5},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Program"

        day1 = data["days"][0]
        exercises_by_id = {e["id"]: e for e in day1["exercises"]}

        assert exercises_by_id[1]["target_sets"] == 5
        assert exercises_by_id[1]["target_reps"] == 5
        assert exercises_by_id[1]["intensity"] == 80.0

        assert exercises_by_id[2]["target_sets"] == 4
        assert exercises_by_id[2]["target_reps"] == 6
        assert exercises_by_id[2]["intensity"] == 77.5

    def test_update_program_exercises_does_not_affect_other_fields(self, client):
        response = client.patch(
            "/programs/1/exercises",
            json={
                "exercises": [
                    {"id": 1, "target_sets": 5, "target_reps": 5, "intensity": 80.0},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        day1 = data["days"][0]
        bench = next(e for e in day1["exercises"] if e["id"] == 1)

        assert bench["exercise_name"] == "Bench Press"
        assert bench["optional"] is False
        assert bench["equipment_type"] == "BARBELL"

    def test_update_program_exercises_not_found(self, client):
        response = client.patch(
            "/programs/999/exercises",
            json={
                "exercises": [
                    {"id": 1, "target_sets": 5, "target_reps": 5, "intensity": 80.0},
                ]
            },
        )

        assert response.status_code == 404


class TestCreateRecommendedProgram:
    """Integration tests for POST /programs/recommended."""

    def test_create_recommended_program_success(self, full_exercise_client):
        response = full_exercise_client.post(
            "/programs/recommended", params={"user_id": 1}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Stronger by Science Linear Progression - 5 Day Variant"
        assert len(data["days"]) == 5

    def test_create_recommended_program_exercise_count(self, full_exercise_client):
        response = full_exercise_client.post(
            "/programs/recommended", params={"user_id": 1}
        )

        data = response.json()
        total_exercises = sum(len(d["exercises"]) for d in data["days"])
        assert total_exercises == 28

    def test_create_recommended_program_day_structure(self, full_exercise_client):
        response = full_exercise_client.post(
            "/programs/recommended", params={"user_id": 1}
        )

        data = response.json()
        days = {d["day"]: d for d in data["days"]}

        # Day 1: 3 mandatory + 3 optional = 6
        assert len(days[1]["exercises"]) == 6
        # Day 2: 2 mandatory + 3 optional = 5
        assert len(days[2]["exercises"]) == 5
        # Day 3: 3 mandatory + 3 optional = 6
        assert len(days[3]["exercises"]) == 6
        # Day 4: 2 mandatory + 3 optional = 5
        assert len(days[4]["exercises"]) == 5
        # Day 5: 3 mandatory + 3 optional = 6
        assert len(days[5]["exercises"]) == 6

    def test_create_recommended_program_missing_exercises(self, client):
        # client fixture only has 4 exercises, not all 28
        response = client.post(
            "/programs/recommended", params={"user_id": 1}
        )

        assert response.status_code == 400
        assert "Missing exercises" in response.json()["detail"]


class TestUserWeight:
    """Integration tests for user weight endpoints."""

    def test_create_user_weight(self, client):
        response = client.post(
            "/user-weight",
            json={"user_id": 1, "weight": 185.5, "date": "2024-02-01"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["weight"] == 185.5
        assert data["date"] == "2024-02-01"
        assert "id" in data

    def test_get_user_weight_history(self, client):
        # Create two entries with different dates
        client.post(
            "/user-weight",
            json={"user_id": 1, "weight": 182.0, "date": "2024-03-01"},
        )
        client.post(
            "/user-weight",
            json={"user_id": 1, "weight": 184.0, "date": "2024-04-01"},
        )

        response = client.get("/user-weight", params={"user_id": 1})

        assert response.status_code == 200
        data = response.json()
        # Should include seeded entry (2024-01-01) plus the two new ones
        assert len(data) >= 3
        # Should be ordered by date descending
        dates = [entry["date"] for entry in data]
        assert dates == sorted(dates, reverse=True)

    def test_get_user_weight_history_empty(self, client):
        response = client.get("/user-weight", params={"user_id": 999})

        assert response.status_code == 200
        assert response.json() == []

    def test_delete_user_weight(self, client):
        # Create an entry to delete
        create_response = client.post(
            "/user-weight",
            json={"user_id": 1, "weight": 190.0, "date": "2024-05-01"},
        )
        weight_id = create_response.json()["id"]

        response = client.delete(f"/user-weight/{weight_id}")

        assert response.status_code == 204

    def test_delete_user_weight_not_found(self, client):
        response = client.delete("/user-weight/99999")

        assert response.status_code == 404
