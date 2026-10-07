from fractions import Fraction

import pytest

from slot import build_columns, build_columns_max_rule, evaluate, payout, simulate

def test_single_square():
    grid = [[3, 3, 0],
            [3, 3, 1],
            [0, 1, 4]]
    assert payout(grid) == 3  # pattern 4.1 with symbol 3

def test_no_win():
    grid = [[0, 1, 2],
            [3, 4, 0],
            [1, 2, 3]]
    assert payout(grid) == 0

def test_two_squares_add_up():
    grid = [[2, 2, 0],
            [2, 2, 2],
            [1, 2, 2]]
    assert payout(grid) == 2  # 4.1 + 4.4, each 1x

def test_full_grid_also_pays_its_squares():
    grid = [[4] * 3 for _ in range(3)]
    assert payout(grid) == 4 * 5 + 5 * 5  # four squares + full grid 5x

def test_evaluate_trivial_machine():
    # every column is all 0s -> every spin is a full grid of 0s
    rtp, win_rate = evaluate([[0], [0], [0]])
    assert rtp == 9 * Fraction(1, 4)
    assert win_rate == 1

def test_design_meets_requirements():
    rtp, win_rate = evaluate(build_columns())
    assert rtp == Fraction(95, 100)
    assert win_rate >= Fraction(55, 100)

def test_too_many_pairs_is_rejected():
    with pytest.raises(ValueError):
        build_columns(pairs=30, length=80)  # 30 pairs need 90 symbols

def test_biggest_win_only_rule_pays_the_largest_pattern():
    grid = [[4] * 3 for _ in range(3)]
    assert payout(grid, rule="max") == 5 * 5  # only the full grid, not its squares

def test_max_rule_design_meets_requirements():
    rtp, win_rate = evaluate(build_columns_max_rule(), rule="max")
    assert rtp == Fraction(95, 100)
    assert win_rate == Fraction(17, 20)

def test_unknown_rule_is_rejected():
    with pytest.raises(ValueError):
        payout([[4] * 3 for _ in range(3)], rule="Sum")  # typo must not silently mean "max"

def test_simulate_follows_the_rule():
    # every spin is a full grid of 0s; only the biggest win pays: 5 * 0.25
    rtp, win_rate = simulate([[0], [0], [0]], spins=10, rule="max")
    assert rtp == 1.25
    assert win_rate == 1
