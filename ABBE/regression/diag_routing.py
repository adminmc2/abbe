"""
Diagnóstico Bloque 2.2 — Routing de intenciones (frame-based)
Valida classify_intent_rules() contra queries representativas.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

CASES = [
    # (query, expected_intent)
    # Productos
    ("¿Qué es el CTM Estabilizador Renal?", "productos"),
    ("¿Cuáles son las indicaciones?", "productos"),
    ("¿Cómo funciona la melatonina en las CTM?", "productos"),
    ("Háblame de Gencell", "productos"),
    ("¿Qué productos tienen?", "productos"),
    # Objeciones
    ("El doctor dice que es muy caro", "objeciones"),
    ("No estoy seguro de la eficacia", "objeciones"),
    ("¿Y si el paciente tiene efectos adversos?", "objeciones"),
    ("El médico prefiere tratamientos convencionales", "objeciones"),
    ("¿Cómo manejo la objeción de precio?", "objeciones"),
    # Argumentos
    ("¿Cómo presento esto a un internista?", "argumentos"),
    ("Dame argumentos para un nefrólogo", "argumentos"),
    ("¿Cómo convencer al doctor?", "argumentos"),
    ("Estrategia de venta para endocrinólogo", "argumentos"),
    # Ambiguos / edge cases
    ("Hola", "productos"),
    ("Gracias", "productos"),
    ("¿Qué me recomiendas?", "productos"),
]

def main():
    print("=" * 70)
    print("  DIAGNÓSTICO 2.2 — Routing de intenciones")
    print("=" * 70)

    passed = 0
    for query, expected in CASES:
        intent = orchestrator.classify_intent_rules(query)
        ok = intent == expected
        status = "✓" if ok else "✗"
        extra = "" if ok else f" (expected {expected})"
        print(f"  {status} [{intent}]{extra} ← {query[:60]}")
        if ok:
            passed += 1

    print(f"\n  Passed: {passed}/{len(CASES)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
