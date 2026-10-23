# Summary Report: Unit Test Automation for cachetools

## Scope
Project: cachetools (Python caching library). Modules tested: `LRUCache`, `TTLCache`, `LFUCache`.
Tools: pytest, pytest-xdist, pytest-order, pytest-cov. Techniques: Equivalence Class Partitioning (ECP)
and Boundary Value Analysis (BVA); see `docs/test_design_notes.md`.

## What was tested
For each class: `__setitem__`, `__getitem__`, `__delitem__`, `pop`, `popitem`, `get`, `setdefault`,
size properties (`maxsize`, `currsize`, custom `getsizeof`), and class-level behavior (eviction order,
`len`, `clear`, `update`). TTLCache additionally covers expiry at ttl-1, ttl and ttl+1 using a fake timer
(no `time.sleep`). LFUCache covers eviction of the least frequently used key.

## Results
| Suite | Tests | Result |
|---|---|---|
| tests/unit/test_lru_cache.py | 57 | all pass |
| tests/unit/test_ttl_cache.py | 62 | all pass |
| tests/unit/test_lfu_cache.py | 56 | all pass |
| tests/data_driven (3 CSV files) | 17 | all pass |
| tests/smoke | 3 | all pass |
| **Total** | **195** | **195 passed** |

The full suite passes serially, in parallel (`pytest -n auto`) and through `run_all.sh`.

## Coverage
`pytest --cov=cachetools`: `cachetools/__init__.py` (which contains the three classes) is at 68%.
The package total is 33% because the other modules (`func.py`, `keys.py`, and so on) were out of scope.

## Task 3: data-driven tests
Three CSV files in `tests/data/` feed parametrized tests (`lru_cases.csv`, `ttl_cases.csv`, `lfu_cases.csv`).
`docs/test_cases.xlsx` lists 14 test cases with technique, expected and actual result, owner and the automated test.

## Task 4: configuration
`pytest.ini` defines markers (groups) and strict marker checking. Parallel runs use `pytest -n auto`.
Groups run in a fixed order through `run_all.sh`, and smoke tests use `pytest-order`.
Parametrization (`@pytest.mark.parametrize`) is used for BVA values and for the CSV-driven tests.

## Issues found
No defects were found in cachetools. One of our own tests was flaky because it depended on how cachetools
breaks ties between keys with equal frequency (not guaranteed by the library). It was rewritten to use
distinct frequencies and then run 30 times without failure.

## Who did what
| Member | Work |
|---|---|
| Safi Ur Rehman | Repository, environment and setup video; design notes; LRUCache tests; CSV and Excel work; configuration; README and report.

| Abdullah Zahid | TTLCache and LFUCache tests 
|Owner of TTLCache and LFUCache (tests committed by Abdullah Zahid ). |
