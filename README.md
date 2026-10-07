# slot-columns

A solution to the slot game homework in [`DS-HomeWork.md`](DS-HomeWork.md): choose the symbols behind each
column of a 3×3 slot machine so that

- **RTP is exactly 0.95**: players get back 95 for every 100 they bet, and
- **the win rate is at least 55%**: at least 55 of every 100 spins pay something.

**Result:** RTP = **19/20 = 0.95 exactly**, win rate = **1159/1600 = 72.4%**. Both are proven by counting every possible spin.

Words used: **column** = up and down, **row** = left to right.

## Where to start reading

1. **[`intuition.md`](intuition.md)**: **why** the solution works, with a small 10-symbol example you can check by hand. No statistics needed.
2. **[`method.md`](method.md)**: **how** the code is built, step by step, with the real code.

## The solution in 30 seconds

1. **Every winning pattern uses the middle column.** So the middle column only contains `2`s, and always shows `2, 2, 2`.
   Now only symbol `2` can win, and a 2×2 square wins whenever the left or right column shows `2, 2` beside it.
2. **The left and right columns** each have a list of 80 symbols containing **19 pairs of `2 2`**, each pair
   followed by a different symbol so that three 2s never appear in a row:
   ```
   2 2 0  2 2 1  2 2 3  2 2 4  ...  (19 pairs)  ...  0 1 3 4 0 1 ...  (filler up to 80)
   ```
3. **Count every spin:** 80 × 3 × 80 = 19,200 possible spins.

| | count | result |
|---|---|---|
| spins where one square wins | 19 × 3 × 80 = 4,560 | |
| total paid by 4 squares (each win pays 1) | 4 × 4,560 = 18,240 | RTP = 18,240 ÷ 19,200 = **0.95** ✓ |
| spins where both sides show no pair | 42 × 3 × 42 = 5,292 | win rate = (19,200 − 5,292) ÷ 19,200 = **72.4%** ✓ |

## Run it

Needs [uv](https://docs.astral.sh/uv/). Only the Python standard library, plus pytest for tests.

```bash
uv run slot.py        # print the column lists, exact RTP / win rate, random check
uv run pytest -q      # run the 11 tests
```

Expected output of `uv run slot.py` (after the three column lists):

```
exact   RTP      = 19/20 = 0.950000  (bet 100 -> expect 95 back)
exact   win rate = 1159/1600 = 0.724375
sim     RTP      = 0.9507, win rate = 0.7255  (200k spins)

rule=max design: RTP = 19/20 = 0.950000, win rate = 17/20 = 0.850000
sim     RTP      = 0.9505, win rate = 0.8497  (200k spins)

all requirements met ✓
```

## Assumptions

1. Each spin stops each column at a random position, independently, and every position is equally likely.
2. **The homework doesn't say how several wins on one spin are paid**, so the code supports both readings:

   | reading | design | RTP | win rate |
   |---|---|---|---|
   | all wins add up (default, usual slot convention) | `build_columns()`: 19 pairs in 80 | 0.95 | 72.4% |
   | only the biggest win pays | `build_columns_max_rule()`: 5 / 3 / 8 symbols | 0.95 | 85% |

   With the middle column all 2s, no single design works for both; see [`intuition.md` section 8](intuition.md#8-what-if-only-the-biggest-win-pays).
3. A "win" means at least one pattern wins on that spin.
