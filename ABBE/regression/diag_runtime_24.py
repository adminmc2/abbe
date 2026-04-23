"""
Diagnóstico Bloque 2.4 — Runtime (coherencia agente↔retrieval)
Valida que el agente seleccionado recibe contexto coherente
y que el effective_mode se aplica correctamente.
Requiere servidor corriendo en puerto 7862.
"""
import asyncio
import json
import websockets

BASE = "ws://localhost:7862"

CASES = [
    {
        "query": "¿Qué es el CTM Estabilizador Renal?",
        "expect_agent": "productos",
        "expect_coverage": "high",
        "label": "Producto principal",
    },
    {
        "query": "El doctor dice que es caro, ¿cómo respondo?",
        "expect_agent": "objeciones",
        "expect_coverage": "medium",
        "label": "Objeción de precio",
    },
    {
        "query": "¿Cómo presento las CTM a un nefrólogo?",
        "expect_agent": "argumentos",
        "expect_coverage": "medium",
        "label": "Argumento por especialidad",
    },
    {
        "query": "¿Se puede usar para alzheimer?",
        "expect_agent": "productos",
        "expect_coverage": "low",
        "label": "Indicación no soportada",
    },
]

async def run_case(case):
    uri = f"{BASE}/ws/chat"
    full_response = ""
    agent_info = {}
    try:
        async with websockets.connect(uri, close_timeout=15) as ws:
            payload = {"message": case["query"], "mode": case.get("mode", "auto")}
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
    print("  DIAGNÓSTICO 2.4 — Runtime coherencia agente↔retrieval")
    print("=" * 70)

    passed = 0
    for case in CASES:
        print(f"\n--- {case['label']}: {case['query'][:50]}")
        response, info = await run_case(case)
        agent = info.get("agent", "?")
        coverage = info.get("rag_coverage", "?")
        max_score = info.get("max_score", 0)
        docs = info.get("context_docs", 0)

        agent_ok = agent == case["expect_agent"]
        print(f"  Agent: {agent} {'✓' if agent_ok else '✗ expected ' + case['expect_agent']}")
        print(f"  Coverage: {coverage} (expected: {case['expect_coverage']}), max_score: {max_score}")
        print(f"  Docs: {docs}")
        print(f"  Response: {response[:150]}...")
        if agent_ok:
            passed += 1

    print(f"\n{'=' * 70}")
    print(f"  Agent match: {passed}/{len(CASES)}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    asyncio.run(main())
