from datetime import date, timedelta

from auth.auth import hash_password
from db.db import DB
from repositories.exercise_repository import ExerciseRepository
from services.workout_service import WorkoutService

DEMO_USERNAME = "demo"

# 1RM values by exercise name (lbs)
_ONE_REP_MAXES = {
    "Bench Press": 155,
    "Squat": 170,
    "Deadlift": 200,
    "Overhead Press": 90,
    "Romanian Deadlift": 190,
    "Close Grip Bench Press": 100,
    "DB Bench Press": 65,
    "Incline Bench Press": 50,
    "Leg Press": 380,
    "T-Bar Rows": 60,
    "Lat Pull-Downs": 150,
    "Assisted Pull-Ups": 170,
    "Bulgarian Split Squat": 70,
    "Seated Machine Row": 150,
    "Hanging Leg Raises": 0,
    "Seated Leg Curl": 110,
    "Reverse Pec Deck": 70,
    "Cable Tricep Pushdown": 85,
    "Seated Cable Row": 145,
    "Face Pulls": 55,
    "Hammer Curls": 45,
    "Lateral Raises": 30,
    "Calf Raises": 260,
    "Plank": 0,
    "Hip Thrusts": 240,
    "Neutral-Grip Pulldown": 130,
    "DB Curls": 35,
    "Front Squat": 170,
}


class DemoService:
    def __init__(self, db: DB):
        self.db = db
        self.conn = db.connection

    def reset_and_seed(self) -> tuple[int, str]:
        """Reset demo user data and seed fresh demo state. Returns (user_id, username)."""
        user_id = self._get_or_create_demo_user()
        self._wipe_user_data(user_id)
        self._seed_user_weight(user_id)
        self._seed_one_rep_maxes(user_id)

        workout_service = WorkoutService(self.db)
        program = workout_service.create_recommended_program(user_id)
        program_id = program.id

        today = date.today()

        # Week 1: complete all 5 days, optionals on days 1, 3, 5
        workout_service.populate_exercise_logs_week(user_id, program_id)
        self._complete_week_logs(
            user_id, program_id, week=1,
            complete_days={1, 2, 3, 4, 5},
            optional_days={1, 3, 5},
            start_date=today - timedelta(days=35),
        )
        self._bump_one_rep_maxes(user_id, factor=1.02)

        # Week 2: complete all 5 days, optionals on days 2, 4
        workout_service.populate_exercise_logs_week(user_id, program_id)
        self._complete_week_logs(
            user_id, program_id, week=2,
            complete_days={1, 2, 3, 4, 5},
            optional_days={2, 4},
            start_date=today - timedelta(days=28),
        )
        self._bump_one_rep_maxes(user_id, factor=1.02)

        # Week 3: complete all 5 days, optionals on days 1, 3, 5
        workout_service.populate_exercise_logs_week(user_id, program_id)
        self._complete_week_logs(
            user_id, program_id, week=3,
            complete_days={1, 2, 3, 4, 5},
            optional_days={1, 3, 5},
            start_date=today - timedelta(days=21),
        )
        self._bump_one_rep_maxes(user_id, factor=1.02)

        # Week 4: complete all 5 days, optionals on days 1, 2, 4
        workout_service.populate_exercise_logs_week(user_id, program_id)
        self._complete_week_logs(
            user_id, program_id, week=4,
            complete_days={1, 2, 3, 4, 5},
            optional_days={1, 2, 4},
            start_date=today - timedelta(days=14),
        )
        self._bump_one_rep_maxes(user_id, factor=1.02)

        # Week 5: in progress — complete days 1-3, optionals on day 1
        workout_service.populate_exercise_logs_week(user_id, program_id)
        self._complete_week_logs(
            user_id, program_id, week=5,
            complete_days={1, 2, 3},
            optional_days={1},
            start_date=today - timedelta(days=5),
        )

        return user_id, DEMO_USERNAME

    def _get_or_create_demo_user(self) -> int:
        row = self.conn.execute(
            "SELECT id FROM users WHERE username = ?", (DEMO_USERNAME,)
        ).fetchone()
        if row:
            return row[0]

        pw_hash = hash_password("demo")
        cursor = self.conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (DEMO_USERNAME, pw_hash, "demo"),
        )
        return cursor.lastrowid

    def _wipe_user_data(self, user_id: int):
        self.conn.execute(
            "DELETE FROM exercise_log WHERE user_id = ?", (user_id,)
        )
        self.conn.execute("""
            DELETE FROM workout_day_exercises WHERE workout_program_id IN (
                SELECT id FROM workout_programs WHERE user_id = ?
            )
        """, (user_id,))
        self.conn.execute(
            "DELETE FROM workout_programs WHERE user_id = ?", (user_id,)
        )
        self.conn.execute(
            "DELETE FROM user_one_rep_maxes WHERE user_id = ?", (user_id,)
        )
        self.conn.execute(
            "DELETE FROM user_weight WHERE user_id = ?", (user_id,)
        )

    def _seed_user_weight(self, user_id: int):
        today = date.today()
        weights = [
            (user_id, 196.0, (today - timedelta(days=60)).isoformat()),
            (user_id, 194.5, (today - timedelta(days=49)).isoformat()),
            (user_id, 193.0, (today - timedelta(days=38)).isoformat()),
            (user_id, 192.0, (today - timedelta(days=28)).isoformat()),
            (user_id, 191.0, (today - timedelta(days=21)).isoformat()),
            (user_id, 190.0, (today - timedelta(days=14)).isoformat()),
            (user_id, 189.0, (today - timedelta(days=7)).isoformat()),
            (user_id, 188.5, today.isoformat()),
        ]
        self.conn.executemany(
            "INSERT INTO user_weight (user_id, weight, date) VALUES (?, ?, ?)",
            weights,
        )

    def _seed_one_rep_maxes(self, user_id: int):
        exercise_repo = ExerciseRepository(self.db)
        id_map = exercise_repo.get_id_map_by_name(list(_ONE_REP_MAXES.keys()))

        entries = []
        for name, max_val in _ONE_REP_MAXES.items():
            exercise_id = id_map.get(name)
            if exercise_id is not None:
                entries.append((user_id, exercise_id, max_val, max_val))

        self.conn.executemany(
            "INSERT INTO user_one_rep_maxes (user_id, exercise_id, original_one_rep_max, current_one_rep_max) VALUES (?, ?, ?, ?)",
            entries,
        )

    def _complete_week_logs(
        self,
        user_id: int,
        program_id: int,
        week: int,
        complete_days: set[int],
        optional_days: set[int],
        start_date: date,
    ):
        rows = self.conn.execute("""
            SELECT el.id, wde.workout_day, wde.optional, wde.target_sets
            FROM exercise_log el
            JOIN workout_day_exercises wde ON el.workout_day_exercise_id = wde.id
            WHERE el.user_id = ? AND wde.workout_program_id = ? AND el.program_week = ?
        """, (user_id, program_id, week)).fetchall()

        rir_cycle = [1, 2, 2, 3, 2, 1, 3, 2]
        i = 0

        for row in rows:
            log_id, day, is_optional, target_sets = row[0], row[1], bool(row[2]), row[3]

            if day not in complete_days:
                continue
            if is_optional and day not in optional_days:
                continue

            rir = rir_cycle[i % len(rir_cycle)]
            completed_at = (start_date + timedelta(days=day - 1)).isoformat()
            i += 1

            self.conn.execute("""
                UPDATE exercise_log
                SET sets_completed = ?, reps_in_reserve = ?, completed = 1, completed_at = ?
                WHERE id = ?
            """, (target_sets, rir, completed_at, log_id))

    def _bump_one_rep_maxes(self, user_id: int, factor: float):
        self.conn.execute("""
            UPDATE user_one_rep_maxes
            SET current_one_rep_max = ROUND(current_one_rep_max * ?, 1)
            WHERE user_id = ?
        """, (factor, user_id))
