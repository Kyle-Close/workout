from typing import override


class CompleteDayCalcOneRepMaxView:
    user_id: int
    exercise_id: int
    one_rep_max: float
    target_sets: int
    sets_completed: int
    reps_in_reserve: int
    workout_day: int
    workout_program_id: int
    workout_day_exercise_id: int

    def __init__(self, cursorResult: tuple[int, int, float, int, int, int, int, int, int]):
        self.user_id = cursorResult[0]
        self.exercise_id = cursorResult[1]
        self.one_rep_max = cursorResult[2]
        self.target_sets = cursorResult[3]
        self.sets_completed = cursorResult[4]
        self.reps_in_reserve = cursorResult[5]
        self.workout_day = cursorResult[6]
        self.workout_program_id = cursorResult[7]
        self.workout_day_exercise_id = cursorResult[8]
        

    @override
    def __str__(self) -> str:
        return (
            f"user id: {self.user_id}\n"
            f"exercise id: {self.exercise_id}\n"
            f"one rep max: {self.one_rep_max}\n"
            f"target sets: {self.target_sets}\n"
            f"sets completed: {self.sets_completed}\n"
            f"reps in reserve: {self.reps_in_reserve}\n"
        )
