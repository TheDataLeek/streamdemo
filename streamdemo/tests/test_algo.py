import numpy as np

from ..algo import score_bump


def test_score_bump():
    x = 0
    vals = [0, 0.5, 0.75, 0.875]
    for i, item in enumerate(vals):
        assert x == vals[i]
        x = score_bump(x)

