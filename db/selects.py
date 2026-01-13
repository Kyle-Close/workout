from typing import cast
from db.db import DB
from views.user import User
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise
from views.user_one_rep_maxes import UserOneRepMaxes
from views.workout_day_exercise import WorkoutDayExercise


def get_user(db: DB, username: str) -> User:
    statement = "SELECT * FROM users WHERE username = (?)"
    return cast(User, db.connection.execute(statement, (username,)).fetchone())


def latest_program_week_entry(db: DB, user_id: int, program_id: int) -> int:
    statement = """
        SELECT MAX(program_week) AS largest_program_week
        FROM exercise_log AS t1
        INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
        WHERE t1.user_id = (?) AND t2.workout_program_id = (?)
    """
    value = db.connection.execute(statement, (user_id, program_id)).fetchone()[0]
    return value if value is not None else 0


def get_user_one_rep_maxes_with_exercise_data(
    db: DB, user_id: int
) -> list[UserOneRepMaxWithExercise]:
    statement = """
        SELECT *
        FROM user_one_rep_maxes AS t1
        INNER JOIN exercises AS t2 ON t1.exercise_id = t2.id
        WHERE t1.user_id = (?)
    """
    rows = cast(
        list[tuple[int, int, int, float, int, str, str, float]],
        db.connection.execute(statement, (user_id,)).fetchall(),
    )
    return [UserOneRepMaxWithExercise(row) for row in rows]


def get_user_one_rep_maxes(db: DB, user_id: int) -> list[UserOneRepMaxes]:
    statement = """
        SELECT t1.name
        FROM user_one_rep_maxes
        WHERE user_id = (?)
    """
    rows = db.connection.execute(statement, (user_id,)).fetchall()
    return [UserOneRepMaxes(row) for row in rows]


def get_program_workout_days_excercises_data(db: DB, program_id: int):
    statement = """
        SELECT t1.id, t1.exercise_id, t1.workout_program_id, t1.workout_day, t1.target_sets, t1.target_reps, t1.intensity
        FROM workout_day_exercises AS t1
        INNER JOIN workout_programs as t2 ON t1.workout_program_id = t2.id
        WHERE t1.workout_program_id = (?)
    """
    rows = db.connection.execute(statement, (program_id,)).fetchall()
    return [WorkoutDayExercise(row) for row in rows]
