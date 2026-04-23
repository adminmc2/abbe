"""
Diagnóstico Bloque 2.3 — Retrieval RAG (BM25 + fallback)
Valida scores, cobertura, categorías y fallback auditable.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.rag_engine import get_rag_engine
from agents.orchestrator import get_orchestrator

rag = get_rag_engine()
orchestrator = get_orchestrator()

QUERIES = [
    # Cobertura alta esperada
    ("¿Qué es el CTM Estabilizador Renal?", "high"),
    ("¿Cuáles son las indicaciones del CTM Metabólica?", "high"),
    ("¿Cómo funciona el pretratamiento con melatonina?", "high"),
    ("¿Qué es Gencell Biotechnology?", "high"),
    # Cobertura media esperada
    ("¿Cómo manejar la objeción de precio?", "medium"),
    ("¿Qué diferencia hay entre Renal y Metabólica?", "medium"),
    # Cobertura baja/nula esperada
    ("¿Cuánto cuesta exactamente el tratamiento?", "low"),
    ("¿Se puede usar para cáncer?", "low"),
    ("Háblame de política internacional", "no_results"),
    # Fallback esperado (query no matchea categorías del agente)
    ("¿Cómo convencer a un internista?", "medium"),
]

def classify_coverage(results):
    max_score = max((r[1] for r in results), default=0.0)
    strong = [r for r in results if r[1] >= 10.0]
    if not results or max_score == 0:
        return "no_results", max_score
    elif max_score >= 10.0 and len(strong) >= 2:
        return "high", max_score
    elif max_score >= 5.0:
        return "medium", max_score
    else:
        return "low", max_score

def main():
    print("=" * 70)
    print("  DIAGNÓSTICO 2.3 — Retrieval RAG")
    print("=" * 70)

    agent = orchestrator.get_agent("productos")
    passed = 0

    for query, expected_coverage in QUERIES:
        results = rag.search(query, top_k=5)
        coverage, max_score = classify_coverage(results)
        relevant = [r for r in results if r[1] >= 3.0]

        # Fallback test
        fb_results, meta = agent.search_knowledge_with_fallback(query)

        ok = coverage == expected_coverage
        status = "✓" if ok else "~"
        print(f"\n  {status} {query[:55]}")
        print(f"    Coverage: {coverage} (expected: {expected_coverage}), max_score: {max_score:.2f}")
        print(f"    Docs: {len(results)}, relevant(>=3.0): {len(relevant)}")
        print(f"    Fallback: {meta.get('fallback_activated', False)}")
        if results:
            top = results[0]
            print(f"    Top: [{top[0]['categoria']}] score={top[1]:.2f} → {top[0]['pregunta'][:50]}")
        if ok:
            passed += 1

    print(f"\n  Matched: {passed}/{len(QUERIES)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
