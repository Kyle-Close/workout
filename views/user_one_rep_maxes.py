from typing import override


class UserOneRepMaxes:
    id: int
    user_id: int
    exercise_id: int
    one_rep_max: float

    def __init__(self, cursorResult: tuple[int, int, int, float]):
        self.id = cursorResult[0]
        self.user_id = cursorResult[1]
        self.exercise_id = cursorResult[2]
        self.one_rep_max = cursorResult[3]

    @override
    def __str__(self):
        return (
            f"id: {self.id}\n"
            f"user id: {self.user_id}\n"
            f"exercise id: {self.exercise_id}\n"
            f"one rep max: {self.one_rep_max}\n"
        )
