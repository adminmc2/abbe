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
| 1. Datos, gobernanza y cumplimiento | **En progreso** | `1.1`, `1.2`, `1.3` y `1.4` cerrados; `1.5` activo |
| 2. Retrieval, routing y seguridad | **Pendiente crítico** | Persisten temas de discriminación por producto, thresholds y léxico heredado |
| 3. Frontend y desacople real | **Pendiente** | Falta auditar frontend/data-driven y limpiar residuos |
| 4. Documentación, configuración e higiene | **En progreso** | Validación y trazabilidad mejoraron; siguen abiertos docs, privacidad y despliegue |

---

## Impacto cruzado más reciente

### Dictamen aplicado tras revisión directa de `main.py` y evidencias reales de runtime para `1.3`

Estado actual confirmado:
- El sistema **no usa base de datos**.
- La persistencia sigue basada en archivos JSON locales.
- `user_data.json` sigue siendo historial de búsquedas del frontend.
- La app **sí persiste trazas reales** en:
  - `audit_traces.jsonl`
- Cada traza persistida incluye ahora:
  - `timestamp`
  - `session_id`
  - `query`
  - `intent`
  - `agent`
  - `rag_coverage`
  - `max_score`
  - `no_results`
  - `fallback_used`
  - `retrieved_results`
  - `response_text`

Cambios confirmados:
- `source_doc` ya se normaliza internamente a:
  - `normalized_sources: List[str]`
- `search()` sigue propagando el `qa_pair` completo
- `format_context()` incluye `Fuente: ...` en cada hecho verificado
- `main.py` escribe trazas append-only en `audit_traces.jsonl`
- la respuesta final del LLM ya se guarda en la traza persistida
- existe evidencia real de:
  - una consulta multi-fuente
  - un rechazo seguro con `no_results: true`

### Impacto en categorías

**Sin cambios.**  
La trazabilidad se resuelve en runtime y persistencia, no creando categorías nuevas.

### Nota operativa

El campo `fallback_used` ya existe en la traza.  
Su semántica actual queda aceptada para esta fase, pero si luego se quiere distinguir fallback real vs cobertura baja con precisión, ese endurecimiento pertenece a `2.5` / `2.2`, no bloquea `1.3`.

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 1.3 Trazabilidad de fuentes | **Cerrado** | Ya existe normalización de fuentes, persistencia estructurada, `response_text`, `no_results`, `fallback_used` y evidencia real de runtime |
| 1.5 Política de comparativas y competencia | **Parcial reforzado** | La trazabilidad persistente ya permite auditar comparativas y rechazos |
| 2.5 `NO RESULTS` y anti-fabrication | **Parcial reforzado** | Ya hay evidencia persistida de rechazo seguro y del contexto entregado al LLM |
| 2.7 Suite mínima de regresión fija | **Pendiente preparado** | Las trazas ya pueden alimentar casos reales de regresión |
| 4.1 Documentación / versionado | **Parcial** | `main.py` refleja `4.2.0`, pero falta auditoría completa del repositorio |
| 4.5 Higiene de datos | **Pendiente reforzado** | Ya existe persistencia de respuestas y contexto; falta política explícita de privacidad, retención y rotación |

---

## 1.3 Trazabilidad de fuentes
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- `source_doc` se mantiene compatible en `knowledge_base.json`
- el runtime normaliza a:
  - `normalized_sources: List[str]`
- la trazabilidad ya no depende solo de `stdout`
- existe persistencia append-only en:
  - `audit_traces.jsonl`
- se guarda la respuesta final del LLM en cada interacción
- se guardan los resultados recuperados con:
  - `qa_id`
  - `categoria`
  - `product`
  - `product_line`
  - `normalized_sources`
  - `score`
- la traza incluye:
  - `no_results`
  - `fallback_used`
- existe evidencia real de:
  - caso multi-fuente
  - rechazo seguro por falta de soporte documental

### Decisión de diseño fijada

- **No** se introduce base de datos en esta fase
- `audit_traces.jsonl` se considera suficiente para trazabilidad operativa actual
- Neon/Postgres queda como mejora futura no bloqueante

### Evidencia revisada

- `main.py`
- evidencia real de `audit_traces.jsonl` con:
  - consulta multi-fuente (`Q&A #40`)
  - rechazo seguro (`no_results: true`)

### Nota no bloqueante

Si más adelante se quiere una auditoría más estricta del fallback real, ese ajuste deberá salir del retrieval como señal explícita.  
No bloquea el cierre actual de `1.3`.

---

## 1.5 Política de comparativas y competencia
**Estado:** Parcial reforzado  
**Bloquea avance:** Sí, antes del cierre completo del bloque 1

### Estado actualizado

- `1.3` ya permite auditar mejor comparativas y respuestas multi-fuente
- ya existe base para demostrar qué fuentes fueron entregadas al LLM
- aún falta definir:
  - comparativas permitidas
  - comparativas prohibidas
  - respuesta segura si no existe soporte documental suficiente

### Evidencia futura requerida

- 1 comparativa permitida con soporte verificable
- 1 comparativa rechazada correctamente
- política escrita y visible de cuándo comparar y cuándo negarse

---

## 2.5 `NO RESULTS` y anti-fabrication end-to-end
**Estado:** Parcial reforzado  
**Bloquea avance:** Sí

### Estado actualizado

- ya se persisten:
  - `retrieved_results`
  - `response_text`
  - `no_results`
  - `fallback_used`
- ya existe evidencia real de rechazo seguro ante consulta fuera de dominio
- ya es posible auditar qué contexto recibió el LLM

### Sigue abierto

- la cobertura `low|medium|high` sigue dependiendo de la calibración de scores
- `fallback_used` existe, pero su semántica puede endurecerse más adelante
- esto conecta directamente con:
  - `2.2`
  - `2.1`

### Cierre esperado

- rechazo seguro consistente cuando no hay soporte suficiente
- pruebas persistidas de:
  - `no_results`
  - baja cobertura
  - fallback
  - respuesta segura

---

## 2.7 Suite mínima de regresión fija
**Estado:** Pendiente preparado  
**Bloquea avance:** Sí, antes del cierre final

### Estado actualizado

- `1.3` ya deja infraestructura suficiente para capturar errores reales
- las trazas de `audit_traces.jsonl` deben alimentar esta suite más adelante

### Regla fijada

Las trazas persistidas deberán convertirse después en:
- consultas fallidas
- rechazos seguros
- casos ambiguos
- ejemplos de cobertura baja

---

## 4.5 Higiene de datos: `user_data.json` y trazas de auditoría
**Estado:** Pendiente reforzado  
**Bloquea avance:** Sí, si participa en runtime o contiene residuos visibles

### Estado actualizado

- `user_data.json` sigue existiendo
- ahora también existe:
  - `audit_traces.jsonl`
- la app ya persiste respuestas y contexto recuperado
- esto refuerza la necesidad de una política explícita de:
  - privacidad
  - retención
  - rotación
  - exclusión del versionado

### Criterio de cierre

- política clara para `user_data.json`
- política clara para `audit_traces.jsonl`
- no almacenar identidad sensible en claro si no hace falta
- preferir:
  - `session_id`
  - `user_id_hash` si en el futuro aparece identidad persistente
- definir retención y limpieza del archivo

---

# Siguiente punto activo

## 1.4 — Cobertura por agente y por producto

**Estado:** Cerrado
**Cerrado tras aprobación del revisor.**

### Evidencia 1: Qué cambió

Auditoría completa de cobertura de `knowledge_base.json` por producto y por agente, con cruce directo de Q&A IDs.

### Evidencia 2: Dónde

Este documento. Sin cambios de código — `1.4` es auditoría de contenido.

### Evidencia 3: Cómo se validó

Cruce directo de cada Q&A ID contra `knowledge_base.json` (50 entries, campos `id`, `categoria`, `product`, `product_line`).

### Evidencia 4: Matriz de cobertura

#### Agente Productos (categorías: `productos`, `tecnologia`, `protocolos`, `seguridad`)

| Subtema | CTM Estabilizador Renal | CTM Metabólica |
|---|---|---|
| Definición del producto | #2 | #26 |
| Composición | #3, #4 | #27, #28 |
| Tecnología / Mecanismo | #5, #6, #14, #15 | #30, #31, #32, #33 |
| Indicaciones | #7 | #29 |
| Protocolos | #8 | #34 |
| Contraindicaciones | #9 | #35 |
| Efectos adversos | #10 | #36 |
| Interacciones | #11 | #37 |
| Embarazo/pediátrico | #13 | #38 |
| Almacenamiento | #12 | #39 |
| Empresa (cross-product) ¹ | #1 | #1 |
| Comparativa terapéutica ¹ | #19 (vs convencional) | #42 (vs estatinas/PCSK9i) |
| Comparativa cross-product ¹ | #40 (Renal vs Metabólica) | #40 (Renal vs Metabólica) |
| Comparativa competidor de marca ¹ | N/A | N/A |

> ¹ **Cobertura transversal**: estas filas no pertenecen estrictamente a las categorías del Agente Productos, pero se listan aquí porque el contenido de la KB es accesible por cualquier agente vía RAG. El mínimo exigido para Productos (composición, tecnología, indicaciones, protocolos, seguridad) ya está cubierto sin estas filas.

#### Agente Objeciones (categorías: `objeciones_precio`, `objeciones_eficacia`, `objeciones_seguridad`)

| Subtema | CTM Estabilizador Renal | CTM Metabólica |
|---|---|---|
| Precio | #16 | #41 |
| Eficacia | #17 | #43 |
| Seguridad | #18, #20 | #44, #45 |
| Comparativa terapéutica | #19 (vs tratamiento convencional) | #42 (vs estatinas/alternativas) |
| Comparativa competidor de marca | N/A — sin competidor directo en CTM pre-tratadas | N/A |

#### Agente Argumentos (categorías: `argumentos_venta`, `perfil_paciente`)

| Subtema | CTM Estabilizador Renal | CTM Metabólica |
|---|---|---|
| Especialidad | Nefrólogo (#21), Internista (#22), Médico general (#25) | Cardiólogo (#46), Endocrinólogo (#47), Internista (#48) |
| Pitch | #21, #22, #25 | #46, #47, #48 |
| Diferenciadores | #24 (vs otras terapias celulares) | #50 (vs otros tratamientos dislipidemia) |
| Perfil de paciente | #23 | #49 |

### Huecos detectados

| Hueco | Decisión |
|---|---|
| Comparativa con competidor de marca | **N/A** — no hay competidor directo identificado/cargado en el catálogo y la KB actuales |
| Más especialidades | No bloqueante — se amplía cargando nuevas Q&As por producto |

### Nota de alcance: cobertura y especialidades

- **Solo cuenta como cobertura lo respaldado por Q&As en `knowledge_base.json`.** Las especialidades o indicaciones mencionadas en los system prompts de los agentes **no constituyen cobertura** — son instrucciones de formato/estilo, no datos verificables.
- Las especialidades cubiertas son las que tienen Q&A dedicado: nefrólogo, internista, médico general (Renal); cardiólogo, endocrinólogo, internista (Metabólica).
- Cualquier residuo de especialidades antiguas (ej: dermatólogo, cirujano plástico de versiones anteriores) queda pendiente en **bloque 3.3** (limpieza de prompts), no es alcance de 1.4.
- "Comparativa con competidor de marca" es N/A porque no hay competidor directo identificado/cargado en el catálogo y la KB actuales.

### Nota sobre referencias

Los Q&A IDs listados son **referencias de cobertura**, no conteo único. Un mismo Q&A puede aparecer en más de un subtema cuando su contenido es relevante para ambos (ej: #19 aparece en Productos/Comparativa y en Objeciones/Comparativa). El total real de Q&As únicos en la KB es **50**.

### Regla

La cobertura debe validarse por **producto real**, no solo por conteo global de Q&As.

---

## Impacto cruzado tras cierre de 1.4

| Punto | Estado | Motivo |
|---|---|---|
| 1.4 Cobertura por agente y producto | **Cerrado** | Matriz completa con 4 evidencias, cobertura verificada por producto real |
| 1.5 Política de comparativas y competencia | **Parcial reforzado** | 1.4 ubicó las comparativas existentes (#19, #42, #40) y confirmó que competidor de marca es N/A |
| 2.1 Discriminación por producto | **Pendiente** | 1.4 no demuestra discriminación en ranking, solo cobertura de contenido |
| 2.7 Suite mínima de regresión | **Pendiente preparado** | La matriz de cobertura puede alimentar casos de prueba por producto/agente |
| 3.3 Limpieza de prompts | **Pendiente** | Residuos de especialidades antiguas en prompts quedan aquí, no en 1.4 |

**Sin impacto en categorías.**

---

# Siguiente punto activo

## 1.5 — Política de comparativas y competencia

**No avanzar a `2.x` hasta cerrar `1.5`.**

### Pendiente de requisitos del revisor

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
- Comparativa con competidor de marca es N/A (no cargado en catálogo/KB)
- Residuos de especialidades antiguas en prompts → bloque 3.3