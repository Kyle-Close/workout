import pytest

from helpers.Round import round_to_nearest


class TestRoundToNearest:
    """Tests for the round_to_nearest helper function.

    Note: Python's round() uses "round half to even" (banker's rounding),
    so 152.5 rounds to 152 (even), not 155.
    """

    def test_round_to_nearest_5_rounds_up(self):
        # 153 / 5 = 30.6, rounds to 31 * 5 = 155
        assert round_to_nearest(153, 5) == 155

    def test_round_to_nearest_5_rounds_down(self):
        assert round_to_nearest(152.4, 5) == 150

    def test_round_to_nearest_5_exact(self):
        assert round_to_nearest(150.0, 5) == 150

    def test_round_to_nearest_5_banker_rounding(self):
        # 152.5 / 5 = 30.5, banker's rounding -> 30 (even) * 5 = 150
        assert round_to_nearest(152.5, 5) == 150
        # 157.5 / 5 = 31.5, banker's rounding -> 32 (even) * 5 = 160
        assert round_to_nearest(157.5, 5) == 160

    def test_round_to_nearest_2_5(self):
        # 152.5 / 2.5 = 61, 61 * 2.5 = 152.5
        assert round_to_nearest(152.5, 2.5) == 152.5
        # 155 / 2.5 = 62, 62 * 2.5 = 155
        assert round_to_nearest(155, 2.5) == 155

    def test_round_to_nearest_1(self):
        assert round_to_nearest(152.6, 1) == 153

    def test_round_to_nearest_10(self):
        assert round_to_nearest(155, 10) == 160

    def test_round_to_nearest_zero_value(self):
        assert round_to_nearest(0, 5) == 0

    def test_round_to_nearest_negative_value(self):
        # -12.5 / 5 = -2.5, banker's rounding -> -2 (even) * 5 = -10
        assert round_to_nearest(-12.5, 5) == -10
        # -17.5 / 5 = -3.5, banker's rounding -> -4 (even) * 5 = -20
        assert round_to_nearest(-17.5, 5) == -20

    def test_round_to_nearest_small_unit(self):
        # 10.3 / 0.5 = 20.6, rounds to 21 * 0.5 = 10.5
        assert round_to_nearest(10.3, 0.5) == 10.5
        # 11 / 0.5 = 22, 22 * 0.5 = 11
        assert round_to_nearest(11, 0.5) == 11

    @pytest.mark.parametrize(
        "value,unit,expected",
        [
            (100, 5, 100),
            (101, 5, 100),
            (102, 5, 100),
            (103, 5, 105),
            (104, 5, 105),
            (105, 5, 105),
        ],
    )
    def test_round_to_nearest_parametrized(self, value, unit, expected):
        assert round_to_nearest(value, unit) == expected
