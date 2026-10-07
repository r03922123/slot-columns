# How the solution works (no statistics needed)

This explains the solution in `slot.py` using only **counting and dividing**.
Words used: **column** = up and down, **row** = left to right.

---

## 1. The setup

The screen is a 3×3 grid with three columns: **left, middle, right**.

Behind each column is a **long vertical list of symbols**. A spin slides each column's list
to a random spot, and the window shows **3 symbols from that list, one under the other**:

```
  LEFT column list          the 3×3 window you see
        ...
         2                  LEFT   MIDDLE   RIGHT
         2   ──────►      ┌──────┬────────┬───────┐
         0   ──────►      │  2   │   2    │   ?   │  ← top row
         2   ──────►      │  2   │   2    │   ?   │  ← middle row
        ...               │  0   │   2    │   ?   │  ← bottom row
                          └──────┴────────┴───────┘
```

- Each column slides **on its own**.
- A list **wraps around**: after the last symbol comes the first one again.
- **Our job is to choose the symbols in each column's list.**

## 2. The goal

- **RTP = 0.95**: over many spins, players get back 95 for every 100 they bet.
- **Win rate ≥ 55%**: at least 55 of every 100 spins pay something.

The five winning patterns are four 2×2 squares (each pays 1× the symbol's multiplier) and the full 3×3 (pays 5×).
Symbol multipliers: `0 → 0.25, 1 → 0.55, 2 → 1, 3 → 3, 4 → 5`.

---

## 3. The key idea: the middle column only contains 2s

Look at the five patterns. `M` marks the middle column:

```
top-left   top-right  bottom-left bottom-right  full 3×3
■ M .      . M ■      . . .       . . .         ■ M ■
■ M .      . M ■      ■ M .       . M ■         ■ M ■
. . .      . . .      ■ M .       . M ■         ■ M ■
```

**Every pattern uses the middle column.** So we make the middle column's list contain only `2`s.
Wherever it stops, it shows `2, 2, 2`. As a result:

1. **Only symbol `2` can ever win**, because every pattern has to match the middle column.
2. **Each square wins when the left (or right) column shows `2, 2` in the same two rows:**

| square | wins when |
|---|---|
| top-left | left column shows `2, 2` in the **top + middle** rows |
| bottom-left | left column shows `2, 2` in the **middle + bottom** rows |
| top-right | right column shows `2, 2` in the **top + middle** rows |
| bottom-right | right column shows `2, 2` in the **middle + bottom** rows |

The whole problem is now: **how often does a side column show `2, 2`?**

---

## 4. A small example: a 10-symbol list

Before the real solution, here is a tiny version. The left and right columns both use this list:

```
position:  0  1  2  3  4  5  6  7  8  9
symbol:    2  2  0  2  2  1  3  4  0  1
           └──┘     └──┘
          pair 1   pair 2
```

When a column stops at a position, the window shows **that symbol on the top row, the next one on the
middle row, and the one after that on the bottom row** (wrapping from 9 back to 0).

All 10 possible stops:

| stop at | top | middle | bottom | top two rows = 2,2? | bottom two rows = 2,2? |
|---|---|---|---|---|---|
| 0 | **2** | **2** | 0 | ✓ | |
| 1 | 2 | 0 | 2 | | |
| 2 | 0 | **2** | **2** | | ✓ |
| 3 | **2** | **2** | 1 | ✓ | |
| 4 | 2 | 1 | 3 | | |
| 5 | 1 | 3 | 4 | | |
| 6 | 3 | 4 | 0 | | |
| 7 | 4 | 0 | 1 | | |
| 8 | 0 | 1 | 2 | | |
| 9 | 1 | **2** | **2** | | ✓ (wraps around) |

What this shows:

- Top two rows show `2, 2` at **2 of 10 stops** → the top square wins **20%** of the time.
- Bottom two rows show `2, 2` at **2 of 10 stops** → the bottom square also wins **20%** of the time.
- **Each pair gives one top win and one bottom win**, at different stops.

So: **how often a square wins = number of pairs ÷ length of the list.**

### Working out the small machine completely

The left column (10 stops) × middle column (3 stops) × right column (10 stops) = **300 possible spins**, all equally likely.

**Payout.** The top-left square wins whenever the left column is at stop 0 or 3. The other columns can be anywhere:

```
spins where top-left wins = 2 × 3 × 10 = 60
all 4 squares together    = 4 × 60     = 240   (each win pays 1)
RTP                       = 240 ÷ 300  = 0.80
```

**Win rate.** The left column shows a pair (top or bottom) at 4 stops, so it shows **no pair at 6 stops**.
The same goes for the right column. A spin loses only when **both** side columns show no pair:

```
losing spins  = 6 × 3 × 6    = 108
winning spins = 300 − 108    = 192
win rate      = 192 ÷ 300    = 64%
```

The small machine pays back only 0.80. **To reach 0.95 we need more pairs for each symbol in the list.**

---

## 5. The real solution: 19 pairs in 80 symbols

### Where 19 and 80 come from

```
we must pay back 95 out of every 100 bet
4 squares share that   → each square pays 95 ÷ 4 = 23.75
each win pays 1        → each square must win 23.75% of the time
```

From the small example, a square wins `pairs ÷ length` of the time. So we need:

```
pairs ÷ length = 0.2375
```

Pairs must be a whole number. Try list lengths until it works:

| list length | pairs needed (length × 0.2375) | whole number? |
|---|---|---|
| 10 | 2.375 | ✗ |
| 20 | 4.75 | ✗ |
| 40 | 9.5 | ✗ |
| **80** | **19** | ✓ |

**80 is the shortest list that works, and it needs exactly 19 pairs.** (160 with 38, or 240 with 57, give the same game.)

### Building the 80-symbol list

```
2 2 0  2 2 1  2 2 3  2 2 4  2 2 0  ...  (19 pairs)   0 1 3 4 0 1 ...  (filler)
└────┘
pair + separator
```

| part | count |
|---|---|
| 19 pairs, each written as `2 2 x` (pair + separator) | 19 × 3 = 57 symbols |
| filler to reach 80 | 80 − 57 = 23 symbols |
| **total** | **80** |

- **Separator `x`** (0, 1, 3 or 4) after each pair: two pairs never touch, so three 2s never appear in a column.
  That means the full 3×3 jackpot can never happen, and the top and bottom squares on one side never win at
  the same stop. Both keep the counting simple.
- **Filler**: any non-2 symbol, only there to make the list 80 long. It can never win, because the middle column is always 2.

The left and right columns use this same list. The middle column is `2, 2, 2`.

### Counting the real machine

Same steps as the small example, with bigger numbers:

```
possible spins = 80 × 3 × 80 = 19,200
```

**Payout:**

```
spins where top-left wins = 19 × 3 × 80     = 4,560
all 4 squares together    = 4 × 4,560       = 18,240
RTP                       = 18,240 ÷ 19,200 = 0.95    ✓
```

**Win rate:**

```
left column shows a pair at 19 + 19 = 38 stops  →  no pair at 80 − 38 = 42 stops
right column: same, no pair at 42 stops

losing spins  = 42 × 3 × 42     = 5,292
winning spins = 19,200 − 5,292  = 13,908
win rate      = 13,908 ÷ 19,200 = 72.4%    ✓  (need ≥ 55%)
```

### Small vs real, side by side

| | small example | real solution |
|---|---|---|
| side column list length | 10 | 80 |
| pairs of `2 2` | 2 | 19 |
| a square wins | 2 ÷ 10 = 20% | 19 ÷ 80 = 23.75% |
| RTP = 4 × that | 0.80 | **0.95** ✓ |
| win rate | 64% | **72.4%** ✓ |

---

## 6. Why symbol 2 and not another symbol

The payout is fixed at 0.95. The symbol's multiplier decides whether that comes as **many small wins** or
**a few big ones**. For each symbol, this is how often a square would need to win:

| winning symbol | multiplier | a square must win | problem |
|---|---|---|---|
| 0 | 0.25 | 95% of stops | impossible: each pair uses 3 symbols (`2 2 x`), so at most 1 in 3 stops can start a pair |
| 1 | 0.55 | 43% of stops | still more than 1 in 3, so also impossible |
| **2** | **1** | **23.75% of stops** | **fits, win rate 72%** |
| 3 | 3 | 7.9% of stops | wins too rare: win rate 29% |
| 4 | 5 | 4.75% of stops | wins too rare: win rate 18% |

Symbol 2 is the only one cheap enough to win often and expensive enough to fit in the list.

---

## 7. How the code checks it

We don't just trust the arithmetic above. The code counts every spin itself.

| code (in `slot.py`) | what it does |
|---|---|
| `build_columns()` | builds the three column lists |
| `window(list, stop)` | "if this column stops here, what shows on the top, middle and bottom rows?" (the table in section 4) |
| `payout(grid)` | checks one 3×3 grid against all 5 patterns and adds up the winnings |
| `evaluate()` | goes through all 19,200 spins, adds up the payout and counts the wins (section 5) using exact fractions, so 0.95 means exactly 95/100 |
| `simulate()` | spins randomly 200,000 times like a real player, as a second check (≈ 0.95) |

**One speed-up:** many stops show the same 3 symbols (for example, every stop showing `2 2 0` looks the same).
`evaluate()` checks each different-looking grid once (only 361 of them) and multiplies by how many stops
produce it. That gives the same answer as checking all 19,200 spins, much faster.

---

## In one line

**The middle column always shows 2, 2, 2, so a square wins whenever the left or right column shows 2, 2
beside it. With 19 pairs in an 80-symbol list, each square wins 23.75% of the time: 4 × 0.2375 = 0.95 paid back,
and 72.4% of spins win.**
