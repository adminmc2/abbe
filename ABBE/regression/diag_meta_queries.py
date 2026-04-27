"""
Test de regresión: meta-queries de catálogo / portafolio
Verifica que queries genéricas sobre el catálogo de productos
retornan Q&A #105 con score suficiente (no caen a LOW/external).

Bloque: 2.7 (meta-queries)
Modo: offline (no requiere servidor)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rag_engine import get_rag_engine

# Queries a probar con score mínimo esperado
META_QUERY_CASES = [
    # Formales
    ("¿Qué productos tiene Above Pharma?", 105, 10.0),
    ("¿Cuál es el catálogo completo de Above Pharma?", 105, 10.0),
    ("¿Qué portafolio de productos ofrece Gencell?", 105, 10.0),
    ("¿Cuántos productos vende Above Pharma?", 105, 10.0),
    # Coloquiales (rep latinoamericano)
    ("dame la lista de productos", 105, 8.0),
    ("quiero la lista de todo el catálogo de productos", 105, 8.0),
    ("qué ofrece above pharma", 105, 8.0),
    ("qué vende gencell", 105, 8.0),
    ("que productos manejan", 105, 5.0),
    # NOTE: "que tienen ustedes" is too vague for BM25 (no pharma keywords).
    # In production, is_greeting_or_vague() would catch it before RAG.
    # Con typos comunes
    ("catalogo de productos", 105, 8.0),
    ("portafolio completo", 105, 8.0),
]

# Queries específicas que NO deben retornar Q&A #105 como top result
NEGATIVE_CASES = [
    ("¿Qué es el CTM Estabilizador Renal?", 105),  # Debe retornar Q&A 2-4, no 105
    ("indicaciones de la CTM Metabólica", 105),      # Debe retornar Q&As de Metabólica
]


def main():
    rag = get_rag_engine()
    passed = 0
    failed = 0
    total = len(META_QUERY_CASES) + len(NEGATIVE_CASES)

    print(f"{'=' * 70}")
    print(f"  DIAG: Meta-queries de catálogo ({total} casos)")
    print(f"{'=' * 70}")

    # Positive cases: must hit Q&A #105 with min score
    print(f"\n  --- Positive cases (must hit Q&A #105) ---")
    for query, expected_qa_id, min_score in META_QUERY_CASES:
        results = rag.search(query, top_k=3)
        if not results:
            print(f"  FAIL  | {query}")
            print(f"         No results returned")
            failed += 1
            continue

        top_qa, top_score = results[0]
        top_id = top_qa.get('id')
        hit = top_id == expected_qa_id and top_score >= min_score

        if hit:
            print(f"  PASS  | score={top_score:6.2f} (>={min_score}) | Q{top_id} | {query[:50]}")
            passed += 1
        else:
            print(f"  FAIL  | score={top_score:6.2f} (need>={min_score}) | Q{top_id} (need Q{expected_qa_id}) | {query[:50]}")
            failed += 1

    # Negative cases: specific queries must NOT have Q&A #105 as top result
    print(f"\n  --- Negative cases (must NOT hit Q&A #105 as top) ---")
    for query, forbidden_top_id in NEGATIVE_CASES:
        results = rag.search(query, top_k=3)
        if not results:
            print(f"  FAIL  | {query} — no results")
            failed += 1
            continue

        top_qa, top_score = results[0]
        top_id = top_qa.get('id')
        hit = top_id != forbidden_top_id

        if hit:
            print(f"  PASS  | Q{top_id} (not Q{forbidden_top_id}) score={top_score:6.2f} | {query[:50]}")
            passed += 1
        else:
            print(f"  FAIL  | Q{top_id} == Q{forbidden_top_id} (should not be top) | {query[:50]}")
            failed += 1

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 70}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
