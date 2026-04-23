"""
Diagnóstico final Bloque 2.6 — Evidencia runtime para cierre
Simula flujo completo: qa_26_a → logout → qa_26_b → vuelta a qa_26_a
Valida: persistencia, aislamiento, trazabilidad
"""
import requests
import asyncio
import websockets
import json
import time

BASE = "http://localhost:7862"
WS_BASE = "ws://localhost:7862"
APP_ID = "abbe_above_pharma"
USER_A = "qa_26_a"
USER_B = "qa_26_b"

QUERIES_A = [
    "¿Qué es el CTM Estabilizador Renal?",
    "¿Cuáles son las indicaciones del CTM Metabólica?"
]
QUERIES_B = [
    "¿Cómo manejar la objeción de precio alto?",
    "¿Qué diferencia hay entre Renal y Metabólica?"
]

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(f"  ✗ {label} — {detail}")

def save_history(username, searches):
    r = requests.post(f"{BASE}/api/history/save", json={
        "username": username,
        "searches": searches,
        "app_id": APP_ID
    })
    return r.status_code, r.json()

def load_history(username):
    r = requests.post(f"{BASE}/api/history/load", json={
        "username": username,
        "app_id": APP_ID
    })
    return r.status_code, r.json()

async def ws_query(query, username):
    """Envía una consulta por WebSocket y retorna la respuesta completa."""
    uri = f"{WS_BASE}/ws/chat"
    full_response = ""
    try:
        async with websockets.connect(uri, close_timeout=10) as ws:
            payload = {
                "message": query,
                "mode": "productos",
                "username": username
            }
            await ws.send(json.dumps(payload))
            async for msg in ws:
                data = json.loads(msg)
                if data.get("type") == "stream":
                    full_response += data.get("content", "")
                elif data.get("type") == "end":
                    break
    except Exception as e:
        full_response = f"[ERROR: {e}]"
    return full_response

async def run_queries(queries, username):
    """Ejecuta queries secuencialmente para un usuario."""
    results = []
    for q in queries:
        resp = await ws_query(q, username)
        results.append({"query": q, "answer": resp[:100], "timestamp": int(time.time() * 1000)})
    return results

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

async def main():
    global passed, failed

    # PASO 0: Limpiar estado previo de test
    print_section("PASO 0: Limpiar estado previo")
    save_history(USER_A, [])
    save_history(USER_B, [])
    print("  Historiales de qa_26_a y qa_26_b reseteados")

    # PASO 1: Login qa_26_a → 2 consultas
    print_section("PASO 1: Login qa_26_a + 2 consultas")
    results_a = await run_queries(QUERIES_A, USER_A)
    print(f"  Consultas realizadas: {len(results_a)}")
    for r in results_a:
        print(f"    → {r['query'][:50]}... ({len(r['answer'])} chars)")

    searches_a = [{"query": r["query"], "icon": "product", "desc": "test", "timestamp": r["timestamp"], "answer": r["answer"]} for r in results_a]
    status, resp = save_history(USER_A, searches_a)
    check("Save qa_26_a: status 200", status == 200)
    check("Save qa_26_a: saved count", resp.get("saved") == 2, f"got {resp.get('saved')}")

    # PASO 2: Simular recarga — load qa_26_a
    print_section("PASO 2: Recarga qa_26_a (simula reload)")
    status, data = load_history(USER_A)
    check("Load qa_26_a: status 200", status == 200)
    check("Load qa_26_a: 2 searches", len(data.get("searches", [])) == 2, f"got {len(data.get('searches', []))}")
    if data.get("searches"):
        check("Load qa_26_a: query correcta", data["searches"][0]["query"] == QUERIES_A[0])
    print(f"  Network: POST /api/history/load → username={USER_A}, app_id={APP_ID}")
    print(f"  Response: searches={len(data.get('searches', []))}, last_sync={data.get('last_sync')}")

    # PASO 3: Logout qa_26_a → Login qa_26_b → 2 consultas distintas
    print_section("PASO 3: Logout A → Login qa_26_b + 2 consultas")
    results_b = await run_queries(QUERIES_B, USER_B)
    print(f"  Consultas realizadas: {len(results_b)}")
    for r in results_b:
        print(f"    → {r['query'][:50]}... ({len(r['answer'])} chars)")

    searches_b = [{"query": r["query"], "icon": "objection", "desc": "test", "timestamp": r["timestamp"], "answer": r["answer"]} for r in results_b]
    status, resp = save_history(USER_B, searches_b)
    check("Save qa_26_b: status 200", status == 200)
    check("Save qa_26_b: saved count", resp.get("saved") == 2, f"got {resp.get('saved')}")

    # PASO 4: Recarga qa_26_b — no ve nada de qa_26_a
    print_section("PASO 4: Recarga qa_26_b (aislamiento)")
    status, data_b = load_history(USER_B)
    check("Load qa_26_b: status 200", status == 200)
    check("Load qa_26_b: 2 searches", len(data_b.get("searches", [])) == 2, f"got {len(data_b.get('searches', []))}")
    all_queries_b = [s["query"] for s in data_b.get("searches", [])]
    has_a_data = any(q in all_queries_b for q in QUERIES_A)
    check("Aislamiento: qa_26_b NO contiene queries de A", not has_a_data, f"found: {all_queries_b}")

    # PASO 5: Volver a qa_26_a — recupera solo lo suyo
    print_section("PASO 5: Volver a qa_26_a (persistencia)")
    status, data_a2 = load_history(USER_A)
    check("Load qa_26_a (vuelta): status 200", status == 200)
    check("Load qa_26_a (vuelta): 2 searches", len(data_a2.get("searches", [])) == 2, f"got {len(data_a2.get('searches', []))}")
    all_queries_a = [s["query"] for s in data_a2.get("searches", [])]
    has_b_data = any(q in all_queries_a for q in QUERIES_B)
    check("Aislamiento: qa_26_a NO contiene queries de B", not has_b_data, f"found: {all_queries_a}")
    check("Persistencia: qa_26_a conserva su query original", QUERIES_A[0] in all_queries_a)

    # PASO 6: Persistencia backend
    print_section("PASO 6: Persistencia en user_data.json")
    try:
        with open("user_data.json", "r") as f:
            ud = json.load(f)
        for user in [USER_A, USER_B]:
            user_data = ud.get(user, {})
            app_data = user_data.get("apps", {}).get(APP_ID, {})
            user_searches = app_data.get("searches", [])
            check(f"user_data.json: {user}.apps.{APP_ID} existe", len(user_searches) > 0)
            if user_searches:
                for s in user_searches:
                    print(f"      → {s.get('query', '?')[:60]}")
    except Exception as e:
        check("user_data.json legible", False, str(e))

    # PASO 7: Trazabilidad
    print_section("PASO 7: Trazabilidad en audit_traces.jsonl")
    try:
        traces = []
        with open("audit_traces.jsonl", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    traces.append(json.loads(line))
        for user in [USER_A, USER_B]:
            user_traces = [t for t in traces if t.get("frontend_user") == user]
            check(f"audit_traces: {user} tiene trazas", len(user_traces) > 0)
            if user_traces:
                latest = user_traces[-1]
                print(f"      frontend_user: {latest.get('frontend_user')}")
                print(f"      query: {latest.get('query', '?')[:60]}")
                print(f"      session_id: {latest.get('session_id', '?')}")
    except Exception as e:
        check("audit_traces.jsonl legible", False, str(e))

    # RESUMEN
    print_section("RESUMEN FINAL")
    total = passed + failed
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {failed}/{total}")
    if failed == 0:
        print(f"\n  ★ TODOS LOS TESTS PASARON — 2.6 listo para cierre")
    else:
        print(f"\n  ✗ {failed} test(s) fallaron — revisar antes de cerrar")

if __name__ == "__main__":
    asyncio.run(main())
