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

### Dictamen aplicado tras revisión de evidencias de ranking aportadas para `2.1`

Estado actual confirmado:
- `agents/rag_engine.py` ya incorpora `_detect_product()` y metadata boost de `+25%` por `product.id`.
- Existe evidencia de 8 queries dirigidas:
  - 4 para `ctm_estabilizador_renal`
  - 4 para `ctm_metabolica`
- La señal por `product.id` ya opera por:
  - alias
  - keywords
- Resultado observado:
  - top-1 correcto por producto: `8/8`
  - confusiones en top-3: `2/24 -> 1/24`
  - la confusión residual aparece solo en:
    - query `PCSK9`
    - score `0.072`
    - queda filtrada por `min_score = 0.1`
- Las queries ambiguas siguen sin boost por producto cuando `_detect_product()` retorna `None`, lo cual es correcto en esta fase.

### Nota de alcance

El cierre de `2.1` es estrictamente sobre discriminación por `product.id`.  
No certifica todavía precisión temática por subtema (`contraindicaciones`, `administración`, etc.); ese ajuste queda movido a `2.2`.

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 2.1 Discriminación por producto, no solo por `product_line` | **Cerrado** | Ya existe señal explícita por `product.id` y evidencia auditada de no confusión suficiente |
| 2.2 Thresholds, scores y cobertura RAG | **Activo** | Falta calibrar precisión temática, cortes de score y buckets `low/medium/high` |
| 2.5 `NO RESULTS` y anti-fabrication | **Parcial reforzado** | La confusión residual queda bajo threshold y no llega al LLM |
| 2.7 Suite mínima de regresión fija | **Pendiente preparado** | Las 8 queries de ranking ya pueden convertirse en regresión |
| 3.3 Limpieza de residuos activos del dominio anterior | **Pendiente crítico confirmado** | `MEDICAL_SYNONYMS` y residuos heredados siguen fuera del alcance de `2.1` |
| 4.1 Documentación / versionado | **Parcial reforzado** | `main.py`, `FastAPI.version` y `/api/health` ya están alineados a `4.4.0` |

---

## 2.1 Discriminación por producto, no solo por `product_line`
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- `rag_engine.py` ya incorpora `_detect_product()` con señal explícita por `product.id`
- el ranking ya usa:
  - alias del catálogo
  - keywords del catálogo
  para aplicar metadata boost por producto específico
- se auditó una batería de 8 queries dirigidas:
  - 4 para `ctm_estabilizador_renal`
  - 4 para `ctm_metabolica`
- resultado consolidado:
  - top-1 correcto por producto: `8/8`
  - confusiones en top-3: `2/24 -> 1/24`
  - el residuo restante queda por debajo de `min_score=0.1` y no llega al LLM

### Evidencia revisada

#### CTM Estabilizador Renal
- Q1 `¿Cuál es la composición del CTM Estabilizador Renal?`
  - top-3 final: `#3 renal`, `#4 renal`, `#2 renal`
  - señal: alias match
- Q2 `¿Cuáles son las contraindicaciones del CTM Estabilizador Renal?`
  - top-3 final: todos `renal`
  - señal: alias match
- Q3 `¿Cómo se administra el CTM Estabilizador Renal?`
  - top-3 final: todos `renal`
  - señal: alias match
- Q4 `¿Por qué las CTM se pre-tratan con melatonina?`
  - top-3 final: `#6 renal`, `#3 renal`, `#1 null`
  - señal: keyword match (`melatonina`)

#### CTM Metabólica
- Q5 `¿Qué es la CTM Metabólica?`
  - top-3 final: todos `metabólica`
  - señal: alias match
- Q6 `¿Cuáles son las contraindicaciones de la CTM Metabólica?`
  - top-3 final: todos `metabólica`
  - señal: alias match
- Q7 `¿Cómo se administra la CTM Metabólica?`
  - top-3 final: todos `metabólica`
  - señal: alias match
- Q8 `¿Qué es la PCSK9 y por qué es importante inhibirla?`
  - top-2 final: `metabólica`
  - residuo: `#5 renal` con score `0.072`
  - decisión: no bloquea porque queda filtrado por threshold

### Reservas no bloqueantes

- `_detect_product()` devuelve un solo `product.id`
- el matching sigue siendo endurecible
- `MEDICAL_SYNONYMS` mantiene residuos del dominio anterior

Estas reservas no reabren `2.1`.

### Decisión actual

**Se habilita avance a `2.2`.**

---

## 2.2 Thresholds, scores y cobertura RAG
**Estado:** Activo  
**Bloquea avance:** Sí

### Objetivo real del punto

Demostrar que el retrieval no solo trae el **producto correcto**, sino también el **subtema correcto**, y que los cortes de score / buckets de cobertura (`low`, `medium`, `high`) están calibrados para soportar respuestas seguras.

### Riesgo abierto

La evidencia de `2.1` confirma discriminación por producto, pero no garantiza todavía precisión temática por subtema.  
Eso impacta directamente:
- calidad de respuesta
- `rag_coverage`
- fallback
- `NO RESULTS`
- anti-fabrication

### Evidencia mínima requerida

1. **10–12 queries de calibración**
   - composición
   - indicaciones
   - contraindicaciones
   - administración / protocolo
   - tecnología / mecanismo
   - objeciones
   - comparativas
   - fuera de dominio

2. **Top-5 con scores por query**
   - `qa_id`
   - `categoria`
   - `product`
   - `score`

3. **Decisión de cobertura por query**
   - `high`
   - `medium`
   - `low`
   - `no_results`

4. **Relación con la salida final**
   - 1 caso `high` con respuesta normal
   - 1 caso `medium` con respuesta acotada
   - 1 caso `low` o `no_results` con respuesta segura / rechazo

5. **Decisión explícita de thresholds**
   - `min_score`
   - top-k útil
   - regla de cobertura
   - qué cambia en `rag_engine.py` vs `main.py` si hace falta ajustar

### Archivos a revisar

- `ABBE/agents/rag_engine.py`
- `ABBE/main.py`
- `ABBE/knowledge_base.json`
- opcional:
  - `ABBE/audit_traces.jsonl`

### Regla de diseño

No crear categorías nuevas para arreglar relevancia o cobertura.  
Si falla la precisión, se corrige en:
- scoring
- thresholds
- ranking
- cobertura
- catálogo / aliases / keywords solo si aportan señal real

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