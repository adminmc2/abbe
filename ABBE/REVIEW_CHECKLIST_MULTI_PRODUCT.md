# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando productos nuevos
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- El siguiente punto activo es `2.4`: **coherencia agente↔retrieval, categorías nativas y fallback auditable**

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
| 2. Retrieval, routing y seguridad | **En progreso** | `2.1`–`2.3` cerrados; `2.4` siguiente subpunto pendiente de formalización en este checklist |
| 3. Frontend y desacople real | **Pendiente** | Falta auditar frontend/data-driven y limpiar residuos activos del dominio anterior |
| 4. Documentación, configuración e higiene | **En progreso** | Validación, trazabilidad y routing mejoraron; siguen abiertos versionado visible, privacidad y despliegue |

---

## Impacto cruzado más reciente

### Dictamen aplicado según evidencias runtime aportadas para `2.3`

Estado actual confirmado:
- El runtime real usa `classify_intent_rules()` en `main.py`; no depende del path LLM para el routing operativo.
- `agents/orchestrator.py` fue endurecido con criterio **frame > vocabulario**.
- Se ampliaron variantes comerciales de objeción sin secuestrar consultas técnicas neutras.
- No se añadió sticky routing.
- No fue necesario mover lógica de routing a `main.py`.
- Evidencia aportada:
  - single-turn: `13/13 OK`
  - multi-turn: `6/6 OK`
  - adversariales: `4/4 OK`
  - total: `23/23`, `0 misroutes`
- La batería adversarial confirma que expresiones como:
  - `El médico pregunta ...`
  combinadas con consulta técnica siguen ruteando a `productos`.
- Se reporta versión `4.6.0` y `CHANGELOG.md` actualizado.

### Nota de alcance

El cierre de `2.3` valida **routing por intención en runtime**.  
No sustituye la necesidad de convertir esta batería en regresión fija dentro de `2.7`.

### Observación no bloqueante

- `evaluate_comparative_query()` en `base_agent.py` sigue usando `score >= 0.15` para soporte comparativo, heredado de la escala anterior normalizada.
- No bloquea `2.3`, pero sigue pendiente de recalibración en `2.5` / hardening comparativo.

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 2.2 Thresholds, scores y cobertura RAG | **Cerrado** | Ya existe calibración con raw scores, bucket `medium` real, `no_results` separado y evidencia runtime auditada |
| 2.3 Routing por intención y selección correcta de agente | **Cerrado** | Hay evidencia runtime suficiente en single-turn, multi-turn y adversariales, sin misroutes |
| 2.4 Coherencia agente↔retrieval: categorías nativas y fallback auditable | **Activo** | Las categorías entre agentes se solapan mucho y la traza actual no representa fielmente si el fallback se activó realmente |
| 2.5 `NO RESULTS` y anti-fabrication | **Parcial reforzado** | `no_results` ya es bucket explícito y auditado con score real; falta hardening final |
| 2.7 Suite mínima de regresión fija | **Pendiente preparado** | Las baterías de `2.2` y `2.3` ya pueden convertirse en regresión estable |

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

**Punto cerrado.**

---

## 2.3 Routing por intención y selección correcta de agente
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- El routing operativo se validó en la ruta real de runtime.
- La decisión sigue viviendo en `orchestrator.py`.
- El ajuste aplicado prioriza **frame comercial** sobre vocabulario técnico aislado.
- No se introdujo sticky routing.
- No se observa sobrerouting nuevo de consultas técnicas hacia `objeciones`.

### Evidencia revisada

- **Single-turn**
  - `13/13 OK`

- **Multi-turn**
  - `6/6 OK`

- **Adversariales**
  - `4/4 OK`

- **Total**
  - `23/23`
  - `0 misroutes`

### Confirmaciones relevantes

- `main.py` usa `classify_intent_rules()` en el routing operativo.
- `El médico pregunta ...` + consulta técnica:
  - rutea a `productos`
  - no dispara objeción por sobreajuste
- la mejora corrige los fallos detectados en Fase A sin abrir el riesgo mayor de secuestrar vocabulario técnico

### Decisión actual

**Se habilita fijar y abrir `2.4` en este checklist.**

---

## 2.4 Coherencia agente↔retrieval: categorías nativas y fallback auditable
**Estado:** Activo  
**Bloquea avance:** Sí

### Objetivo real del punto

Demostrar que el agente correcto no solo se selecciona bien, sino que además recupera contexto **principalmente nativo de su intención**; y que el fallback queda trazado de forma **real y auditable**, no inferida indirectamente.

### Riesgo abierto

- `agent_productos.py`, `agent_objeciones.py` y `agent_argumentos.py` comparten categorías amplias (`productos`, `tecnologia`, `seguridad`, `empresa`), por lo que un agente puede responder “bien” apoyándose en contexto genérico.
- `search_knowledge_with_fallback()` vive en `base_agent.py`, pero `main.py` no persiste si el fallback se activó realmente.
- La traza actual puede subreportar fallback, debilitando auditoría y futuras regresiones.

### Evidencia mínima requerida

1. **12 queries claras**
   - 4 de `productos`
   - 4 de `objeciones`
   - 4 de `argumentos`

2. **Para cada query**
   - agente esperado
   - agente real
   - categorías nativas esperadas
   - top-5 **filtrado** por categorías del agente:
     - `qa_id`
     - `categoria`
     - `product`
     - `score`
   - indicar si el fallback se activó realmente
   - top-5 **final** tras fallback/combinación
   - conteo de categorías nativas en top-3

3. **3 casos runtime vía `/ws/chat`**
   - 1 por cada agente
   - con traza persistida
   - mostrando si hubo o no fallback real

4. **Al menos 2 casos específicos**
   - 1 donde el retrieval nativo sea suficiente **sin fallback**
   - 1 donde el fallback mejore realmente el resultado

### Archivos a revisar

- `ABBE/agents/base_agent.py`
- `ABBE/main.py`
- `ABBE/agents/rag_engine.py`
- `ABBE/agents/agent_productos.py`
- `ABBE/agents/agent_objeciones.py`
- `ABBE/agents/agent_argumentos.py`
- `ABBE/audit_traces.jsonl`

### Regla de diseño

- **No** crear agentes nuevos
- **No** crear categorías nuevas en la KB
- **No** resolverlo ampliando aún más el solapamiento de categorías
- Si hace falta ajuste, hacerlo en:
  - priorización de categorías nativas
  - metadata / scoring
  - contrato de retorno del fallback
  - trazabilidad real en runtime

### Criterio de cierre

`2.4` solo se cierra si queda demostrado que:

1. las queries claras de cada agente priorizan contexto nativo suficiente
2. el fallback queda marcado de forma **real**, no inferida por cobertura
3. la traza distingue cuándo el resultado vino de búsqueda filtrada vs fallback
4. el sistema no depende sistemáticamente de contexto genérico para sostener `objeciones` y `argumentos`

---

# Siguiente punto activo

## 2.4 — Coherencia agente↔retrieval: categorías nativas y fallback auditable

**No avanzar a `2.5` hasta cerrar `2.4`.**

---

# Historial breve de decisiones ya fijadas

- `2.1` queda cerrado con señal explícita por `product.id`
- El boost por `product_line` no basta cuando productos hermanos comparten línea
- `_detect_product()` + metadata boost por producto quedan aceptados como solución actual
- La confusión residual en `PCSK9` no bloquea `2.1` porque queda bajo threshold y no llega al LLM
- La precisión temática por subtema no queda cerrada en `2.1`; pasa a `2.2`
- `2.2` queda cerrado con raw scores, bucket `medium` real y `no_results` explícito
- El fallback vuelve a ser funcional tras recalibrar thresholds a escala raw
- `2.3` queda cerrado con routing por intención basado en **frame > vocabulario**
- El routing operativo usa `classify_intent_rules()`; no depende del path LLM
- No se acepta sticky routing como solución
- `El médico pregunta ...` + consulta técnica debe seguir ruteando a `productos`
- Las baterías de `2.2` y `2.3` deberán convertirse en regresión fija en `2.7`
- `3.3` sigue abierto por residuos activos del dominio anterior
- `4.1` sigue parcial hasta verificar consistencia total de versión visible en toda la app