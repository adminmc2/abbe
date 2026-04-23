# ABBE Regression Suite

Suite de diagnóstico y regresión para bloques 2.2–2.6.

## Estructura

```
regression/
├── run_all.py              # Runner unificado
├── README.md               # Este archivo
├── smoke_26_manual.md      # Smoke test manual para 2.6 (navegador)
├── regression_report.md    # Artefacto de salida (generado por run_all.py)
│
├── diag_retrieval.py       # 2.2 — RAG BM25 + fallback (offline)
├── diag_routing.py         # 2.3 — Intent classification (offline)
├── diag_adversarial.py     # 2.3 — Adversarial validation (runtime)
├── diag_multiturn.py       # 2.3 — Multi-turn coherencia (runtime)
├── diag_runtime_24.py      # 2.4 — Coherencia agente↔retrieval (runtime)
├── diag_25_noresults.py    # 2.5 — NO RESULTS + comparativas (offline)
├── diag_25_runtime.py      # 2.5 — effective_mode en respuestas (runtime)
├── diag_26_historial.py    # 2.6 — Endpoints historial + aislamiento (runtime)
└── diag_26_final.py        # 2.6 — Flujo completo A→B→A + trazas (runtime)
```

## Casos y expectativas

Los casos de prueba están **fijos y versionados dentro de cada script**. Cada `diag_*.py` contiene:
- Queries/inputs como constantes (no generados dinámicamente)
- Expectativas explícitas (cobertura esperada, intent esperado, etc.)
- Lógica de verificación con contadores pass/fail

No se usa un archivo externo de fixtures; los casos son self-contained para facilitar la ejecución individual de cada script.

## Ejecucion

```bash
cd ABBE

# Solo tests offline (no requiere servidor)
python3 regression/run_all.py

# Offline + runtime (requiere servidor en :7862)
python3 regression/run_all.py --runtime

# Solo un bloque
python3 regression/run_all.py --block 2.5
python3 regression/run_all.py --block 2.6 --runtime
```

## Exit code

- `0` — todos los scripts pasaron
- `1` — al menos un script falló o hizo timeout

## Requisitos para runtime
- Servidor ABBE corriendo: `uvicorn main:app --port 7862`
- Dependencias: `pip install requests websockets`

## Artefacto de salida
`run_all.py` genera `regression_report.md` con el resultado detallado de cada script.
