from pydantic import BaseModel


class ExerciseHistoryEntry(BaseModel):
    date: str
    weight: float
    sets_completed: int | None
    target_sets: int
    reps_in_reserve: int | None
