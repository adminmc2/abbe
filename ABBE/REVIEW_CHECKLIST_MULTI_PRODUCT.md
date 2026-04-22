# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando productos nuevos
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- Decisión de retrieval: **por producto / línea / metadata**

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
| 1. Datos, gobernanza y cumplimiento | **En progreso** | `1.1`–`1.4` cerrados; `1.5` implementado, pendiente evidencia runtime y cierre formal |
| 2. Retrieval, routing y seguridad | **Pendiente crítico** | Persisten temas de discriminación por producto, thresholds y semántica comparativa |
| 3. Frontend y desacople real | **Pendiente** | Falta auditar frontend/data-driven y limpiar residuos activos del dominio anterior |
| 4. Documentación, configuración e higiene | **En progreso** | Validación, trazabilidad y política comparativa mejoraron; siguen abiertos versionado visible, privacidad y despliegue |

---

## Impacto cruzado más reciente

### Dictamen aplicado tras revisión directa de `agents/base_agent.py`, `agents/catalog.py`, `main.py`, `agents/agent_objeciones.py`, `agents/agent_argumentos.py` y `CLAUDE.md`

Estado actual confirmado:
- La política comparativa **sí existe en código** y no vive solo en prompts.
- `evaluate_comparative_query()` clasifica consultas en:
  - `internal`
  - `therapeutic`
  - `competitor`
- `main.py` evalúa la política **después del RAG**, inyecta instrucciones diferenciadas y persiste:
  - `comparative`
  en `audit_traces.jsonl`.
- `catalog.py` ya expone:
  - `has_competitors()`
  - `get_competitors()`
- `CLAUDE.md` ya documenta la política comparativa y el flujo actualizado.

### Observaciones de profundidad

1. **Comparativas internas**
   - hoy quedan permitidas cuando la query menciona `>= 2` productos internos del catálogo
   - la función no exige explícitamente que uno de los resultados recuperados sea un Q&A comparativo
   - para el portafolio actual esto es aceptable porque existe `#40`, pero el cierre de `1.5` debe demostrar en runtime que el soporte comparativo realmente se recupera

2. **Comparativas terapéuticas**
   - el soporte se decide hoy por:
     - categoría dentro de `COMPARATIVE_CATEGORIES`
     - `score >= 0.15`
   - esto es suficiente para esta fase
   - pero queda acoplado a la calibración de `2.2`

3. **Comparativas de competidor**
   - siguen bloqueadas correctamente mientras:
     - `competitors = []`
   - la futura habilitación es **parcialmente data-driven**
   - no está auditado todavía el contrato/recorrido completo de `competitors` cuando se activen

4. **Enforcement real**
   - el enforcement actual es:
     - evaluación runtime
     - guardarraíl por prompt
     - persistencia de traza
   - no es un hard-block programático
   - por eso la evidencia runtime sigue siendo obligatoria para cerrar `1.5`

5. **Impacto cruzado confirmado**
   - `agent_argumentos.py` conserva residuos claros del dominio anterior en:
     - especialidades
     - ejemplos
     - framing clínico-comercial
   - esto confirma `3.3` como pendiente crítico real, no hipotético

6. **Versionado**
   - `main.py` tiene cabecera/docstring `v4.3`
   - pero `FastAPI.version` y `/api/health` siguen en `4.2.0`
   - esto mantiene `4.1` en parcial con inconsistencia visible

### Impacto en categorías

**Sin cambios.**  
La política comparativa se resuelve en runtime, catálogo y prompts, no creando categorías nuevas en la KB.

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 1.5 Política de comparativas y competencia | **Implementado — pendiente evidencia runtime** | Hay motor runtime, trazabilidad y política explícita, pero falta prueba real permitida + rechazada |
| 2.5 `NO RESULTS` y anti-fabrication | **Parcial reforzado** | La traza ya persiste `comparative`, pero la solidez sigue dependiendo de la calibración del retrieval |
| 2.7 Suite mínima de regresión fija | **Pendiente preparado** | Las comparativas auditadas podrán alimentar regresión real |
| 3.3 Limpieza de residuos activos del dominio anterior | **Pendiente crítico confirmado** | La inspección directa de `agent_argumentos.py` confirma residuos de prompts/especialidades heredadas |
| 4.1 Documentación / versionado | **Parcial con inconsistencia** | `CLAUDE.md` ya se actualizó, pero `main.py` y `/api/health` no reflejan `4.3.0` de forma consistente |
| 4.5 Higiene de datos | **Pendiente reforzado** | `audit_traces.jsonl` ahora también persiste `comparative`; falta política de retención/privacidad |

---

## 1.5 Política de comparativas y competencia
**Estado:** Implementado — pendiente evidencia runtime  
**Bloquea avance:** Sí, antes del cierre completo del bloque 1

### Implementación verificada

- `evaluate_comparative_query()` en `agents/base_agent.py`
  - detecta intención comparativa por señales regex
  - clasifica en:
    - `internal`
    - `therapeutic`
    - `competitor`
  - detecta lenguaje de superioridad
- `main.py`
  - evalúa la política comparativa tras el retrieval
  - inyecta instrucciones diferenciadas según:
    - tipo
    - permitido / rechazado
  - persiste `comparative` en `audit_traces.jsonl`
- `agents/catalog.py`
  - ya expone:
    - `has_competitors()`
    - `get_competitors()`
- `CLAUDE.md`
  - ya documenta la política comparativa y su lugar en el flujo

### Política fijada

#### Comparativas permitidas
- **Internas** entre productos del portafolio actual
- **Terapéuticas** contra tratamiento convencional / alternativas, solo si hay soporte suficiente en resultados RAG
- **Diferenciadores** amplios, sin convertirlos en claims absolutos no documentados

#### Comparativas prohibidas
- **Competidor de marca** mientras `catalog.json` siga sin competidores cargados
- claims de superioridad como:
  - `mejor`
  - `superior`
  - `más eficaz`
  - `más seguro`
  - `más conveniente`
  si no están explícitamente soportados
- comparativas fuera de indicación
- comparativas con productos no cargados en catálogo/KB
- comparativas inventadas por el LLM

### Observaciones de implementación

1. **Interna ≠ automáticamente soportada**
   - hoy una comparativa interna se habilita cuando la query menciona dos productos internos
   - esto se acepta en la fase actual porque existe soporte real en KB (`#40`)
   - pero el cierre debe probar que ese soporte se recupera efectivamente en runtime

2. **Soporte terapéutico todavía heurístico**
   - hoy se decide por:
     - categoría amplia
     - umbral de score
   - esto no bloquea `1.5`
   - pero conecta directamente con:
     - `2.2`
     - `2.5`

3. **El rechazo no es hard-block**
   - el enforcement actual combina:
     - evaluación runtime
     - prompt guardrails
     - trazabilidad persistida
   - esto se considera suficiente para esta fase
   - pero obliga a exigir evidencia real antes de cerrar

4. **Futuro `competitors`**
   - el switch de catálogo ya existe
   - pero cuando se carguen competidores habrá que auditar:
     - contrato
     - validación
     - recorrido end-to-end
   - no bloquea el estado actual porque hoy `competitors` sigue vacío

### Evidencia pendiente para cierre

Para cerrar `1.5` se exige evidencia real de runtime de ambos casos:

#### A. Comparativa permitida
Mostrar:
- consulta real
- agente elegido
- `qa_id` recuperados
- respuesta final
- traza en `audit_traces.jsonl`

Ejemplos válidos:
- `¿Cuál es la diferencia entre el CTM Estabilizador Renal y la CTM Metabólica?`
- `¿Por qué usar CTM Metabólica si ya existen estatinas?`

#### B. Comparativa rechazada
Mostrar:
- consulta real
- respuesta segura
- ausencia de claims de superioridad no soportados
- traza en `audit_traces.jsonl`

Ejemplos válidos:
- `Ya uso otra marca, ¿por qué debería cambiar?`
- `¿Es mejor la CTM Metabólica que otra terapia celular de otra marca?`

### Criterio de cierre

`1.5` solo se cerrará cuando se demuestre que:

1. existe una comparativa permitida auditada en runtime
2. existe una comparativa rechazada auditada en runtime
3. ambas dejan traza persistida en `audit_traces.jsonl`
4. la respuesta permitida usa solo soporte documental recuperado
5. la respuesta rechazada no inventa competencia ni claims de superioridad

### Decisión actual

**No avanzar a `2.x` todavía.**

---

## 4.1 Actualizar `CLAUDE.md`, `README.md`, headers y versiones internas
**Estado:** Parcial con inconsistencia  
**Bloquea avance:** Sí, antes del cierre final

### Estado actualizado

- `CLAUDE.md` ya documenta la política comparativa y el flujo actualizado
- `main.py` muestra cabecera/docstring `v4.3`
- pero:
  - `app = FastAPI(... version="4.2.0")`
  - `/api/health` devuelve `4.2.0`

### Criterio de cierre

- alinear versión visible en:
  - cabecera
  - `FastAPI.version`
  - `/api/health`
  - `CHANGELOG.md`
  - documentación operativa relevante

---

## 4.5 Higiene de datos: `user_data.json` y trazas de auditoría
**Estado:** Pendiente reforzado  
**Bloquea avance:** Sí, si participa en runtime o contiene residuos visibles

### Estado actualizado

- `user_data.json` sigue existiendo
- `audit_traces.jsonl` ya persiste:
  - `retrieved_results`
  - `response_text`
  - `no_results`
  - `fallback_used`
  - `comparative` cuando aplica

### Criterio de cierre

- política clara para `user_data.json`
- política clara para `audit_traces.jsonl`
- no almacenar identidad sensible en claro si no hace falta
- definir:
  - retención
  - rotación
  - limpieza
  - exclusión del versionado

---

# Historial breve de decisiones ya fijadas

- Se mantiene arquitectura por intención, no por producto
- Se mantiene BM25 y se descarta ChromaDB
- Se carga producto por producto
- `agent_tags` no se incorpora por ahora
- `source_section` no es obligatorio en esta fase
- El contrato de datos de la KB se valida en startup
- El contrato de datos del catálogo se valida en startup
- `product = null` es válido para contenido de empresa, nivel línea y comparativas cross-product
- El canónico interno de producto es `product.id`
- El nombre visible de producto es `product.name`
- La trazabilidad persistente se implementa sin base de datos, usando `audit_traces.jsonl`
- Neon/Postgres queda como mejora futura no bloqueante
- `1.3` queda cerrado con persistencia de:
  - `retrieved_results`
  - `response_text`
  - `no_results`
  - `fallback_used`
- "Aprender de errores" significa revisar trazas y convertirlas en mejoras de KB, reglas y regresión; no entrenamiento automático
- La cobertura se valida por producto real, no por conteo global de Q&As
- Solo cuenta como cobertura lo respaldado por KB, no lo mencionado en prompts
- Comparativa con competidor de marca es N/A mientras no exista competidor cargado en catálogo/KB
- Residuos de especialidades antiguas en prompts → bloque 3.3
- La política comparativa tiene enforcement en runtime, no solo en prompts
- Comparativas de competidor de marca: solo permitidas si `has_competitors()` es `True`
- Comparativas terapéuticas: solo permitidas si hay soporte comparativo suficiente en resultados RAG
- Comparativas internas: permitidas en el portafolio actual, pero la salida debe apoyarse solo en datos recuperados y su cierre requiere evidencia runtime
- Claims de superioridad: solo permitidos si están explícitamente en la KB
- La futura activación de `competitors` requerirá auditoría específica de contrato y recorrido end-to-end; no bloquea mientras siga vacío