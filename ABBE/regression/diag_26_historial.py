"""
Diagnóstico Bloque 2.6 — Persistencia y aislamiento de historial
Valida endpoints save/load, app_id scope, aislamiento por usuario.
Requiere servidor corriendo en puerto 7862.
"""
import requests
import json

BASE = "http://localhost:7862"
APP_ID = "abbe_above_pharma"

def save_history(username, searches, app_id=None):
    payload = {"username": username, "searches": searches}
    if app_id:
        payload["app_id"] = app_id
    r = requests.post(f"{BASE}/api/history/save", json=payload)
    return r.status_code, r.json()

def load_history(username, app_id=None):
    payload = {"username": username}
    if app_id:
        payload["app_id"] = app_id
    r = requests.post(f"{BASE}/api/history/load", json=payload)
    return r.status_code, r.json()

def check(label, condition, detail=""):
    status = "✓" if condition else "✗"
    suffix = f" — {detail}" if detail and not condition else ""
    print(f"  {status} {label}{suffix}")
    return condition

def main():
    passed = 0
    total = 0

    print("=" * 60)
    print("  DIAGNÓSTICO 2.6 — Historial por usuario")
    print("=" * 60)

    # Test 1: Usuario nuevo sin historial
    print("\n--- Test 1: Usuario nuevo (sin datos)")
    status, data = load_history("test_26_new", APP_ID)
    total += 2
    if check("Status 200", status == 200): passed += 1
    if check("Searches vacío", len(data.get("searches", [])) == 0): passed += 1

    # Test 2: Guardar historial para user A
    print("\n--- Test 2: Save user A")
    searches_a = [
        {"query": "Test A query 1", "icon": "product", "desc": "test", "timestamp": 1000},
        {"query": "Test A query 2", "icon": "product", "desc": "test", "timestamp": 2000},
    ]
    status, resp = save_history("test_26_a", searches_a, APP_ID)
    total += 2
    if check("Status 200", status == 200): passed += 1
    if check("Saved 2", resp.get("saved") == 2, f"got {resp.get('saved')}"): passed += 1

    # Test 3: Load user A
    print("\n--- Test 3: Load user A")
    status, data = load_history("test_26_a", APP_ID)
    total += 2
    if check("Status 200", status == 200): passed += 1
    if check("2 searches", len(data.get("searches", [])) == 2, f"got {len(data.get('searches', []))}"): passed += 1

    # Test 4: Guardar historial para user B
    print("\n--- Test 4: Save user B")
    searches_b = [
        {"query": "Test B query 1", "icon": "objection", "desc": "test", "timestamp": 3000},
        {"query": "Test B query 2", "icon": "argument", "desc": "test", "timestamp": 4000},
    ]
    status, resp = save_history("test_26_b", searches_b, APP_ID)
    total += 1
    if check("Saved 2", resp.get("saved") == 2): passed += 1

    # Test 5: Aislamiento A ↔ B
    print("\n--- Test 5: Aislamiento")
    _, data_a = load_history("test_26_a", APP_ID)
    _, data_b = load_history("test_26_b", APP_ID)
    queries_a = [s["query"] for s in data_a.get("searches", [])]
    queries_b = [s["query"] for s in data_b.get("searches", [])]
    total += 2
    if check("A no contiene queries de B", not any(q in queries_a for q in ["Test B query 1", "Test B query 2"])): passed += 1
    if check("B no contiene queries de A", not any(q in queries_b for q in ["Test A query 1", "Test A query 2"])): passed += 1

    # Test 6: app_id scope — sin app_id no ve datos con app_id
    print("\n--- Test 6: Scope app_id")
    _, data_no_app = load_history("test_26_a")  # sin app_id
    total += 1
    no_app_searches = data_no_app.get("searches", [])
    if check("Sin app_id no ve datos scoped", len(no_app_searches) == 0 or "Test A query 1" not in [s.get("query") for s in no_app_searches]): passed += 1

    # Test 7: Legacy user intacto
    print("\n--- Test 7: Legacy intacto")
    _, legacy = load_history("José Luis")  # sin app_id, lee raíz
    total += 1
    if check("Legacy accesible", legacy.get("searches") is not None): passed += 1

    print(f"\n{'=' * 60}")
    print(f"  Passed: {passed}/{total}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
