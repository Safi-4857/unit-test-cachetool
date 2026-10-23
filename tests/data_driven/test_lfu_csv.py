import csv
import pathlib

import pytest
from cachetools import LFUCache


def load_cases():
    path = pathlib.Path(__file__).parent.parent / "data" / "lfu_cases.csv"
    with open(path, newline="") as f:
        return [
            (int(r["hits_a"]), int(r["hits_b"]), r["expected_evicted"])
            for r in csv.DictReader(f)
        ]


@pytest.mark.data_driven
@pytest.mark.lfu
@pytest.mark.parametrize("hits_a,hits_b,expected_evicted", load_cases())
def test_lfu_eviction_from_csv(hits_a, hits_b, expected_evicted):
    c = LFUCache(maxsize=2)
    c["a"] = 1
    c["b"] = 2
    for _ in range(hits_a):
        _ = c["a"]
    for _ in range(hits_b):
        _ = c["b"]
    c["c"] = 3
    assert expected_evicted not in c
