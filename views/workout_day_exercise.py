from typing import override


class WorkoutDayExercise:
    id: int
    exercise_id: int
    program_id: int
    workout_day: int
    target_sets: int
    target_reps: int
    intensity: float

    def __init__(self, cursorResult: tuple[int, int, int, int, int, int, float]):
        self.id = cursorResult[0]
        self.exercise_id = cursorResult[1]
        self.program_id = cursorResult[2]
        self.workout_day = cursorResult[3]
        self.target_sets = cursorResult[4]
        self.target_reps = cursorResult[5]
        self.intensity = cursorResult[6]

    @override
    def __str__(self) -> str:
        return (
            f"id: {self.id}\n"
            f"exercise id: {self.exercise_id}\n"
            f"program id: {self.program_id}\n"
            f"workout day: {self.workout_day}\n"
            f"target sets: {self.target_sets}\n"
            f"target reps: {self.target_reps}\n"
            f"intensity: {self.intensity}\n"
        )
