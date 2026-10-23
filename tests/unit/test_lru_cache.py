import pytest
from cachetools import LRUCache


def make(maxsize=3, **items):
    c = LRUCache(maxsize=maxsize)
    for k, v in items.items():
        c[k] = v
    return c


# ---------------------------------------------------------------- __setitem__
@pytest.mark.unit
@pytest.mark.lru
class TestLRUSetItem:
    def test_insert_single(self):  # ECP: valid
        c = make(2)
        c["a"] = 1
        assert c["a"] == 1

    def test_below_capacity(self):  # BVA: n-1
        c = make(3, a=1, b=2)
        assert len(c) == 2

    def test_at_capacity(self):  # BVA: n
        c = make(3, a=1, b=2, c=3)
        assert len(c) == 3

    def test_over_capacity_evicts_lru(self):  # BVA: n+1
        c = make(2, a=1, b=2)
        c["c"] = 3
        assert "a" not in c and len(c) == 2

    def test_overwrite_keeps_size(self):  # ECP: existing key
        c = make(2, a=1)
        c["a"] = 9
        assert c["a"] == 9 and len(c) == 1

    def test_overwrite_at_capacity_no_eviction(self):  # BVA: n, existing key
        c = make(2, a=1, b=2)
        c["a"] = 5
        assert "a" in c and "b" in c

    def test_maxsize_zero_rejects_insert(self):  # BVA: min maxsize
        c = LRUCache(maxsize=0)
        with pytest.raises(ValueError):
            c["a"] = 1


# ---------------------------------------------------------------- __getitem__
@pytest.mark.unit
@pytest.mark.lru
class TestLRUGetItem:
    def test_existing_key(self):  # ECP: valid
        assert make(2, a=1)["a"] == 1

    def test_missing_key_raises(self):  # ECP: invalid
        with pytest.raises(KeyError):
            make(2)["x"]

    def test_get_refreshes_recency(self):  # ECP: recency
        c = make(2, a=1, b=2)
        _ = c["a"]
        c["c"] = 3
        assert "a" in c and "b" not in c

    def test_get_on_empty_cache_raises(self):  # BVA: empty
        with pytest.raises(KeyError):
            LRUCache(maxsize=2)["a"]

    def test_value_none_is_returned(self):  # ECP: falsy value
        c = make(2, a=None)
        assert c["a"] is None

    def test_get_after_eviction_raises(self):  # BVA: n+1
        c = make(1, a=1)
        c["b"] = 2
        with pytest.raises(KeyError):
            c["a"]


# ---------------------------------------------------------------- __delitem__
@pytest.mark.unit
@pytest.mark.lru
class TestLRUDelItem:
    def test_delete_existing(self):  # ECP: valid
        c = make(2, a=1)
        del c["a"]
        assert "a" not in c

    def test_delete_missing_raises(self):  # ECP: invalid
        with pytest.raises(KeyError):
            del make(2)["a"]

    def test_delete_reduces_len(self):  # BVA: n -> n-1
        c = make(2, a=1, b=2)
        del c["a"]
        assert len(c) == 1

    def test_delete_frees_space(self):  # BVA: full then free
        c = make(2, a=1, b=2)
        del c["a"]
        c["c"] = 3
        assert "b" in c and "c" in c

    def test_delete_twice_raises(self):  # ECP: invalid
        c = make(2, a=1)
        del c["a"]
        with pytest.raises(KeyError):
            del c["a"]


# ---------------------------------------------------------------------- pop
@pytest.mark.unit
@pytest.mark.lru
class TestLRUPop:
    def test_pop_existing(self):  # ECP: valid
        c = make(2, a=1)
        assert c.pop("a") == 1 and "a" not in c

    def test_pop_missing_raises(self):  # ECP: invalid
        with pytest.raises(KeyError):
            make(2).pop("a")

    def test_pop_missing_with_default(self):  # ECP: invalid + default
        assert make(2).pop("a", 42) == 42

    def test_pop_existing_ignores_default(self):  # ECP: valid + default
        assert make(2, a=1).pop("a", 42) == 1

    def test_pop_reduces_len(self):  # BVA: n -> n-1
        c = make(2, a=1, b=2)
        c.pop("a")
        assert len(c) == 1

    def test_pop_default_none(self):  # ECP: falsy default
        assert make(2).pop("a", None) is None


# ------------------------------------------------------------------ popitem
@pytest.mark.unit
@pytest.mark.lru
class TestLRUPopItem:
    def test_popitem_returns_lru_pair(self):  # ECP: valid
        c = make(3, a=1, b=2, c=3)
        assert c.popitem() == ("a", 1)

    def test_popitem_empty_raises(self):  # BVA: empty
        with pytest.raises(KeyError):
            LRUCache(maxsize=2).popitem()

    def test_popitem_respects_access(self):  # ECP: recency
        c = make(3, a=1, b=2, c=3)
        _ = c["a"]
        assert c.popitem() == ("b", 2)

    def test_popitem_single_item(self):  # BVA: size 1
        c = make(2, a=1)
        assert c.popitem() == ("a", 1) and len(c) == 0

    def test_popitem_until_empty(self):  # BVA: drain
        c = make(2, a=1, b=2)
        c.popitem()
        c.popitem()
        with pytest.raises(KeyError):
            c.popitem()


# ---------------------------------------------------------------------- get
@pytest.mark.unit
@pytest.mark.lru
class TestLRUGet:
    def test_get_existing(self):  # ECP: valid
        assert make(2, a=1).get("a") == 1

    def test_get_missing_returns_none(self):  # ECP: invalid
        assert make(2).get("a") is None

    def test_get_missing_with_default(self):  # ECP: invalid + default
        assert make(2).get("a", 7) == 7

    def test_get_refreshes_recency(self):  # ECP: recency
        c = make(2, a=1, b=2)
        c.get("a")
        c["c"] = 3
        assert "a" in c and "b" not in c

    def test_get_does_not_insert(self):  # ECP: side effects
        c = make(2)
        c.get("a", 1)
        assert len(c) == 0


# --------------------------------------------------------------- setdefault
@pytest.mark.unit
@pytest.mark.lru
class TestLRUSetDefault:
    def test_setdefault_new_key(self):  # ECP: missing
        c = make(2)
        assert c.setdefault("a", 5) == 5 and c["a"] == 5

    def test_setdefault_existing_key(self):  # ECP: present
        c = make(2, a=1)
        assert c.setdefault("a", 5) == 1 and c["a"] == 1

    def test_setdefault_no_default_is_none(self):  # ECP: default omitted
        c = make(2)
        assert c.setdefault("a") is None and "a" in c

    def test_setdefault_at_capacity_evicts(self):  # BVA: n+1
        c = make(2, a=1, b=2)
        c.setdefault("c", 3)
        assert "a" not in c and len(c) == 2

    def test_setdefault_increases_len(self):  # BVA: n -> n+1
        c = make(3, a=1)
        c.setdefault("b", 2)
        assert len(c) == 2


# ------------------------------------------------- maxsize / currsize / len
@pytest.mark.unit
@pytest.mark.lru
class TestLRUSizeProperties:
    def test_maxsize_value(self):  # ECP: valid
        assert LRUCache(maxsize=5).maxsize == 5

    def test_currsize_empty(self):  # BVA: 0
        assert LRUCache(maxsize=5).currsize == 0

    def test_currsize_after_inserts(self):  # ECP: valid
        assert make(5, a=1, b=2).currsize == 2

    def test_currsize_never_exceeds_maxsize(self):  # BVA: n+1
        c = LRUCache(maxsize=2)
        for i in range(10):
            c[i] = i
        assert c.currsize == 2

    def test_custom_getsizeof(self):  # ECP: custom sizing
        c = LRUCache(maxsize=10, getsizeof=len)
        c["a"] = "xxx"
        assert c.currsize == 3

    def test_value_larger_than_maxsize_raises(self):  # BVA: size > maxsize
        c = LRUCache(maxsize=2, getsizeof=len)
        with pytest.raises(ValueError):
            c["a"] = "xxx"


# ------------------------------------------------------- class / module level
@pytest.mark.module
@pytest.mark.lru
class TestLRUCacheModule:
    def test_new_cache_is_empty(self):
        assert len(LRUCache(maxsize=3)) == 0

    def test_eviction_order_is_least_recent_first(self):
        c = make(3, a=1, b=2, c=3)
        c["d"] = 4
        c["e"] = 5
        assert "a" not in c and "b" not in c and "c" in c

    def test_mixed_access_changes_victim(self):
        c = make(3, a=1, b=2, c=3)
        _ = c["a"]
        _ = c["b"]
        c["d"] = 4
        assert "c" not in c

    def test_contains_for_present_and_absent(self):
        c = make(2, a=1)
        assert "a" in c and "z" not in c

    def test_len_tracks_insert_and_delete(self):
        c = make(3, a=1, b=2)
        del c["a"]
        c["c"] = 3
        assert len(c) == 2

    def test_clear_empties_cache(self):
        c = make(3, a=1, b=2)
        c.clear()
        assert len(c) == 0 and c.currsize == 0

    def test_update_inserts_multiple(self):
        c = LRUCache(maxsize=5)
        c.update({"a": 1, "b": 2})
        assert len(c) == 2

    def test_update_over_capacity_evicts(self):
        c = LRUCache(maxsize=2)
        c.update({"a": 1, "b": 2, "c": 3})
        assert len(c) == 2 and "a" not in c

    @pytest.mark.parametrize("maxsize", [1, 2, 3, 10])  # BVA: maxsize values
    def test_len_capped_at_maxsize(self, maxsize):
        c = LRUCache(maxsize=maxsize)
        for i in range(maxsize + 5):
            c[i] = i
        assert len(c) == maxsize
