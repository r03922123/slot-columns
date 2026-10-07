"""
A tiny slot machine designer, with an exact checker.

The game in one paragraph:
    There are 3 columns. Behind each column is a long list of symbols that wraps around.
    A spin picks a uniformly random stop on every column independently, and each
    column shows the 3 consecutive symbols starting at that stop. Then we look
    for 5 patterns on the 3x3 grid (four 2x2 squares + the full 3x3), and pay
    bet * multiplier for each square, and bet * multiplier * 5 for the full grid.

The design trick (the whole idea, really):
    Make the MIDDLE column all 2s. Every pattern touches the middle column, so now
    only symbol 2 (multiplier 1) can ever pay, and a 2x2 square hits exactly when
    the side column shows "2, 2" in those two rows. Put the 2s on the side columns
    as separated pairs (never three in a row), and it becomes counting:

        possible spins             = 80 * 3 * 80        = 19,200
        spins where a square wins  = 19 * 3 * 80        = 4,560
        RTP                        = 4 * 4,560 / 19,200 = 0.95    (exact)
        losing spins               = 42 * 3 * 42        = 5,292
        win rate                   = 1 - 5,292 / 19,200 = 0.724   (>= 0.55)

    We don't trust the arithmetic, though: evaluate() counts every possible
    spin with exact fractions and checks it.

See intuition.md (why it works) and method.md (how the code is built).

Run:  uv run slot.py
"""

import random
from collections import Counter
from fractions import Fraction

# symbol -> multiplier, as exact fractions so RTP comes out exact (no float fuzz)
MULT = {0: Fraction(1, 4), 1: Fraction(11, 20), 2: Fraction(1), 3: Fraction(3), 4: Fraction(5)}

# each pattern = the (row, col) cells that must all hold the same symbol
SQUARES = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # 4.1 top-left
    [(0, 1), (0, 2), (1, 1), (1, 2)],  # 4.2 top-right
    [(1, 0), (1, 1), (2, 0), (2, 1)],  # 4.3 bottom-left
    [(1, 1), (1, 2), (2, 1), (2, 2)],  # 4.4 bottom-right
]
FULL = [(r, c) for r in range(3) for c in range(3)]  # 4.5, pays 5x

# -----------------------------------------------------------------------------
# the game

def window(column, stop):
    """The 3 symbols a column shows when it lands on `stop` (it wraps around)."""
    return tuple(column[(stop + r) % len(column)] for r in range(3))

def same_symbol(grid, cells):
    """The symbol if all cells match, else None."""
    syms = {grid[r][c] for r, c in cells}
    return syms.pop() if len(syms) == 1 else None

def payout(grid):
    """Payout per 1 unit of bet for a 3x3 grid (grid[row][col]). Wins add up."""
    total = Fraction(0)
    for cells in SQUARES:
        s = same_symbol(grid, cells)
        if s is not None:
            total += MULT[s]
    s = same_symbol(grid, FULL)
    if s is not None:
        total += 5 * MULT[s]
    return total

# -----------------------------------------------------------------------------
# exact evaluation: enumerate every spin

def evaluate(columns):
    """
    Exact (RTP, win_rate) as Fractions, counted over every possible spin.
    Many stops show the same 3 symbols, so instead of trying every stop we count
    each distinct view once and weight it by how many stops show it.
    """
    views = [Counter(window(column, s) for s in range(len(column))) for column in columns]
    total_spins = len(columns[0]) * len(columns[1]) * len(columns[2])
    paid, wins = Fraction(0), 0
    for a, na in views[0].items():
        for b, nb in views[1].items():
            for c, nc in views[2].items():
                n = na * nb * nc  # how many spins show this grid
                p = payout([[a[r], b[r], c[r]] for r in range(3)])
                paid += n * p
                wins += n if p > 0 else 0
    return paid / total_spins, Fraction(wins, total_spins)

def simulate(columns, spins=200_000, seed=1337):
    """Random check: actually spin the machine many times and count."""
    rng = random.Random(seed)
    paid, wins = 0.0, 0
    for _ in range(spins):
        cols = [window(column, rng.randrange(len(column))) for column in columns]
        p = float(payout([[cols[0][r], cols[1][r], cols[2][r]] for r in range(3)]))
        paid += p
        wins += p > 0
    return paid / spins, wins / spins

# -----------------------------------------------------------------------------
# the design

def build_columns(pairs=19, length=80):
    """
    Left and right columns: `pairs` separated (2, 2) pairs in a list of `length`,
    padded with filler. Middle column: all 2s.
    Filler symbols (0, 1, 3, 4) can never pay, because the middle column is all 2s.
    """
    if 3 * pairs > length:
        raise ValueError(f"{pairs} pairs need {3 * pairs} symbols (2, 2, separator each), but length is {length}")
    filler = [0, 1, 3, 4]
    side = []
    for i in range(pairs):
        side += [2, 2, filler[i % 4]]  # the filler after each pair keeps pairs separated
    side += [filler[i % 4] for i in range(length - len(side))]
    middle = [2, 2, 2]
    return [side, middle, side]

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    columns = build_columns()
    for i, column in enumerate(columns):
        print(f"column {i} (len {len(column)}): {column}")

    rtp, win_rate = evaluate(columns)
    print(f"\nexact   RTP      = {rtp} = {float(rtp):.6f}  (bet 100 -> expect {float(rtp * 100):g} back)")
    print(f"exact   win rate = {win_rate} = {float(win_rate):.6f}")

    sim_rtp, sim_win = simulate(columns)
    print(f"sim     RTP      = {sim_rtp:.4f}, win rate = {sim_win:.4f}  (200k spins)")

    if rtp != Fraction(95, 100):
        raise SystemExit("FAILED: RTP must be exactly 0.95")
    if win_rate < Fraction(55, 100):
        raise SystemExit("FAILED: win rate must be >= 55%")
    print("\nall requirements met ✓")
