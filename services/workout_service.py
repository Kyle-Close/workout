import logging
from dataclasses import dataclass
from typing import final
from fastapi import HTTPException
from db.db import DB
from helpers.Round import round_to_nearest
from repositories.exercise_log_repository import ExerciseLogRepository
from repositories.one_rep_max_repository import OneRepMaxRepository
from repositories.user_repository import UserRepository
from repositories.workout_program_repository import WorkoutProgramRepository
from views.exercise_log import ExerciseLog
from views.program_detail import ProgramDayExercise, ProgramDay, ProgramDetail
from views.program_summary import ProgramSummary

logger = logging.getLogger(__name__)


@dataclass
class UpdateLogsResult:
    logs_updated: int
    maxes_updated: list[int]
    generated_new_week: bool


@final
class WorkoutService:
    db: DB

    def __init__(self, db: DB) -> None:
        self.db = db
        self.exercise_log_repository = ExerciseLogRepository(db)
        self.workout_program_repository = WorkoutProgramRepository(db)
        self.one_rep_max_repository = OneRepMaxRepository(db)
        self.user_repository = UserRepository(db)

    def get_user_programs(self, user_id: int) -> list[ProgramSummary]:
        return self.workout_program_repository.get_user_programs(user_id)

    def update_program(self, program_id: int, name: str):
        return self.workout_program_repository.update_program(program_id, name)

    def delete_program(self, program_id: int, user_id: int) -> None:
        owner = self.workout_program_repository.get_program_owner(program_id)
        if owner is None:
            raise HTTPException(status_code=404, detail="Program not found")
        if owner != user_id:
            raise HTTPException(status_code=403, detail="You do not own this program")
        self.workout_program_repository.delete_program(program_id)

    def create_program(self, user_id: int, name: str, exercises: list[dict]) -> ProgramDetail:
        program_id = self.workout_program_repository.create_program(user_id, name)
        self.workout_program_repository.create_workout_day_exercises(program_id, exercises)
        return self.get_program_detail(program_id)

    def get_program_detail(self, program_id: int) -> ProgramDetail | None:
        rows = self.workout_program_repository.get_program_detail(program_id)
        if not rows:
            return None

        program_id_val = rows[0]["program_id"]
        program_name = rows[0]["program_name"]

        days_map: dict[int, list[ProgramDayExercise]] = {}
        for row in rows:
            day_num = row["workout_day"]
            exercise = ProgramDayExercise(
                exercise_name=row["exercise_name"],
                target_sets=row["target_sets"],
                target_reps=row["target_reps"],
                intensity=row["intensity"],
                optional=bool(row["optional"]),
                equipment_type=row["equipment_type"],
            )
            days_map.setdefault(day_num, []).append(exercise)

        days = [ProgramDay(day=day_num, exercises=exercises) for day_num, exercises in sorted(days_map.items())]

        return ProgramDetail(id=program_id_val, name=program_name, days=days)

    def get_latest_program_week_entry(self, user_id: int, workout_program_id: int):
        return self.workout_program_repository.get_latest_program_week_entry(user_id, workout_program_id)

    def update_exercise_logs(self, logs: list[ExerciseLog]):
        try:
            self.exercise_log_repository.update_many_exercise_logs(logs)
        except Exception as e:
            logger.error(f"Failed to update logs: {e}")
            raise HTTPException(status_code=500, detail="Failed to update exercise logs") from e

    def populate_exercise_logs_week(self, user_id: int, program_id: int) -> None:
        workout_day_entries = self.workout_program_repository.get_program_workout_days_exercise_data(program_id)
        one_rep_maxes_with_exercise = self.one_rep_max_repository.get_user_one_rep_maxes_with_exercise_data(user_id)
        new_week_num = self.workout_program_repository.get_latest_program_week_entry(user_id, program_id) + 1

        for entry in workout_day_entries:
            exercise_data = next(
                (e for e in one_rep_maxes_with_exercise if e.exercise_id == entry.exercise_id),
                None,
            )

            if exercise_data is None:
                raise ValueError(
                    f"Could not find exercise data for workout day entry (exercise_id={entry.exercise_id})"
                )

            one_rep_max = exercise_data.current_one_rep_max
            weight_increment = exercise_data.weight_increment
            intensity = entry.intensity / 100

            if self._is_assisted_exercise(entry.exercise_name):
                current_body_weight = self.user_repository.get_user_recent_weight(user_id)
                if current_body_weight is None:
                    raise ValueError(f"No weight recorded for user (user_id={user_id})")
                weight = round_to_nearest(current_body_weight - (one_rep_max * intensity), weight_increment)
            else:
                weight = round_to_nearest(one_rep_max * intensity, weight_increment)

            self.exercise_log_repository.create_exercise_log_entry(user_id, entry.id, new_week_num, weight)

    def _is_assisted_exercise(self, exercise_name: str) -> bool:
        return "assisted" in exercise_name.lower()

    def check_is_week_complete(self, user_id: int, program_id: int, week_num: int) -> bool:
        incomplete_count = self.exercise_log_repository.get_count_of_incomplete_mandatory_logs_by_week(
            user_id, program_id, week_num
        )
        return incomplete_count == 0

    def process_log_updates(self, logs: list[ExerciseLog], one_rep_max_service) -> UpdateLogsResult:
        """
        Orchestrates the full log update workflow:
        1. Update exercise logs with payload data
        2. Update user 1 rep maxes based on the updated logs
        3. Generate a new week of logs if current week is complete
        """
        from services.exercise_log_service import ExerciseLogService

        self.update_exercise_logs(logs)

        one_rep_max_updates = one_rep_max_service.update_maxes_from_completed_logs(logs)

        exercise_log_service = ExerciseLogService(self.db)
        first_log_detailed = exercise_log_service.get_detailed_log_info([logs[0].id])
        details = first_log_detailed[0]

        latest_week = self.get_latest_program_week_entry(details.user_id, details.workout_program_id)
        should_populate_new_week = self.check_is_week_complete(details.user_id, details.workout_program_id, latest_week)

        if should_populate_new_week:
            self.populate_exercise_logs_week(details.user_id, details.workout_program_id)

        return UpdateLogsResult(
            logs_updated=len(logs),
            maxes_updated=one_rep_max_updates,
            generated_new_week=should_populate_new_week,
        )
