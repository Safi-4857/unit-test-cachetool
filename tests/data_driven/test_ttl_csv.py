import csv
import pathlib

import pytest
from cachetools import TTLCache


class Timer:
    def __init__(self):
        self.t = 0

    def __call__(self):
        return self.t


def load_cases():
    path = pathlib.Path(__file__).parent.parent / "data" / "ttl_cases.csv"
    with open(path, newline="") as f:
        return [
            (int(r["ttl"]), int(r["elapsed"]), r["expected_alive"] == "True")
            for r in csv.DictReader(f)
        ]


@pytest.mark.data_driven
@pytest.mark.ttl
@pytest.mark.parametrize("ttl,elapsed,expected_alive", load_cases())
def test_ttl_expiry_from_csv(ttl, elapsed, expected_alive):
    timer = Timer()
    c = TTLCache(maxsize=2, ttl=ttl, timer=timer)
    c["a"] = 1
    timer.t += elapsed
    assert ("a" in c) is expected_alive
