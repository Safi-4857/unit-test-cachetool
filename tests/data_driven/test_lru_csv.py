import csv
import pathlib

import pytest
from cachetools import LRUCache


def load_cases():
    path = pathlib.Path(__file__).parent.parent / "data" / "lru_cases.csv"
    with open(path, newline="") as f:
        return [
            (int(r["maxsize"]), int(r["inserts"]), int(r["expected_len"]))
            for r in csv.DictReader(f)
        ]


@pytest.mark.data_driven
@pytest.mark.lru
@pytest.mark.parametrize("maxsize,inserts,expected_len", load_cases())
def test_lru_len_from_csv(maxsize, inserts, expected_len):
    c = LRUCache(maxsize=maxsize)
    for i in range(inserts):
        c[i] = i
    assert len(c) == expected_len
