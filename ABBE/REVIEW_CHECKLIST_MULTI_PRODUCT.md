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
| 1. Datos, gobernanza y cumplimiento | **En progreso** | `1.1` y `1.2` cerrados; `1.3` activo |
| 2. Retrieval, routing y seguridad | **Pendiente crítico** | Persisten temas de producto, thresholds y léxico heredado |
| 3. Frontend y desacople real | **Pendiente** | Falta auditar frontend/data-driven y limpiar residuos |
| 4. Documentación, configuración e higiene | **En progreso** | Validación mejoró; documentación y despliegue siguen abiertos |

---

## Impacto cruzado más reciente

### Dictamen aplicado tras cierre de `1.2`

Cambios absorbidos:
- Ya existe contrato de datos del catálogo
- Ya existe validación del catálogo con política `warn/strict`
- Ya existe canónico interno por `product.id`
- Ya existen helpers explícitos para:
  - `product.id -> producto`
  - `product.id -> name`
  - `alias -> product.id`
  - `product.id -> keywords`
- `get_condition_product_map()` ya devuelve `product.id`
- `agent_productos.py` ya resuelve `id -> name` para uso de prompt

### Impacto en categorías

**Sin cambios.**  
La taxonomía de la KB se mantiene igual.

Regla de mantenimiento vigente:
- si se añade una categoría nueva en la KB, deben actualizarse:
  1. la allowlist de categorías del validador
  2. el mapping agente → categorías

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 1.1 Contrato de datos por Q&A | **Cerrado** | Contrato mínimo, allowlist de categorías y validación configurable ya existen |
| 1.2 Contrato de datos por producto | **Cerrado** | Validador de catálogo + canónico por `product.id` + helpers explícitos |
| 1.3 Trazabilidad de fuentes | **Parcial** | Hay `source_doc`, pero falta cerrar trazabilidad end-to-end y convención multi-fuente |
| 1.4 Cobertura por agente y por producto | **Pendiente** | Aún no hay matriz de cobertura formal |
| 2.1 Discriminación por producto | **Parcial** | La infraestructura por `product.id` ya existe, pero falta aplicarla en ranking/RAG |
| 4.3 Validación automática al arrancar | **Parcial sólido** | KB y catálogo ya validan con `warn/strict`; falta política final por entorno |
| 4.1 Documentación / versionado | **Parcial** | Hay progreso reportado, pero falta auditoría completa de docs y versiones |

---

# BLOQUE 1 — Datos, gobernanza y cumplimiento

## 1.1 Contrato de datos por Q&A
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Contrato mínimo visible aplicado en la KB
- `source_doc` obligatorio
- `product = null` permitido para:
  - contenido de empresa
  - contenido de línea
  - comparativas cross-product
- `categoria` validada contra allowlist explícita
- Validación configurable `warn|strict`

### Regla fijada

Si se añade una categoría nueva:
1. actualizar allowlist del validador
2. actualizar mapping agente → categorías

---

## 1.2 Contrato de datos por producto en `catalog.json`
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Validador del catálogo con:
  - campos obligatorios por línea y por producto
  - IDs únicos
  - tipos correctos
  - detección de aliases duplicados
  - política `warn|strict`
- `get_catalog()` ya no depende de fallback silencioso puro
- Canónico interno fijado en `product.id`
- Nombre visible separado en `product.name`
- Helpers canónicos disponibles para futura evolución del retrieval

### Decisión de diseño fijada

- **Interno:** `product.id`
- **Visible:** `product.name`

### Impacto confirmado

Esto prepara, pero **no cierra**, el punto `2.1` de discriminación por producto.

---

## 1.3 Trazabilidad de fuentes
**Estado:** Parcial  
**Bloquea avance:** Sí

### Objetivo real del punto

No basta con que la KB tenga `source_doc`.  
Hay que asegurar trazabilidad **end-to-end** para respuestas recuperadas o sintetizadas.

### Lo ya resuelto

- `source_doc` es obligatorio en la KB
- Los casos revisados ya tienen fuente coherente
- La trazabilidad mínima documental existe

### Lo que falta para cerrarlo

1. **Definir convención multi-fuente**
   - decidir si se mantiene:
     - `source_doc` como string documentado
   - o si se migra a:
     - `source_docs` como lista
2. **Preservar trazabilidad en runtime**
   - el sistema debe conservar al menos:
     - `qa_id`
     - fuente(s) usadas
   - aunque sea en logs internos o estructura de contexto
3. **Cerrar criterio para respuestas sintetizadas**
   - si una respuesta mezcla varias entradas, debe seguir siendo auditable
4. **Definir política cuando no hay fuente suficiente**
   - no inventar claims
   - no mezclar fuentes ambiguas como si fueran una sola

### No obligatorio en esta fase

- `source_section`
- `source_page`
- `source_ref`

Pueden añadirse después, pero no son requisito para cerrar `1.3`.

### Evidencia requerida para cierre

1. decisión de modelado multi-fuente
2. ejemplo de estructura interna/log donde se preserve `qa_id + source`
3. 3 ejemplos auditables:
   - producto específico
   - contenido de línea/empresa
   - comparativa multi-fuente

---

## 1.4 Cobertura por agente y por producto
**Estado:** Pendiente  
**Bloquea avance:** Sí, después de `1.3`

### Objetivo

Validar cobertura funcional real, no solo conteo de Q&As.

### Cobertura mínima esperada por producto

- **Productos:** composición, tecnología, indicaciones, protocolos, seguridad
- **Objeciones:** precio, eficacia, marca, comparativa
- **Argumentos:** perfil de paciente, especialidad, pitch, diferenciadores

### Evidencia requerida

- tabla de cobertura por producto
- huecos identificados
- decisión explícita sobre qué falta cargar

---

## 1.5 Política de comparativas y competencia
**Estado:** Parcial  
**Bloquea avance:** Sí, antes del cierre completo del bloque 1

### Objetivo

Definir cuándo el sistema puede comparar y cuándo debe negarse.

### Falta cerrar

- comparativas permitidas
- comparativas prohibidas
- comportamiento seguro si no hay soporte documental suficiente

### Evidencia requerida

- 1 comparativa permitida
- 1 comparativa rechazada correctamente
- política escrita en datos o documentación operativa

---

# BLOQUE 2 — Retrieval, routing y seguridad

## 2.1 Discriminación por producto, no solo por `product_line`
**Estado:** Parcial  
**Bloquea avance:** Sí

### Estado actual

- Ya existe base estructural por `product.id`
- Ya existen aliases y keywords por producto
- Pero aún no está auditado que el ranking use esa señal de forma explícita

### Cierre esperado

- ranking con señal real por `product.id`
- resolución correcta entre productos hermanos
- evidencia con top-3 y scores

---

## 2.2 Recalibración de BM25, thresholds y fallback
**Estado:** Parcial crítico  
**Bloquea avance:** Sí

### Riesgo abierto

- la normalización de scores puede debilitar thresholds absolutos
- fallback y `NO RESULTS` necesitan recalibración real

### Evidencia requerida

- matriz de pruebas con scores
- política de threshold
- comportamiento consistente para:
  - exactas
  - ambiguas
  - fuera de dominio

---

## 2.3 Separación real entre intención y producto
**Estado:** Sin verificar  
**Bloquea avance:** Sí

### Cierre esperado

- intención decide agente
- producto decide retrieval/contexto
- logs o trazas que lo demuestren

---

## 2.4 Reglas primero, LLM solo en ambigüedad
**Estado:** Sin verificar  
**Bloquea avance:** No, pero recomendado

---

## 2.5 `NO RESULTS` y anti-fabrication end-to-end
**Estado:** Parcial  
**Bloquea avance:** Sí

### Cierre esperado

- sin contexto suficiente → respuesta segura
- sin comparativas soportadas → rechazo seguro
- sin claims documentados → no inventar

---

## 2.6 Auditoría del léxico heredado y normalización clínica
**Estado:** Pendiente crítico  
**Bloquea avance:** Sí

### Problema abierto

Persisten residuos del dominio anterior en lógica o prompts visibles.  
Debe limpiarse antes del cierre técnico.

---

## 2.7 Suite mínima de regresión fija
**Estado:** Pendiente  
**Bloquea avance:** Sí, antes del cierre final

### Mínimo esperado

- 25–40 queries fijas
- esperado vs obtenido
- cobertura de:
  - productos
  - objeciones
  - argumentos
  - comparativas
  - fuera de dominio
  - ambigüedad

---

# BLOQUE 3 — Frontend y desacople real

## 3.1 FAQs y chips desde datos, no desde HTML hardcodeado
**Estado:** Pendiente  
**Bloquea avance:** Sí

## 3.2 Eliminar lógica de dominio/producto de `app.js`
**Estado:** Pendiente  
**Bloquea avance:** Sí

## 3.3 Limpieza de residuos activos del dominio anterior
**Estado:** Pendiente  
**Bloquea avance:** Sí

### Nota

Este punto incluye revisar:
- prompts visibles
- constantes frontend
- UI
- datos servidos en runtime

---

# BLOQUE 4 — Documentación, configuración y limpieza técnica

## 4.1 Actualizar `CLAUDE.md`, `README.md`, headers y versiones internas
**Estado:** Parcial  
**Bloquea avance:** Sí

### Estado actual

- Hay progreso reportado en versionado
- Falta auditoría completa de:
  - `README.md`
  - headers internos
  - consistencia final de versiones visibles

---

## 4.2 Centralizar configuración de modelos, providers, boosts y thresholds
**Estado:** Pendiente  
**Bloquea avance:** No, pero recomendado antes del cierre

---

## 4.3 Validación automática del schema al arrancar
**Estado:** Parcial sólido  
**Bloquea avance:** No para `1.3`

### Estado actual

- KB validada en startup
- catálogo validado en startup
- política `warn|strict` ya existe

### Falta cerrar

- política por entorno
- mensajes de error operativos
- validación integrada y documentada como estándar del proyecto

---

## 4.4 Higiene de despliegue: sacar páginas de prueba de `static/`
**Estado:** Pendiente  
**Bloquea avance:** No, pero debe cerrarse antes de producción final

---

## 4.5 Higiene de datos: `user_data.json`
**Estado:** Pendiente  
**Bloquea avance:** Sí, si participa en runtime o contiene residuos visibles

---

## 4.6 Consistencia de metadata global
**Estado:** Pendiente  
**Bloquea avance:** No

---

## 4.7 Modularización de `main.py` y `app.js`
**Estado:** Pendiente no bloqueante

---

# Siguiente punto activo

## 1.3 — Trazabilidad de fuentes

**No avanzar a 1.4 hasta cerrar `1.3`.**

### Evidencia mínima a pedir ahora

1. decisión de modelado para múltiples fuentes
2. evidencia de trazabilidad interna en runtime (`qa_id + source`)
3. 3 ejemplos auditables:
   - producto específico
   - línea/empresa
   - comparativa multi-fuente
4. criterio seguro cuando no exista soporte documental suficiente

---

# Plantilla obligatoria para cada cierre

Para marcar cualquier punto como cerrado, el ejecutor debe aportar:

1. **Qué cambió**
2. **Dónde cambió**
3. **Cómo se validó**
4. **Evidencia concreta**

Si falta una de las 4, el punto no se cierra.

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