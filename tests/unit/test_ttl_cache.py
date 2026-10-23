import pytest
from cachetools import TTLCache


class Timer:
    """Fake clock so tests never sleep."""

    def __init__(self):
        self.t = 0

    def __call__(self):
        return self.t

    def tick(self, n):
        self.t += n


def make(maxsize=3, ttl=10, **items):
    timer = Timer()
    c = TTLCache(maxsize=maxsize, ttl=ttl, timer=timer)
    for k, v in items.items():
        c[k] = v
    return c, timer


# ---------------------------------------------------------------- __setitem__
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLSetItem:
    def test_insert_single(self):  # ECP: valid
        c, _ = make(2)
        c["a"] = 1
        assert c["a"] == 1

    def test_below_capacity(self):  # BVA: n-1
        c, _ = make(3, a=1, b=2)
        assert len(c) == 2

    def test_at_capacity(self):  # BVA: n
        c, _ = make(3, a=1, b=2, c=3)
        assert len(c) == 3

    def test_over_capacity_evicts_oldest(self):  # BVA: n+1
        c, _ = make(2, a=1, b=2)
        c["c"] = 3
        assert "a" not in c and len(c) == 2

    def test_overwrite_keeps_size(self):  # ECP: existing key
        c, _ = make(2, a=1)
        c["a"] = 9
        assert c["a"] == 9 and len(c) == 1

    def test_overwrite_resets_ttl(self):  # BVA: ttl restarts
        c, t = make(2, a=1)
        t.tick(5)
        c["a"] = 2
        t.tick(7)
        assert "a" in c

    def test_maxsize_zero_rejects_insert(self):  # BVA: min maxsize
        c = TTLCache(maxsize=0, ttl=10, timer=Timer())
        with pytest.raises(ValueError):
            c["a"] = 1


# ---------------------------------------------------------------- __getitem__
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLGetItem:
    def test_existing_key(self):  # ECP: valid
        c, _ = make(2, a=1)
        assert c["a"] == 1

    def test_missing_key_raises(self):  # ECP: invalid
        c, _ = make(2)
        with pytest.raises(KeyError):
            c["x"]

    def test_get_before_ttl(self):  # BVA: ttl-1
        c, t = make(2, a=1)
        t.tick(9)
        assert c["a"] == 1

    def test_get_at_ttl_raises(self):  # BVA: ttl
        c, t = make(2, a=1)
        t.tick(10)
        with pytest.raises(KeyError):
            c["a"]

    def test_get_after_ttl_raises(self):  # BVA: ttl+1
        c, t = make(2, a=1)
        t.tick(11)
        with pytest.raises(KeyError):
            c["a"]

    def test_get_does_not_refresh_ttl(self):  # ECP: access vs write
        c, t = make(2, a=1)
        t.tick(5)
        _ = c["a"]
        t.tick(6)
        assert "a" not in c


# ---------------------------------------------------------------- __delitem__
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLDelItem:
    def test_delete_existing(self):  # ECP: valid
        c, _ = make(2, a=1)
        del c["a"]
        assert "a" not in c

    def test_delete_missing_raises(self):  # ECP: invalid
        c, _ = make(2)
        with pytest.raises(KeyError):
            del c["a"]

    def test_delete_reduces_len(self):  # BVA: n -> n-1
        c, _ = make(2, a=1, b=2)
        del c["a"]
        assert len(c) == 1

    def test_delete_expired_raises(self):  # BVA: ttl+1
        c, t = make(2, a=1)
        t.tick(11)
        with pytest.raises(KeyError):
            del c["a"]

    def test_delete_twice_raises(self):  # ECP: invalid
        c, _ = make(2, a=1)
        del c["a"]
        with pytest.raises(KeyError):
            del c["a"]


# ---------------------------------------------------------------------- pop
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLPop:
    def test_pop_existing(self):  # ECP: valid
        c, _ = make(2, a=1)
        assert c.pop("a") == 1 and "a" not in c

    def test_pop_missing_raises(self):  # ECP: invalid
        c, _ = make(2)
        with pytest.raises(KeyError):
            c.pop("a")

    def test_pop_missing_with_default(self):  # ECP: invalid + default
        c, _ = make(2)
        assert c.pop("a", 42) == 42

    def test_pop_expired_returns_default(self):  # BVA: ttl+1
        c, t = make(2, a=1)
        t.tick(11)
        assert c.pop("a", "gone") == "gone"

    def test_pop_before_ttl(self):  # BVA: ttl-1
        c, t = make(2, a=1)
        t.tick(9)
        assert c.pop("a") == 1

    def test_pop_reduces_len(self):  # BVA: n -> n-1
        c, _ = make(2, a=1, b=2)
        c.pop("a")
        assert len(c) == 1


# ------------------------------------------------------------------ popitem
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLPopItem:
    def test_popitem_returns_oldest(self):  # ECP: valid
        c, t = make(3)
        c["a"] = 1
        t.tick(1)
        c["b"] = 2
        assert c.popitem() == ("a", 1)

    def test_popitem_empty_raises(self):  # BVA: empty
        c, _ = make(2)
        with pytest.raises(KeyError):
            c.popitem()

    def test_popitem_single_item(self):  # BVA: size 1
        c, _ = make(2, a=1)
        assert c.popitem() == ("a", 1) and len(c) == 0

    def test_popitem_skips_expired(self):  # BVA: ttl+1
        c, t = make(3, a=1)
        t.tick(6)
        c["b"] = 2
        t.tick(5)
        assert c.popitem() == ("b", 2)

    def test_popitem_all_expired_raises(self):  # BVA: all expired
        c, t = make(2, a=1, b=2)
        t.tick(11)
        with pytest.raises(KeyError):
            c.popitem()


# ---------------------------------------------------------------------- get
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLGet:
    def test_get_existing(self):  # ECP: valid
        c, _ = make(2, a=1)
        assert c.get("a") == 1

    def test_get_missing_returns_none(self):  # ECP: invalid
        c, _ = make(2)
        assert c.get("a") is None

    def test_get_missing_with_default(self):  # ECP: invalid + default
        c, _ = make(2)
        assert c.get("a", 7) == 7

    def test_get_expired_returns_default(self):  # BVA: ttl+1
        c, t = make(2, a=1)
        t.tick(11)
        assert c.get("a", "d") == "d"

    def test_get_at_ttl_returns_default(self):  # BVA: ttl
        c, t = make(2, a=1)
        t.tick(10)
        assert c.get("a", "d") == "d"


# --------------------------------------------------------------- setdefault
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLSetDefault:
    def test_setdefault_new_key(self):  # ECP: missing
        c, _ = make(2)
        assert c.setdefault("a", 5) == 5 and c["a"] == 5

    def test_setdefault_existing_key(self):  # ECP: present
        c, _ = make(2, a=1)
        assert c.setdefault("a", 5) == 1

    def test_setdefault_no_default_is_none(self):  # ECP: default omitted
        c, _ = make(2)
        assert c.setdefault("a") is None and "a" in c

    def test_setdefault_expired_key_is_replaced(self):  # BVA: ttl+1
        c, t = make(2, a=1)
        t.tick(11)
        assert c.setdefault("a", 9) == 9

    def test_setdefault_at_capacity_evicts(self):  # BVA: n+1
        c, _ = make(2, a=1, b=2)
        c.setdefault("c", 3)
        assert "a" not in c and len(c) == 2


# ----------------------------------------------- ttl / maxsize / currsize
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLProperties:
    def test_ttl_value(self):  # ECP: valid
        assert TTLCache(maxsize=2, ttl=10, timer=Timer()).ttl == 10

    def test_maxsize_value(self):  # ECP: valid
        assert TTLCache(maxsize=5, ttl=10, timer=Timer()).maxsize == 5

    def test_currsize_empty(self):  # BVA: 0
        c, _ = make(5)
        assert c.currsize == 0

    def test_currsize_after_inserts(self):  # ECP: valid
        c, _ = make(5, a=1, b=2)
        assert c.currsize == 2

    def test_currsize_drops_after_expiry(self):  # BVA: ttl
        c, t = make(5, a=1, b=2)
        t.tick(10)
        assert c.currsize == 0

    def test_ttl_zero_expires_immediately(self):  # BVA: min ttl
        c = TTLCache(maxsize=2, ttl=0, timer=Timer())
        c["a"] = 1
        assert "a" not in c


# ------------------------------------------------------- expiry boundaries
@pytest.mark.unit
@pytest.mark.ttl
class TestTTLExpiry:
    @pytest.mark.parametrize(
        "elapsed,alive",
        [(0, True), (9, True), (10, False), (11, False)],  # BVA around ttl=10
    )
    def test_membership_at_elapsed_time(self, elapsed, alive):
        c, t = make(2, ttl=10, a=1)
        t.tick(elapsed)
        assert ("a" in c) is alive

    def test_items_expire_independently(self):  # ECP
        c, t = make(3)
        c["a"] = 1
        t.tick(6)
        c["b"] = 2
        t.tick(5)
        assert "a" not in c and "b" in c

    def test_len_excludes_expired(self):
        c, t = make(3, a=1, b=2)
        t.tick(11)
        assert len(c) == 0


# ------------------------------------------------------- class / module level
@pytest.mark.module
@pytest.mark.ttl
class TestTTLCacheModule:
    def test_new_cache_is_empty(self):
        c, _ = make(3)
        assert len(c) == 0

    def test_eviction_order_is_oldest_first(self):
        c, _ = make(3, a=1, b=2, c=3)
        c["d"] = 4
        c["e"] = 5
        assert "a" not in c and "b" not in c and "c" in c

    def test_contains_for_present_and_absent(self):
        c, _ = make(2, a=1)
        assert "a" in c and "z" not in c

    def test_clear_empties_cache(self):
        c, _ = make(3, a=1, b=2)
        c.clear()
        assert len(c) == 0

    def test_update_inserts_multiple(self):
        c, _ = make(5)
        c.update({"a": 1, "b": 2})
        assert len(c) == 2

    def test_update_over_capacity_evicts(self):
        c, _ = make(2)
        c.update({"a": 1, "b": 2, "c": 3})
        assert len(c) == 2 and "a" not in c

    def test_expired_slot_is_reusable(self):
        c, t = make(1, a=1)
        t.tick(11)
        c["b"] = 2
        assert c["b"] == 2 and len(c) == 1

    @pytest.mark.parametrize("maxsize", [1, 2, 3, 10])  # BVA: maxsize values
    def test_len_capped_at_maxsize(self, maxsize):
        c, _ = make(maxsize)
        for i in range(maxsize + 5):
            c[i] = i
        assert len(c) == maxsize
