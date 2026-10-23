# Test Design Notes (ECP and BVA)

Project: cachetools. Tool: pytest.
ECP = Equivalence Class Partitioning, BVA = Boundary Value Analysis.

## LRUCache (owner: Safi)

Test file: `tests/unit/test_lru_cache.py`

| Function | Technique | Partition / boundary | Test values | Expected |
|---|---|---|---|---|
| `__setitem__` | BVA | below / at / above capacity | n-1, n, n+1 items | n+1 evicts the least recently used |
| `__setitem__` | BVA | minimum maxsize | maxsize=0 | `ValueError` on insert |
| `__setitem__` | ECP | new key vs existing key | new, overwrite | size grows / size unchanged |
| `__getitem__` | ECP | present vs missing key | present, absent | value / `KeyError` |
| `__getitem__` | ECP | recency | read oldest key, then insert | read key survives eviction |
| `__getitem__` | BVA | empty cache | empty | `KeyError` |
| `__delitem__` | ECP | present vs missing key | present, absent, twice | removed / `KeyError` |
| `__delitem__` | BVA | size n -> n-1 | full cache | `len` decreases, space freed |
| `pop` | ECP | present / missing / missing + default | key, absent, absent + 42 | value / `KeyError` / 42 |
| `popitem` | BVA | empty vs 1 item vs many | empty, 1, 3 | `KeyError` / pair / LRU pair |
| `popitem` | ECP | recency | read oldest, then pop | second oldest returned |
| `get` | ECP | present / missing / default | key, absent, absent + 7 | value / None / 7 |
| `get` | ECP | side effects | missing key | cache not modified |
| `setdefault` | ECP | missing / present / no default | new, existing, omitted | sets / keeps / None |
| `setdefault` | BVA | at capacity | n items, add one | LRU evicted |
| `maxsize`, `currsize` | BVA | empty / typical / capped | 0, 2, 10 inserts into maxsize 2 | 0 / 2 / 2 |
| `getsizeof` | BVA | value size vs maxsize | size 3 into maxsize 10 and 2 | accepted / `ValueError` |

Class-level tests (`@pytest.mark.module`): eviction order across many inserts,
mixed read/write access, `len` tracking, `clear`, `update`, and a parametrized
BVA check that `len` never exceeds maxsize for maxsize = 1, 2, 3, 10.

## TTLCache (owner: Abdullah Zahid)

Test file: `tests/unit/test_ttl_cache.py`
Same function table as above, plus expiry: BVA at ttl-1, ttl, ttl+1, using a fake timer.

## LFUCache (owner: Abdullah Zahid)

Test file: `tests/unit/test_lfu_cache.py`
Same function table as above, with eviction of the least frequently used item.
