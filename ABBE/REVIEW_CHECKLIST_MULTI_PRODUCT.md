# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando productos nuevos
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- El siguiente riesgo crítico abierto es `2.2`: calibración de thresholds, scores y cobertura RAG

---

## Reglas inviolables

1. **No** pasar al siguiente punto hasta cerrar el actual.
2. Todo cierre requiere 4 evidencias:
   - qué cambió
   - dónde cambió
   - cómo se validó
   - evidencia concreta
3. Tras cada cierre se revisa el **impacto cruzado** sobre los demás bloques.
4. Si un cambio reabre otro punto, su estado vuelve a `Parcial` o `Pendiente`.
5. Este documento es la **fuente temporal de verdad** durante la revisión.
6. Al finalizar toda la revisión, este archivo se elimina.

---

## Arquitectura ya aprobada (no rediseñar)

- Monolito modular con **FastAPI + WebSocket**
- **3 agentes por intención**
- `catalog.json` separado de `knowledge_base.json`
- **BM25** como base de retrieval
- **Sin ChromaDB**
- **Sin embeddings** por ahora
- Onboarding **producto por producto**
- Si falta semántica de producto, se corrige en:
  - `catalog.json`
  - `agents/catalog.py`
  - `agents/rag_engine.py`
- **No** se crean categorías nuevas en la KB para resolver problemas que pertenecen al catálogo

---

## Estado global actual

| Bloque | Estado | Nota |
|---|---|---|
| 1. Datos, gobernanza y cumplimiento | **Cerrado** | `1.1`–`1.5` cerrados; bloque 1 finalizado |
| 2. Retrieval, routing y seguridad | **En progreso** | `2.1` activo; persisten discriminación por producto, thresholds y léxico heredado |
| 3. Frontend y desacople real | **Pendiente** | Falta auditar frontend/data-driven y limpiar residuos activos del dominio anterior |
| 4. Documentación, configuración e higiene | **En progreso** | Validación, trazabilidad y política comparativa mejoraron; siguen abiertos versionado visible, privacidad y despliegue |

---

## Impacto cruzado más reciente

### Dictamen aplicado tras revisión directa de `agents/rag_engine.py`, `agents/base_agent.py`, `main.py`, `CHANGELOG.md` y evidencias diagnósticas/runtime aportadas para `2.2`

Estado actual confirmado:
- `agents/rag_engine.py` ya no normaliza scores a `[0,1]`; `search()` devuelve **raw BM25 scores** con boosts.
- `agents/base_agent.py` recalibró:
  - `search_knowledge_with_fallback(... score_threshold=8.0)`
  - `format_context(... min_score=3.0)`
  - la normalización queda solo para display local de confianza.
- `main.py` ya calcula cobertura con 4 buckets reales:
  - `high`
  - `medium`
  - `low`
  - `no_results`
- La evidencia diagnóstica aportada reporta:
  - antes: `10 high / 0 medium / 2 low`
  - después: `8 high / 2 medium / 0 low / 2 no_results`
- Existe evidencia runtime de:
  - `high`: composición CTM Estabilizador Renal (`max_score: 43.312`)
  - `medium`: `¿Cómo funcionan las CTM?` (`max_score: 6.502`)
  - `no_results`: `Lifting temporal con hilo tensor` (`max_score: 0.0`)
- La traza persistida ya registra el score raw usado para cobertura.
- El fallback vuelve a ser funcional tras recalibrar el umbral a escala raw.

### Nota de alcance

El cierre de `2.2` valida:
- calibración de scores
- buckets de cobertura
- separación real entre `high`, `medium`, `low` y `no_results`

No cierra todavía:
- endurecimiento de soporte comparativo
- hardening final anti-fabrication
- limpieza de residuos del dominio anterior

### Observación no bloqueante

- `evaluate_comparative_query()` en `base_agent.py` sigue usando `score >= 0.15` para soporte comparativo, heredado de la escala anterior normalizada.
- No bloquea el cierre de `2.2`, pero debe recalibrarse en `2.5` / hardening comparativo para mantener coherencia de thresholds.

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 2.2 Thresholds, scores y cobertura RAG | **Cerrado** | Ya existe calibración con raw scores, bucket `medium` real, `no_results` separado y evidencia runtime auditada |
| 2.5 `NO RESULTS` y anti-fabrication | **Parcial reforzado** | `no_results` ya es bucket explícito y auditado con score real |
| 2.7 Suite mínima de regresión fija | **Pendiente preparado** | La batería de 12 queries y los 3 casos runtime ya pueden convertirse en regresión |
| 4.1 Documentación / versionado | **Parcial reforzado** | `main.py`, `FastAPI.version`, `/api/health` y `CHANGELOG.md` ya están alineados a `4.5.0` |
| 3.3 Limpieza de residuos activos del dominio anterior | **Pendiente crítico confirmado** | Persisten residuos fuera del alcance de `2.2` |

---

## 2.2 Thresholds, scores y cobertura RAG
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Se eliminó la normalización artificial `[0,1]` en `search()`.
- El ranking sigue siendo válido, pero ahora la cobertura usa scores raw reales.
- `main.py` distingue correctamente:
  - `high`
  - `medium`
  - `low`
  - `no_results`
- `medium` deja de ser un bucket muerto.
- `no_results` queda separado de `low`.
- `base_agent.py` recalibra:
  - threshold de fallback
  - `min_score` de contexto
- Se validó con:
  - 12 queries diagnósticas
  - 3 casos runtime auditables

### Evidencia revisada

#### Distribución diagnóstica
- Antes:
  - `high: 10`
  - `medium: 0`
  - `low: 2`
- Después:
  - `high: 8`
  - `medium: 2`
  - `low: 0`
  - `no_results: 2`

#### Casos runtime
- **HIGH**
  - Query: `Composición CTM Estabilizador Renal`
  - Coverage: `high`
  - `max_score`: `43.312`

- **MEDIUM**
  - Query: `¿Cómo funcionan las CTM?`
  - Coverage: `medium`
  - `max_score`: `6.502`

- **NO_RESULTS**
  - Query: `Lifting temporal con hilo tensor`
  - Coverage: `no_results`
  - `max_score`: `0.0`

### Nota no bloqueante

Que la batería final no haya producido un caso `low` no reabre `2.2`.  
El bucket existe y quedó correctamente separado de `no_results`; la evidencia mínima runtime ya quedó cubierta con:
- `high`
- `medium`
- `no_results`

### Decisión actual

**Se habilita avance al siguiente subpunto del bloque 2.**

---

# Siguiente punto activo

## 2.2 — Thresholds, scores y cobertura RAG

**No avanzar a `2.3` hasta cerrar `2.2`.**

### Evidencia mínima a pedir ahora

1. 10–12 queries de calibración con top-5
2. `qa_id`, `categoria`, `product`, `score`
3. bucket de cobertura por query
4. 3 ejemplos auditables:
   - `high`
   - `medium`
   - `low/no_results`
5. decisión explícita de thresholds y qué capa debe ajustarse

---

# Historial breve de decisiones ya fijadas

- `2.1` queda cerrado con señal explícita por `product.id`
- El boost por `product_line` no basta cuando productos hermanos comparten línea
- `_detect_product()` + metadata boost por producto quedan aceptados como solución actual
- La confusión residual en `PCSK9` no bloquea `2.1` porque queda bajo threshold y no llega al LLM
- La precisión temática por subtema no queda cerrada en `2.1`; pasa a `2.2`