import sqlite3
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from db.db import DB
from main import app, get_db


class TestDB(DB):
    """Test database using in-memory SQLite."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection


@pytest.fixture
def test_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Create an in-memory SQLite database with schema."""
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row

    # Create schema
    connection.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE user_weight (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            equipment_type TEXT NOT NULL,
            weight_increment REAL NOT NULL
        );

        CREATE TABLE workout_programs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE workout_day_exercises (
            id INTEGER PRIMARY KEY,
            workout_program_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            workout_day INTEGER NOT NULL,
            target_sets INTEGER NOT NULL,
            target_reps INTEGER NOT NULL,
            intensity REAL NOT NULL,
            optional INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (workout_program_id) REFERENCES workout_programs(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE user_one_rep_maxes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            one_rep_max REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE exercise_log (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            workout_day_exercise_id INTEGER NOT NULL,
            program_week INTEGER NOT NULL,
            weight REAL NOT NULL,
            sets_completed INTEGER,
            reps_in_reserve INTEGER,
            notes TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (workout_day_exercise_id) REFERENCES workout_day_exercises(id)
        );
    """)

    yield connection
    connection.close()


@pytest.fixture
def test_db(test_db_connection: sqlite3.Connection) -> Generator[TestDB, None, None]:
    """Create a TestDB instance."""
    db = TestDB(test_db_connection)
    yield db


@pytest.fixture
def seeded_db(test_db: TestDB) -> TestDB:
    """Database with sample test data."""
    conn = test_db.connection

    # Insert users
    conn.execute("INSERT INTO users (id, name) VALUES (1, 'Test User')")

    # Insert user weight
    conn.execute(
        "INSERT INTO user_weight (user_id, weight, date) VALUES (1, 180.0, '2024-01-01')"
    )

    # Insert exercises
    conn.executemany(
        "INSERT INTO exercises (id, name, equipment_type, weight_increment) VALUES (?, ?, ?, ?)",
        [
            (1, "Bench Press", "BARBELL", 5.0),
            (2, "Squat", "BARBELL", 5.0),
            (3, "Deadlift", "BARBELL", 5.0),
            (4, "Assisted Pull-up", "MACHINE", 5.0),
        ],
    )

    # Insert workout program
    conn.execute("INSERT INTO workout_programs (id, name) VALUES (1, 'Test Program')")

    # Insert workout day exercises
    conn.executemany(
        """INSERT INTO workout_day_exercises
           (id, workout_program_id, exercise_id, workout_day, target_sets, target_reps, intensity, optional)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (1, 1, 1, 1, 3, 8, 75.0, 0),  # Bench Press Day 1
            (2, 1, 2, 1, 3, 8, 80.0, 0),  # Squat Day 1
            (3, 1, 3, 2, 3, 5, 85.0, 0),  # Deadlift Day 2
            (4, 1, 4, 2, 3, 8, 70.0, 1),  # Assisted Pull-up Day 2 (optional)
        ],
    )

    # Insert user one rep maxes
    conn.executemany(
        "INSERT INTO user_one_rep_maxes (user_id, exercise_id, one_rep_max) VALUES (?, ?, ?)",
        [
            (1, 1, 200.0),  # Bench Press
            (1, 2, 300.0),  # Squat
            (1, 3, 400.0),  # Deadlift
            (1, 4, 50.0),  # Assisted Pull-up (assistance weight)
        ],
    )

    conn.commit()
    return test_db


@pytest.fixture
def seeded_db_with_logs(seeded_db: TestDB) -> TestDB:
    """Database with sample test data including exercise logs."""
    conn = seeded_db.connection

    # Insert exercise logs for week 1
    conn.executemany(
        """INSERT INTO exercise_log
           (id, user_id, workout_day_exercise_id, program_week, weight, sets_completed, reps_in_reserve, completed)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (1, 1, 1, 1, 150, 3, 2, 1),  # Bench Press - completed
            (2, 1, 2, 1, 240, 3, 1, 1),  # Squat - completed
            (3, 1, 3, 1, 340, 3, 2, 0),  # Deadlift - not completed
            (4, 1, 4, 1, 145, None, None, 0),  # Assisted Pull-up - not completed (optional)
        ],
    )

    conn.commit()
    return seeded_db


@pytest.fixture
def seeded_db_with_multi_week_logs(seeded_db_with_logs: TestDB) -> TestDB:
    """Database with exercise logs for week 1 AND week 2 to test weight_change."""
    conn = seeded_db_with_logs.connection

    # Insert exercise logs for week 2 with different weights
    conn.executemany(
        """INSERT INTO exercise_log
           (id, user_id, workout_day_exercise_id, program_week, weight, sets_completed, reps_in_reserve, completed)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (5, 1, 1, 2, 155, 3, 2, 0),  # Bench Press - weight +5
            (6, 1, 2, 2, 240, 3, 1, 0),  # Squat - weight same
            (7, 1, 3, 2, 335, 3, 2, 0),  # Deadlift - weight -5
            (8, 1, 4, 2, 145, None, None, 0),  # Assisted Pull-up - weight same
        ],
    )

    conn.commit()
    return seeded_db_with_logs


@pytest.fixture
def multi_week_client(seeded_db_with_multi_week_logs: TestDB) -> Generator[TestClient, None, None]:
    """FastAPI test client with multi-week database."""

    def override_get_db() -> Generator[TestDB, None, None]:
        try:
            yield seeded_db_with_multi_week_logs
            seeded_db_with_multi_week_logs.connection.commit()
        except sqlite3.Error:
            seeded_db_with_multi_week_logs.connection.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def client(seeded_db_with_logs: TestDB) -> Generator[TestClient, None, None]:
    """FastAPI test client with database dependency override."""

    def override_get_db() -> Generator[TestDB, None, None]:
        try:
            yield seeded_db_with_logs
            seeded_db_with_logs.connection.commit()
        except sqlite3.Error:
            seeded_db_with_logs.connection.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
