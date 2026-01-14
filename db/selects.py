from typing import cast
from db.db import DB
from views.one_rep_max_with_user_id_and_exercise_id import (
    CompleteDayCalcOneRepMaxView,
)
from views.user import User
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise
from views.user_one_rep_maxes import UserOneRepMaxes
from views.workout_day_exercise import WorkoutDayExercise
from views.get_current_week_view import ExerciseLogWithDay


def get_user(db: DB, username: str) -> User:
    statement = "SELECT * FROM users WHERE username = (?)"
    return cast(User, db.connection.execute(statement, (username,)).fetchone())


def get_latest_program_week_entry(db: DB, user_id: int, program_id: int) -> int:
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


def get_many_user_one_rep_maxes(
    db: DB, user_id: int, exercise_ids: list[int]
) -> list[UserOneRepMaxes]:
    if not exercise_ids:
        return []

    ids = ",".join("?" for _ in exercise_ids)
    statement = f"""
        SELECT *
        FROM user_one_rep_maxes
        WHERE user_id = (?) AND exercise_id IN ({ids})
    """
    params = [user_id, *ids]

    rows = db.connection.execute(statement, params).fetchall()
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


def get_complete_day_calc_one_rep_max_query_res(
    db: DB, user_id: int, exercise_log_ids: list[int]
) -> list[CompleteDayCalcOneRepMaxView]:
    if not exercise_log_ids:
        return []

    placeholders = ",".join("?" for _ in exercise_log_ids)

    statement = f"""
        SELECT t1.user_id, t2.exercise_id, t3.one_rep_max, t2.target_sets, t1.sets_completed, t1.reps_in_reserve, t2.workout_day, t2.workout_program_id, t2.id
        FROM exercise_log AS t1
        INNER JOIN workout_day_exercises AS t2
            ON t1.workout_day_exercise_id = t2.id
        INNER JOIN user_one_rep_maxes AS t3
            ON t1.user_id = t3.user_id
           AND t2.exercise_id = t3.exercise_id
        WHERE t3.user_id = ?
          AND t1.id IN ({placeholders});
    """

    params = [user_id, *exercise_log_ids]

    rows = db.connection.execute(statement, params).fetchall()
    return [CompleteDayCalcOneRepMaxView(row) for row in rows]


def get_number_of_days_in_program_week(db: DB, program_id: int):
    statement = """
        SELECT MAX(t1.workout_day)
        FROM workout_day_exercises AS t1
        INNER JOIN workout_programs AS t2 ON t1.workout_program_id = t2.id
        WHERE t1.workout_program_id = ?
    """
    params = (program_id,)
    return db.connection.execute(statement, params).fetchone()[0]


def get_user_program_exercise_logs_by_week(
    db: DB, user_id: int, program_id: int, week_num: int
) -> list[ExerciseLogWithDay]:
    statement = """
        SELECT t1.*, t2.workout_day
        FROM exercise_log AS t1
        INNER JOIN workout_day_exercises AS t2 ON t1.workout_day_exercise_id = t2.id
        WHERE t1.user_id = ? AND t2.workout_program_id = ? AND t1.program_week = ?
    """
    params = (user_id, program_id, week_num)
    rows = db.connection.execute(statement, params).fetchall()
    return [ExerciseLogWithDay(**dict(row)) for row in rows]
