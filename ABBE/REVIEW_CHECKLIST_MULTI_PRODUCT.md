# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando **5 productos nuevos**
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- Decisión de retrieval: **por producto/línea/metadata**

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
- `catalog.json` + `knowledge_base.json`
- **BM25** como base de retrieval
- **Sin ChromaDB**
- **Sin embeddings** por ahora
- Onboarding **producto por producto**

---

## Estado global actual

### Aprobado conceptualmente

- Desacople principal del backend respecto a Novacutan
- Catálogo separado de la KB
- BM25 como dirección correcta
- Validación multi-producto inicial con 2 productos

### Aún abierto

- Gobierno de datos y trazabilidad
- Retrieval robusto por producto
- Anti-fabrication end-to-end
- Frontend realmente data-driven
- Documentación operativa alineada
- Higiene de despliegue y datos

---

## Impacto cruzado más reciente

### Dictamen aplicado tras revisión de `knowledge_base.json` + `agents/rag_engine.py`

Cambios validados:
- `Q&A #1` corregido con trazabilidad multi-fuente coherente
- `VALID_CATEGORIES` añadida al validador
- `_validate_kb()` ahora soporta `KB_VALIDATION_MODE=warn|strict`

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 1.1 Contrato de datos por Q&A | **Cerrado** | Se corrigió `Q&A #1`, existe allowlist explícita para `categoria` y el validador ya soporta enforcement configurable |
| 1.3 Trazabilidad de fuentes | **Parcial** | La trazabilidad ya es coherente en los casos revisados; queda pendiente solo la mejora futura de modelar múltiples fuentes como lista |
| 4.3 Validación automática al arrancar | **Parcial** | Ya existe modo `strict`, pero falta definir política por entorno y revisar cobertura equivalente para el catálogo |
| 2.1 Discriminación por producto | **Pendiente** | Sin cambios en ranking por `product` |
| 2.2 BM25 / thresholds / fallback | **Parcial crítico** | Sin cambios |
| 2.6 Léxico heredado | **Pendiente crítico** | Sin cambios |
| 3.3 Residuos activos del dominio anterior | **Pendiente** | Sin cambios |
| 4.1 Documentación / versiones | **Pendiente** | Sin cambios |

### Regla nueva de mantenimiento

Si se añade una categoría nueva en `knowledge_base.json`, deben actualizarse:
1. `VALID_CATEGORIES` en `agents/rag_engine.py`
2. el mapping agente → categorías en los agentes correspondientes

Esto no bloquea el estado actual, pero evita drift futuro.

---

## 1.1 Contrato de datos por Q&A
**Estado:** Cerrado  
**Bloquea avance:** No

### Criterio de cierre cumplido

- Los Q&As revisados cumplen el contrato mínimo
- `Q&A #1` ya tiene trazabilidad coherente
- `categoria` ya se valida contra allowlist explícita
- el validador ya puede operar en modo `strict`

### Nota operativa

El modo actual es configurable:
- `warn`: reporta sin detener arranque
- `strict`: falla rápido ante datos inválidos

Esto se considera suficiente para cerrar 1.1 en esta fase.

---

## 1.3 Trazabilidad de fuentes
**Estado:** Parcial  
**Bloquea avance:** No, por ahora

### Estado actualizado

- `source_doc` es obligatorio y coherente en los casos revisados
- `Q&A #1` ya no tiene inconsistencia de fuente
- La mejora pendiente es solo de modelado:
  - pasar de string concatenado a una lista tipo `source_docs` si más adelante hace falta

---

## 4.3 Validación automática del schema al arrancar
**Estado:** Parcial  
**Bloquea avance:** No para 1.2

### Estado actualizado

- `_validate_kb()` ya soporta:
  - campos obligatorios
  - no vacíos
  - IDs únicos
  - referencias cruzadas
  - allowlist de categorías
  - modo `warn|strict`

### Pendiente

- definir política por entorno:
  - local / predeploy: `strict`
  - producción: `warn` o `strict`, según operativa
- extender la misma disciplina de validación al catálogo si aún no existe

---

# Siguiente punto activo

## 1.2 — Contrato de datos por producto en `catalog.json`

**Evidencia requerida para revisar 1.2:**
- `catalog.json` completo
- `agents/catalog.py`
- ejemplos reales de:
  - `get_product_synonyms()`
  - `get_product_aliases()`
  - `get_product_keywords()`
  - `get_condition_product_map()`

**Criterio de cierre esperado:**
- cada producto tiene estructura suficiente para operar sin hardcodes
- aliases/keywords/synonyms salen del catálogo
- empresa / fabricante / línea / producto quedan semánticamente claros
- no se crean categorías nuevas para resolver problemas que pertenecen al catálogo