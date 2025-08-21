import tempfile
from nova_prime.memory.store import MemoryStore

def test_memory_store_add_and_query(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        monkeypatch.setenv("XDG_DATA_HOME", td)
        store = MemoryStore()
        ev = store.add_event("testuser", "note", {"text": "ciao"})
        assert ev.user_id == "testuser"
        res = store.query(user_id="testuser")
        assert len(res) >= 1
        assert any(r.data.get("text") == "ciao" for r in res)