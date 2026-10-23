import pytest
from cachetools import LFUCache, LRUCache, TTLCache


@pytest.mark.smoke
@pytest.mark.order(1)
def test_lru_basic_insert_and_get():
    c = LRUCache(maxsize=2)
    c["a"] = 1
    assert c["a"] == 1


@pytest.mark.smoke
@pytest.mark.order(2)
def test_ttl_basic_insert_and_get():
    c = TTLCache(maxsize=2, ttl=10, timer=lambda: 0)
    c["a"] = 1
    assert c["a"] == 1


@pytest.mark.smoke
@pytest.mark.order(3)
def test_lfu_basic_insert_and_get():
    c = LFUCache(maxsize=2)
    c["a"] = 1
    assert c["a"] == 1
