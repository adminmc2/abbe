"""
Diagnóstico Bloque 2.5 — NO RESULTS y anti-fabricación (Fase A: offline)
10 queries diseñadas para probar detección de comparativas,
cobertura RAG y comportamiento de fallback.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.rag_engine import get_rag_engine
from agents.orchestrator import get_orchestrator

rag = get_rag_engine()
orchestrator = get_orchestrator()

QUERIES = [
    # Q1-Q3: Queries con cobertura alta esperada
    "¿Qué es el CTM Estabilizador Renal?",
    "¿Cuáles son las indicaciones del CTM Metabólica?",
    "¿Cómo funciona el pretratamiento con melatonina?",
    # Q4-Q6: Queries con cobertura baja/nula esperada
    "¿Cuánto cuesta el tratamiento CTM?",
    "¿Es mejor Gencell que Regen-Stem?",
    "¿Se puede usar CTM para lupus?",
    # Q7-Q8: Comparativas internas (permitidas)
    "¿Qué diferencia hay entre CTM Renal y CTM Metabólica?",
    "¿Cuál de los dos productos es más indicado para diabetes?",
    # Q9-Q10: Comparativas de competidor (rechazadas si no hay competidores en catálogo)
    "¿Es mejor que las células madre de otra marca?",
    "¿Por qué elegir Gencell y no otro laboratorio?",
]

def classify_rag_coverage(results):
    max_score = max((r[1] for r in results), default=0.0)
    strong_docs = [r for r in results if r[1] >= 10.0]
    if not results or max_score == 0:
        return "no_results", max_score
    elif max_score >= 10.0 and len(strong_docs) >= 2:
        return "high", max_score
    elif max_score >= 5.0:
        return "medium", max_score
    else:
        return "low", max_score

def main():
    agent = orchestrator.get_agent("productos")
    print("=" * 70)
    print("  DIAGNÓSTICO 2.5 — 10 queries offline")
    print("=" * 70)

    for i, query in enumerate(QUERIES, 1):
        print(f"\n--- Q{i}: {query}")

        # Intent
        intent = orchestrator.classify_intent_rules(query)
        print(f"  Intent (rules): {intent}")

        # RAG search
        results = rag.search(query, top_k=5)
        coverage, max_score = classify_rag_coverage(results)
        relevant = [r for r in results if r[1] >= 3.0]
        print(f"  RAG: {len(results)} docs, max_score={max_score:.2f}, coverage={coverage}")
        print(f"  Relevant (>=3.0): {len(relevant)} docs")

        # Fallback
        fb_results, search_meta = agent.search_knowledge_with_fallback(query)
        print(f"  Fallback: activated={search_meta.get('fallback_activated')}")

        # Comparative
        comp = agent.evaluate_comparative_query(query, results)
        if comp["is_comparative"]:
            print(f"  Comparative: type={comp['type']}, allowed={comp['allowed']}, reason={comp['reason']}")
        else:
            print(f"  Comparative: no")

        # Top 3 results
        for j, (qa, score) in enumerate(results[:3]):
            print(f"    [{j+1}] score={score:.2f} cat={qa['categoria']} → {qa['pregunta'][:60]}")

    print("\n" + "=" * 70)
    print("  FIN DIAGNÓSTICO 2.5 OFFLINE")
    print("=" * 70)

if __name__ == "__main__":
    main()
