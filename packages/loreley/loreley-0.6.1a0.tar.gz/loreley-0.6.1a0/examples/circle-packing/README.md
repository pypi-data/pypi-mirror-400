## Circle packing in a unit square

This repository defines a small geometric optimisation problem about packing circles
inside the unit square.

---

## Problem definition

- **Container**: the closed unit square \([0, 1] × [0, 1]\).
- **Circles**: a fixed number \(n \in \mathbb{N}\) of circles. Each circle \(i\) has
  centre \((x_i, y_i)\) and radius \(r_i > 0\).
- **Decision variables**: the list of triples \((x_i, y_i, r_i)\) for
  \(i = 1, \dots, n\).
- **Constraints**:
  - Every circle must lie entirely inside the unit square.
  - No two circles may overlap (they may touch).
- **Objective**: for a given positive integer \(n\), **maximise the sum of radii**:

  \[
    \text{objective} = \sum_{i=1}^n r_i.
  \]

The number of circles \(n\) is fixed by the problem instance; only the positions and
radii are allowed to vary.

---

## Solution interface (`solution.py`)

Your solution must live in [`solution.py`](solution.py) and expose a single function:

```python
from typing import Iterable, Tuple

def pack_circles(n: int = 26) -> Iterable[Tuple[float, float, float]]:
    """Return an iterable of (x, y, r) triples for n circles in the unit square."""
```

Each triple `(x, y, r)` represents a circle with centre `(x, y)` and radius `r`. The
argument `n` is the requested number of circles; callers that do not specify `n` may
call `pack_circles()` with no arguments, which is equivalent to `pack_circles(26)`.

Implementations are expected to satisfy:

- All elements are length-3 iterables of real numbers.
- `n` is a positive integer.
- `r > 0` for every circle.
- Circles stay within the unit square: `r <= x <= 1 - r` and `r <= y <= 1 - r`.
- No two circles overlap: the distance between any pair of centres is at least the sum
  of their radii (within a small numerical tolerance).
- The iterable describes exactly `n` circles.

This repository intentionally contains only the problem statement and a minimal baseline
implementation in `solution.py`.

