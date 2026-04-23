"""
Diagnóstico Bloque 2.5 — Runtime (4 cases via WebSocket)
Valida que el LLM respeta effective_mode en respuestas reales.
Requiere servidor corriendo en puerto 7862.
"""
import asyncio
import json
import websockets

BASE = "ws://localhost:7862"

CASES = [
    {
        "id": 1,
        "label": "Cobertura alta — respuesta normal",
        "query": "¿Qué es el CTM Estabilizador Renal?",
        "expect_mode": "normal",
    },
    {
        "id": 2,
        "label": "Comparativa competidor — rechazo",
        "query": "¿Es mejor Gencell que Regen-Stem?",
        "expect_mode": "rechazo",
    },
    {
        "id": 3,
        "label": "Query fuera de KB — rechazo/acotada",
        "query": "¿Se puede usar CTM para lupus?",
        "expect_mode": "acotada",
    },
    {
        "id": 4,
        "label": "Comparativa interna — permitida",
        "query": "¿Qué diferencia hay entre CTM Renal y CTM Metabólica?",
        "expect_mode": "normal",
    },
]

async def run_case(case):
    uri = f"{BASE}/ws/chat"
    full_response = ""
    agent_info = {}
    try:
        async with websockets.connect(uri, close_timeout=15) as ws:
            payload = {"message": case["query"], "mode": "productos"}
            await ws.send(json.dumps(payload))
            async for msg in ws:
                data = json.loads(msg)
                if data.get("type") == "agent_info":
                    agent_info = data
                elif data.get("type") == "stream":
                    full_response += data.get("content", "")
                elif data.get("type") == "end":
                    break
    except Exception as e:
        full_response = f"[ERROR: {e}]"
    return full_response, agent_info

async def main():
    print("=" * 70)
    print("  DIAGNÓSTICO 2.5 — 4 cases runtime")
    print("=" * 70)

    passed = 0
    for case in CASES:
        print(f"\n--- Case {case['id']}: {case['label']}")
        print(f"  Query: {case['query']}")
        response, info = await run_case(case)
        coverage = info.get("rag_coverage", "?")
        agent = info.get("agent", "?")
        max_score = info.get("max_score", "?")
        print(f"  Agent: {agent}, RAG coverage: {coverage}, max_score: {max_score}")
        print(f"  Response preview: {response[:200]}...")
        print(f"  Expected mode: {case['expect_mode']}")

        # Verificación básica
        if case["expect_mode"] == "rechazo":
            has_refusal = any(w in response.lower() for w in ["no cuento con", "no dispongo", "no puedo comparar", "fuera de", "no tengo información"])
            print(f"  Refusal detected: {has_refusal}")
            if has_refusal:
                passed += 1
        else:
            has_content = len(response) > 100
            print(f"  Has substantial content: {has_content}")
            if has_content:
                passed += 1

    print(f"\n{'=' * 70}")
    print(f"  Passed: {passed}/{len(CASES)}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    asyncio.run(main())
