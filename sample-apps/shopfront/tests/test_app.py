import pytest
from fastapi.testclient import TestClient

import app as shop

client = TestClient(shop.app)


@pytest.fixture(autouse=True)
def reset_state():
    shop.state["mode"] = "normal"
    shop.leaked_memory.clear()
    yield
    shop.state["mode"] = "normal"
    shop.leaked_memory.clear()


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "mode": "normal"}


def test_checkout_normal():
    r = client.get("/checkout")
    assert r.status_code == 200
    assert r.json()["order"] == "confirmed"


def test_set_valid_mode():
    r = client.post("/admin/mode/slow")
    assert r.status_code == 200
    assert shop.state["mode"] == "slow"


def test_set_invalid_mode_rejected():
    r = client.post("/admin/mode/explode")
    assert r.status_code == 400
    assert shop.state["mode"] == "normal"


def test_slow_mode_calls_sleep(monkeypatch):
    calls = []
    monkeypatch.setattr(shop.time, "sleep", lambda s: calls.append(s))
    client.post("/admin/mode/slow")
    r = client.get("/checkout")
    assert r.status_code == 200
    assert calls == [3]


def test_leak_mode_grows_memory():
    client.post("/admin/mode/leak")
    client.get("/checkout")
    assert len(shop.leaked_memory) == 1


def test_crash_mode_exits(monkeypatch):
    exit_codes = []
    monkeypatch.setattr(shop.os, "_exit", lambda code: exit_codes.append(code))
    client.post("/admin/mode/crash")
    client.get("/checkout")
    assert exit_codes == [1]
