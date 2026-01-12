from typing import override


class UserOneRepMaxWithExercise:
    exercise_id: int
    name: str
    weight_increment: float
    one_rep_max: float

    def __init__(self, cursorResult: tuple[int, int, int, float, int, str, str, float]):
        self.exercise_id = cursorResult[2]
        self.name = cursorResult[5]
        self.weight_increment = cursorResult[7]
        self.one_rep_max = cursorResult[3]

    @override
    def __str__(self) -> str:
        return (
            f"exercise id: {self.exercise_id}\n"
            f"name: {self.name}\n"
            f"weight increment: {self.weight_increment}\n"
            f"one rep max: {self.one_rep_max}\n"
        )
