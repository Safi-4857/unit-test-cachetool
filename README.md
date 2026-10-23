# Unit Test Automation: cachetools

Group assignment: automated unit testing of an open-source Python project with pytest.

- **Project under test:** [cachetools](https://github.com/tkem/cachetools) (copy in `src_cachetools/`)
- **Modules tested:** `LRUCache`, `TTLCache`, `LFUCache`
- **Tools:** Python, pytest, pytest-xdist (parallel runs), pytest-order (execution order), pytest-cov (coverage)

## Contributions

| Member | Modules | Test file |
|---|---|---|
| Safi | LRUCache | `tests/unit/test_lru_cache.py` |
| Abdullah Zahid | TTLCache | `tests/unit/test_ttl_cache.py` |
| Abdullah Zahid | LFUCache | `tests/unit/test_lfu_cache.py` |


## Repository layout

```
src_cachetools/        project under test
tests/unit/            function-level and class-level tests (one file per cache)
tests/smoke/           quick ordered sanity tests
tests/data_driven/     CSV-driven parametrized tests
tests/data/            CSV test data
docs/                  design notes (ECP/BVA), Excel test cases, summary report
videos/setup_demo.mp4  setup demonstration
pytest.ini             markers and pytest configuration
run_all.sh             runs the groups in a fixed order
```

## Setup (Git Bash on Windows)

```bash
git clone https://github.com/Safi-4857/unit-test-cachetool.git
cd unit-test-cachetool
python -m venv venv
source venv/Scripts/activate        # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
pip install -e src_cachetools
```

## How to run

```bash
pytest                               # everything
pytest -n auto                       # everything, in parallel
pytest -m smoke                      # smoke suite (fixed order 1, 2, 3)
pytest -m unit                       # function-level tests
pytest -m module                     # class/module-level tests
pytest -m data_driven                # CSV-driven tests
pytest -m lru                        # one group: LRUCache (also: ttl, lfu)
pytest -m "ttl and unit"             # combine groups
pytest tests/unit/test_lfu_cache.py  # one suite (file)
bash run_all.sh                      # all groups, in the order below, each in parallel
pytest --cov=cachetools              # coverage
```

### Execution order

`run_all.sh` runs: **smoke, then unit, then module, then data_driven**. The smoke tests also carry
`@pytest.mark.order(1..3)`, so they run in that sequence. Groups run in parallel internally (`-n auto`);
the groups themselves run one after another, which keeps the order between groups fixed.

### Groups and markers

| Marker | Meaning |
|---|---|
| `smoke` | quick sanity tests |
| `unit` | function-level tests (one test class per method) |
| `module` | class/module-level tests |
| `data_driven` | tests reading CSV files from `tests/data/` |
| `lru`, `ttl`, `lfu` | tests for one cache class |

Test design notes (ECP and BVA) are in `docs/test_design_notes.md`; manual test cases in `docs/test_cases.xlsx`.