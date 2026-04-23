"""
Diagnóstico — Multi-turn conversation
Valida que el contexto previo (priorContext) se envía correctamente
y que el LLM mantiene coherencia entre turnos.
Requiere servidor corriendo en puerto 7862.
"""
import asyncio
import json
import websockets

BASE = "ws://localhost:7862"

CONVERSATIONS = [
    {
        "label": "Follow-up sobre producto",
        "turns": [
            "¿Qué es el CTM Estabilizador Renal?",
            "¿Y cuáles son sus indicaciones?",
            "¿Cómo se administra?",
        ]
    },
    {
        "label": "Cambio de tema",
        "turns": [
            "¿Qué es el CTM Metabólica?",
            "¿Cómo manejar la objeción de precio?",
        ]
    },
]

async def send_message(query):
    uri = f"{BASE}/ws/chat"
    full_response = ""
    agent_info = {}
    try:
        async with websockets.connect(uri, close_timeout=15) as ws:
            payload = {"message": query, "mode": "auto"}
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
    print("  DIAGNÓSTICO — Multi-turn conversations")
    print("=" * 70)

    for conv in CONVERSATIONS:
        print(f"\n{'─' * 50}")
        print(f"  Conversación: {conv['label']}")
        print(f"{'─' * 50}")
        for i, query in enumerate(conv["turns"], 1):
            print(f"\n  Turn {i}: {query}")
            response, info = await send_message(query)
            agent = info.get("agent", "?")
            coverage = info.get("rag_coverage", "?")
            print(f"  Agent: {agent}, Coverage: {coverage}")
            print(f"  Response: {response[:200]}...")

    print(f"\n{'=' * 70}")
    print(f"  Revisión manual de coherencia entre turnos")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    asyncio.run(main())
