import sqlite3
from typing import cast
from views.user import User
from views.user_one_rep_max_with_exercise import UserOneRepMaxWithExercise
from views.user_one_rep_maxes import UserOneRepMaxes
from views.workout_day_exercise import WorkoutDayExercise


class DB:
    connection: sqlite3.Connection

    def __init__(self):
        try:
            connection = sqlite3.connect("./data/workout.db")
            connection.row_factory = sqlite3.Row
        except Exception as e:
            raise Exception(f"Error connecting to DB: {e}")

        self.connection = connection

    def close(self):
        self.connection.close()
