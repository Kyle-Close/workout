from dataclasses import dataclass
from typing import final
from db.db import DB
from repositories.one_rep_max_repository import OneRepMaxRepository
from repositories.progression_repository import ProgressionRepository
from views.exercise_log import ExerciseLog


@final
class OneRepMaxAdjustment:
    """Progressive overload adjustments based on performance."""

    MISSED_ONE_SET = -0.02
    MISSED_MULTIPLE_SETS = -0.05
    ONE_RIR = 0.01
    TWO_RIR = 0.03
    THREE_PLUS_RIR = 0.05


@dataclass
class OneRepMaxUpdate:
    """Represents a calculated 1RM update."""

    user_id: int
    exercise_id: int
    old_max: float
    new_max: float
    exercise_name: str
    set_delta: int
    reps_in_reserve: int


class OneRepMaxService:
    """Service for calculating and updating one rep maxes based on workout performance."""

    def __init__(self, db: DB):
        self.db = db
        self.progression_repository = ProgressionRepository(db)
        self.one_rep_max_repository = OneRepMaxRepository(db)

    def update_maxes_from_completed_logs(
        self, completed_logs: list[ExerciseLog]
    ) -> list[OneRepMaxUpdate]:
        """
        Calculate and update one rep maxes for completed exercise logs.

        Args:
            completed_logs: List of exercise logs that were just completed

        Returns:
            List of OneRepMaxUpdate objects showing what changed
        """
        if not completed_logs:
            return []

        # Step 1: Fetch all data in single query
        user_id = completed_logs[0].user_id
        log_ids = [log.id for log in completed_logs]

        exercise_data = (
            self.progression_repository.get_exercise_data_for_updating_maxes(
                user_id, log_ids
            )
        )

        # Step 2: Build lookup table
        log_lookup = {log.workout_day_exercise_id: log for log in completed_logs}

        # Step 3: Calculate all updates
        updates = []
        for data in exercise_data:
            log = log_lookup.get(data.workout_day_exercise_id)

            if not log or log.sets_completed is None or log.reps_in_reserve is None:
                continue

            # Calculate new max
            set_delta = log.sets_completed - data.target_sets
            new_max = self.calculate_new_one_rep_max(
                data.one_rep_max, set_delta, log.reps_in_reserve
            )

            # Track the update
            updates.append(
                OneRepMaxUpdate(
                    user_id=data.user_id,
                    exercise_id=data.exercise_id,
                    old_max=data.one_rep_max,
                    new_max=new_max,
                    exercise_name=data.exercise_name,
                    set_delta=set_delta,
                    reps_in_reserve=log.reps_in_reserve,
                )
            )

        # Step 4: Apply all updates to database
        self._apply_updates(updates)

        return updates

    def _apply_updates(self, updates: list[OneRepMaxUpdate]) -> None:
        """Apply one rep max updates to the database."""
        for update in updates:
            self.one_rep_max_repository.update_one_rep_max(
                update.user_id, update.exercise_id, update.new_max
            )

    def calculate_new_one_rep_max(self, old_max: float, set_delta: int, rip: int):
        """
        Calculate adjusted 1RM based on performance.

        Args:
            current: Current one rep max
            set_delta: Sets completed vs target (negative = missed sets)
            rir: Reps in reserve on final set
        """
        adjustment = OneRepMaxAdjustment

        if set_delta == -1:
            percent_to_add = adjustment.MISSED_ONE_SET
        elif set_delta < -1:
            percent_to_add = adjustment.MISSED_MULTIPLE_SETS
        elif rip == 1:
            percent_to_add = adjustment.ONE_RIR
        elif rip == 2:
            percent_to_add = adjustment.TWO_RIR
        elif rip > 2:
            percent_to_add = adjustment.THREE_PLUS_RIR
        else:
            percent_to_add = 0

        return old_max * (1 + percent_to_add)
