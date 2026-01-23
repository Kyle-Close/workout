import pytest

from services.one_rep_max_service import OneRepMaxAdjustment, OneRepMaxService


class TestOneRepMaxServiceCalculation:
    """Tests for OneRepMaxService.calculate_new_one_rep_max."""

    @pytest.fixture
    def service(self, seeded_db):
        return OneRepMaxService(seeded_db)

    def test_missed_one_set(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=-1, reps_in_reserve=0
        )

        expected = 100.0 * (1 + OneRepMaxAdjustment.MISSED_ONE_SET)
        assert new_max == expected
        assert new_max == 98.0  # -2%

    def test_missed_multiple_sets(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=-2, reps_in_reserve=0
        )

        expected = 100.0 * (1 + OneRepMaxAdjustment.MISSED_MULTIPLE_SETS)
        assert new_max == expected
        assert new_max == 95.0  # -5%

    def test_missed_three_sets(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=-3, reps_in_reserve=0
        )

        assert new_max == 95.0  # Same as -2, still -5%

    def test_one_rir(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=0, reps_in_reserve=1
        )

        expected = 100.0 * (1 + OneRepMaxAdjustment.ONE_RIR)
        assert new_max == expected
        assert new_max == 101.0  # +1%

    def test_two_rir(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=0, reps_in_reserve=2
        )

        expected = 100.0 * (1 + OneRepMaxAdjustment.TWO_RIR)
        assert new_max == expected
        assert new_max == 103.0  # +3%

    def test_three_plus_rir(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=0, reps_in_reserve=3
        )

        expected = 100.0 * (1 + OneRepMaxAdjustment.THREE_PLUS_RIR)
        assert new_max == expected
        assert new_max == 105.0  # +5%

    def test_high_rir(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=0, reps_in_reserve=5
        )

        assert new_max == 105.0  # Still +5% for 3+ RIR

    def test_zero_rir_zero_delta(self, service):
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=0, reps_in_reserve=0
        )

        assert new_max == 100.0  # No change

    def test_positive_set_delta_with_rir(self, service):
        # Extra sets completed but still checking RIR
        new_max = service.calculate_new_one_rep_max(
            old_max=100.0, set_delta=1, reps_in_reserve=2
        )

        assert new_max == 103.0  # +3% from 2 RIR


class TestOneRepMaxServiceUpdateFromLogs:
    """Tests for OneRepMaxService.update_maxes_from_completed_logs."""

    def test_update_maxes_empty_logs(self, seeded_db):
        service = OneRepMaxService(seeded_db)
        updates = service.update_maxes_from_completed_logs([])

        assert updates == []
