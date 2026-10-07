# How to implement it, step by step

This explains how the code in `slot.py` is built. For *why* the design works, read `intuition.md` first.
Words used: **column** = up and down, **row** = left to right.

The code is built **from the smallest piece up**. Each step uses the one before it:

```
Step 1  Describe the game as data        (symbols, patterns)
Step 2  One column stops → 3 symbols     window()
Step 3  One 3×3 grid → payout            payout()
Step 4  Every spin → RTP and win rate    evaluate()
Step 5  Build the column lists           build_columns()
Step 6  Check by playing                 simulate()
Step 7  Lock it in with tests            test_slot.py
```

In the code, `columns` is a list of three lists: `columns[0]` is the left column, `columns[1]` the middle,
`columns[2]` the right. Each one is the long list of symbols behind that column.

---

## Step 1: describe the game as data

Before writing any logic, write down the rules as plain data.

**Symbols and what they pay:**

```python
MULT = {0: Fraction(1, 4), 1: Fraction(11, 20), 2: Fraction(1), 3: Fraction(3), 4: Fraction(5)}
```

Why `Fraction(1, 4)` instead of `0.25`? Computers store decimals approximately: in Python, `0.1 + 0.2` gives
`0.30000000000000004`. The rule says RTP must be *exactly* 0.95, so we use fractions, which are always exact.

**Patterns, as lists of cells.** Each cell is `(row, column)`, numbered from 0:

```
          col 0   col 1   col 2
row 0    (0,0)   (0,1)   (0,2)
row 1    (1,0)   (1,1)   (1,2)
row 2    (2,0)   (2,1)   (2,2)
```

```python
SQUARES = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # 4.1 top-left
    [(0, 1), (0, 2), (1, 1), (1, 2)],  # 4.2 top-right
    [(1, 0), (1, 1), (2, 0), (2, 1)],  # 4.3 bottom-left
    [(1, 1), (1, 2), (2, 1), (2, 2)],  # 4.4 bottom-right
]
FULL = [(r, c) for r in range(3) for c in range(3)]  # 4.5, pays 5x
```

Now "a pattern" is just a list of cells that must all hold the same symbol.

**Two short names for the shapes of data**, used in the type hints (the `: Column` and `-> Fraction` parts of each function):

```python
Column = list[int]      # the long list of symbols behind one column
Grid = list[list[int]]  # the 3x3 window, grid[row][col]
```

Type hints don't change what the code does. They only say what goes in and what comes out, so
`def window(column: Column, stop: int) -> tuple[int, ...]` reads as: "give it a column list and a stop
position, and it gives back a few symbols".

---

## Step 2: one column stops → which 3 symbols show

```python
def window(column: Column, stop: int) -> tuple[int, ...]:
    """The 3 symbols a column shows when it lands on `stop` (it wraps around)."""
    return tuple(column[(stop + r) % len(column)] for r in range(3))
```

In plain words: take the symbol at `stop` (top row), `stop + 1` (middle row) and `stop + 2` (bottom row).
The `% len(column)` handles the wrap-around: past the end of the list, go back to the start.

Trying it on the 10-symbol example from `intuition.md`:

```python
lst = [2, 2, 0, 2, 2, 1, 3, 4, 0, 1]
window(lst, 0)  # → (2, 2, 0)   top two rows are 2,2
window(lst, 9)  # → (1, 2, 2)   wraps: positions 9, 0, 1
```

These match the table in `intuition.md`, so this step is checked.

---

## Step 3: score one 3×3 grid

First, a helper that answers: "Do all these cells hold the same symbol? If so, which one?"

```python
def same_symbol(grid: Grid, cells: list[tuple[int, int]]) -> int | None:
    """The symbol if all cells match, else None."""
    syms = {grid[r][c] for r, c in cells}
    return syms.pop() if len(syms) == 1 else None
```

The trick: a **set** (`{...}`) keeps only distinct values. If every cell is `2`, the set is `{2}`, which has
one item, so they all match. If the cells hold `2` and `0`, the set is `{2, 0}`, so they don't.

Then the scorer checks all five patterns and adds up the winnings:

```python
def payout(grid: Grid) -> Fraction:
    """Payout per 1 unit of bet for a 3x3 grid (grid[row][col]). Wins add up."""
    total = Fraction(0)
    for cells in SQUARES:                  # four 2×2 squares: pay 1 × multiplier
        s = same_symbol(grid, cells)
        if s is not None:
            total += MULT[s]
    s = same_symbol(grid, FULL)            # full 3×3: pays 5 × multiplier
    if s is not None:
        total += 5 * MULT[s]
    return total
```

Example:

```python
payout([[2, 2, 0],
        [2, 2, 1],
        [0, 2, 4]])   # → 1   (only the top-left square matches)
```

At this point the code knows the **rules of the game**. Everything after this is about
**our design** and **checking it**.

---

## Step 4: go through every spin → RTP and win rate

### The simple idea

The most obvious way: three nested loops, one per column. Try every stopping position, score the grid, and add it all up:

```python
for i in range(len(columns[0])):              # every left-column stop
    for j in range(len(columns[1])):          # every middle-column stop
        for k in range(len(columns[2])):      # every right-column stop
            a, b, c = window(columns[0], i), window(columns[1], j), window(columns[2], k)
            p = payout([[a[r], b[r], c[r]] for r in range(3)])
            # add p to the total paid; if p > 0, count one win
```

This is the counting from `intuition.md`, done by the computer: 80 × 3 × 80 = 19,200 spins.

`a`, `b` and `c` are what the left, middle and right columns show, each as (top, middle, bottom).
`[[a[r], b[r], c[r]] for r in range(3)]` puts them side by side, row by row, to form the 3×3 grid:

```
a = (2, 2, 0)   b = (2, 2, 2)   c = (0, 1, 3)

grid = [[2, 2, 0],    ← row 0: a[0], b[0], c[0]
        [2, 2, 1],    ← row 1: a[1], b[1], c[1]
        [0, 2, 3]]    ← row 2: a[2], b[2], c[2]
```

### What `slot.py` actually does: the same idea, faster

Many stops show the **same 3 symbols**. For example, every stop showing `(2, 2, 0)` looks identical.
So instead of trying every stop, `evaluate()`:

1. **counts** how often each 3-symbol view appears in each column, for example
   `{(2, 2, 0): 5, (2, 0, 2): 5, (0, 1, 3): 6, ...}`, then
2. loops over the **different views** only, and gives each grid a **weight** = how many spins show it.

```python
def evaluate(columns: list[Column]) -> tuple[Fraction, Fraction]:
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
    return paid / total_spins, Fraction(wins, total_spins)   # (RTP, win rate)
```

Same exact answer as the three simple loops, but only 361 grids to score instead of 19,200.

**Advice: write the simple version first.** It's obviously correct, so it's your reference.
Only then write the fast version and check that it gives the same answer.

---

## Step 5: build the column lists (the actual design)

This is the only step that contains **the solution idea**. Everything else is just the game and the checker.

```python
def build_columns(pairs: int = 19, length: int = 80) -> list[Column]:
    if 3 * pairs > length:
        raise ValueError(f"{pairs} pairs need {3 * pairs} symbols (2, 2, separator each), but length is {length}")
    filler = [0, 1, 3, 4]
    side = []
    for i in range(pairs):
        side += [2, 2, filler[i % 4]]                             # "2 2 x"  (pair + separator)
    side += [filler[i % 4] for i in range(length - len(side))]   # pad to 80
    middle = [2, 2, 2]
    return [side, middle, side]                                  # left, middle, right
```

This builds:

```
left / right:  2 2 0  2 2 1  2 2 3  2 2 4  ... (19 pairs = 57 symbols) ... 0 1 3 4 0 1 ... (23 filler)
middle:        2 2 2
```

- The first check stops you from asking for more pairs than fit: each pair takes 3 symbols (`2 2 x`).
- `filler[i % 4]` rotates through 0, 1, 3, 4 so the separators vary.

---

## Step 6: check by actually playing

`evaluate()` is exact, but it's still our own code. A second check that works differently catches mistakes in it:

```python
def simulate(columns: list[Column], spins: int = 200_000, seed: int = 1337) -> tuple[float, float]:
    """Random check: actually spin the machine many times and count."""
    rng = random.Random(seed)                   # fixed seed → same result every run
    paid, wins = 0.0, 0
    for _ in range(spins):
        cols = [window(column, rng.randrange(len(column))) for column in columns]   # random stop per column
        p = float(payout([[cols[0][r], cols[1][r], cols[2][r]] for r in range(3)]))
        paid += p
        wins += p > 0
    return paid / spins, wins / spins
```

It plays like a real player: a random stop for each column, 200,000 times. The result is about 0.9507.
It's close to 0.95 but not exact, because random play is never exact. That's why `evaluate()` is the
one that proves the rule, and `simulate()` is only a sanity check.

---

## Step 7: lock it in with tests

`test_slot.py` checks each step on its own, smallest piece first:

| test | checks |
|---|---|
| `test_single_square` | Step 3: one square on a hand-made grid pays correctly |
| `test_no_win` | Step 3: a grid with no match pays 0 |
| `test_two_squares_add_up` | Step 3: two squares on one spin add up |
| `test_full_grid_also_pays_its_squares` | Step 3: the full 3×3 pays its bonus plus its four squares |
| `test_evaluate_trivial_machine` | Step 4: a machine where every spin wins gives the RTP we expect |
| `test_design_meets_requirements` | Step 5: our design gives RTP exactly 0.95 and win rate ≥ 55% |
| `test_too_many_pairs_is_rejected` | Step 5: asking for more pairs than fit gives an error |

---

## Running it with uv

```bash
uv init --bare          # create the project (pyproject.toml)
uv add --dev pytest     # add the test tool

uv run slot.py          # print the column lists, exact RTP / win rate, simulation
uv run pytest -q        # run all 7 tests
```

Expected output of `uv run slot.py` (after the three column lists):

```
exact   RTP      = 19/20 = 0.950000  (bet 100 -> expect 95 back)
exact   win rate = 1159/1600 = 0.724375
sim     RTP      = 0.9507, win rate = 0.7255  (200k spins)

all requirements met ✓
```

---

## The whole method on one page

```
RULES (fixed by the homework)        DESIGN (our idea)          CHECK (proof)
┌──────────────────────────┐       ┌──────────────────┐      ┌─────────────────────┐
│ MULT, SQUARES, FULL      │       │ build_columns()  │      │ evaluate()  exact   │
│ window()  1 column       │──────▶│ 19 pairs / 80    │─────▶│ simulate()  random  │
│ payout()  1 grid         │       │ middle = 2,2,2   │      │ tests       pytest  │
└──────────────────────────┘       └──────────────────┘      └─────────────────────┘
```

**Keep these three parts separate.** The rules and the checker know nothing about our trick, so they can
judge it fairly.
