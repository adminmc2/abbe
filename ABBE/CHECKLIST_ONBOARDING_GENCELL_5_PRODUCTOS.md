# CHECKLIST_ONBOARDING_GENCELL_5_PRODUCTOS

> Documento operativo temporal para el onboarding del batch Gencell actual.

## Jerarquía documental

Este checklist forma parte de una estructura de 3 documentos con funciones distintas:

| Documento | Tipo | Función |
|---|---|---|
| `../GUIA_REVISION_AGENTES_MULTI_CONTEXTO.md` | Marco permanente reusable | Define la metodología general de revisión para sistemas de agentes IA |
| `REVIEW_CHECKLIST_MULTI_PRODUCT.md` | Registro cerrado/histórico | Conserva la trazabilidad de la revisión multi-producto ya completada |
| **Este archivo** (`CHECKLIST_ONBOARDING_GENCELL_5_PRODUCTOS.md`) | Documento operativo activo | Gobierna el onboarding actual del batch Gencell producto por producto |

---

## Contexto operativo actual

- Batch actual: **solo Gencell**
- Total de productos en scope: **5**
- Productos ya cargados y validados:
  - `ctm_estabilizador_renal` — CTM Estabilizador Renal
  - `ctm_metabolica` — CTM Metabólica
  - `exocell` — EXOCELL
- Productos en curso / pendientes de cierre:
  - `nk_autologas` — validación `5.5` activa
  - `nk_doble_bloqueo` — pendiente
- **No** entra MyFiller en este batch
- `product_line` única del batch: `gencell`
- Competidores del batch actual: `[]`
- Orden operativo aprobado:
  1. `exocell` — **cerrado**
  2. `nk_autologas` — **activo**
  3. `nk_doble_bloqueo` — **pendiente**
- El orden **no cambia el resultado funcional final**; se usa para **aislar regresiones y detectar confusión entre productos**
- `EXOCELL` quedó integrado y validado en **`v4.12.2`**
- Punto activo actual: **`5.5` — validación de `nk_autologas` (pendiente cierre revisor)**

---

## Freeze oficial de alcance aprobado

| # | Producto | ID | product_line | source_doc | Estado |
|---|---|---|---|---|---|
| 1 | CTM Estabilizador Renal | `ctm_estabilizador_renal` | `gencell` | `FICHA CTM estabilizador renal.pdf` | Cargado y validado |
| 2 | CTM Metabólica | `ctm_metabolica` | `gencell` | `FICHA CTM metabolica.pdf` | Cargado y validado |
| 3 | EXOCELL | `exocell` | `gencell` | `FICHA FIBROBLASTOS exocell.pdf` | Cerrado (`5.2`–`5.6`) |
| 4 | Natural Killer Autólogas | `nk_autologas` | `gencell` | `FICHA NKS natural killer autologa.pdf` | En validación (`5.5` activo) |
| 5 | Natural Killer Doble Bloqueo Autólogas | `nk_doble_bloqueo` | `gencell` | `FICHA NKS natural killer DB autologa.pdf` | Pendiente |

### Regla fijada para `source_doc`

- En `knowledge_base.json`, cada Q&A debe usar el **nombre exacto del PDF** aprobado para ese producto
- No sustituir `source_doc` por descripciones libres

---

## Decisiones ya fijadas

1. La ejecución se hace **producto por producto**, no en bloque.
2. El inventario y freeze de alcance se hace a nivel de batch.
3. No se crea una nueva `product_line`; todo este batch entra en `gencell`.
4. `competitors: []` se mantiene en este batch.
5. No se añaden campos nuevos a `catalog.json` sin validar antes el schema y el validador actual.
6. No se añaden categorías nuevas a `knowledge_base.json`.
7. No se toca `main.py`, `app.js` ni frontend por defecto.
8. `5.4` solo se abre si, tras catálogo + KB + validación, aparecen huecos reales.
9. Cualquier vocabulario estético que entre por `EXOCELL` deja de ser **legacy** y pasa a ser legítimo en runtime **solo** si queda ligado al producto correcto y con soporte documental real.
10. La confusión entre `nk_autologas` y `nk_doble_bloqueo` será un riesgo crítico de validación en `5.5`.

---

## Estado global del batch

| Punto | Estado | Nota |
|---|---|---|
| 5.1 Inventario y freeze de alcance | **Cerrado** | Scope, IDs, `source_doc`, orden y competidores fijados |
| 5.2 Alta en `catalog.json` | **Cerrado (exocell, nk_autologas)** | `nk_doble_bloqueo` pendiente |
| 5.3 Alta en `knowledge_base.json` | **Cerrado (exocell, nk_autologas)** | 18+18 Q&As cargados; `nk_doble_bloqueo` pendiente |
| 5.4 Ajustes semánticos mínimos si hacen falta | **Cerrado (exocell, nk_autologas)** | EXOCELL + NK: runtime ajustado con vocabulario real |
| 5.5 Regresión y validación cruzada | **Activo (nk_autologas)** | Pendiente cierre revisor |
| 5.6 Versionado y documentación por batch | **Ejecutado por lotes** | EXOCELL: `v4.12.2`; NK Autólogas: `v4.13.1`; pendiente repetir para `nk_doble_bloqueo` |

---

## 5.1 Inventario y freeze de alcance
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Quedó fijado el alcance oficial del batch actual: **solo Gencell**
- Quedó fijado el total de productos en scope: **5**
- Quedaron aprobados los nombres canónicos e IDs de los 3 productos nuevos
- Quedaron aprobados los `source_doc` exactos por producto
- Quedó fijado `competitors: []` para este batch
- Quedó fijado el orden operativo de onboarding para control de regresión

### Qué se cerró

- Scope oficial del batch
- Lista completa de productos
- IDs canónicos
- `product_line`
- `source_doc`
- Política de competidores
- Orden operativo

### Cómo se validó

- Confirmación explícita del usuario sobre scope
- Confirmación explícita de nombres canónicos e IDs
- Confirmación explícita de los PDFs como fuente oficial
- Confirmación explícita de `competitors: []`
- Confirmación explícita del orden operativo

### Evidencia concreta

- Scope total aprobado:
  - `ctm_estabilizador_renal`
  - `ctm_metabolica`
  - `exocell`
  - `nk_autologas`
  - `nk_doble_bloqueo`
- `product_line` única aprobada:
  - `gencell`
- `source_doc` aprobados:
  - `FICHA CTM estabilizador renal.pdf`
  - `FICHA CTM metabolica.pdf`
  - `FICHA FIBROBLASTOS exocell.pdf`
  - `FICHA NKS natural killer autologa.pdf`
  - `FICHA NKS natural killer DB autologa.pdf`
- Política de competidores:
  - `[]`
- Orden operativo aprobado:
  - `exocell` → `nk_autologas` → `nk_doble_bloqueo`

### Decisión actual

**Se cierra `5.1`.**  
**Se habilita avance a `5.2` producto por producto.**

---

## 5.2 Alta en `catalog.json`
**Estado:** Cerrado (exocell, nk_autologas)
**Bloquea avance:** No (pendiente solo nk_doble_bloqueo)

### Objetivo real del punto

Dar de alta cada producto nuevo en `catalog.json` respetando el contrato vigente del catálogo y sin introducir cambios innecesarios fuera del alcance.

### Cierre alcanzado para `exocell`

- `exocell` quedó dado de alta dentro de `gencell`
- La entrada quedó alineada con el naming canónico aprobado
- Se mantuvo `competitors: []`
- No se creó una nueva `product_line`
- La descripción de `gencell` quedó alineada al estado real cargado en ese momento, sin anticipar oncología antes de cargar los productos NK

### Qué cambió para `exocell`

- Alta de `exocell` como 3er producto de `gencell`
- Definición de aliases, synonyms y keywords útiles para retrieval
- Normalización de la entrada sin extender el schema de catálogo

### Cómo se validó para `exocell`

- Validador de catálogo OK al arrancar
- Revisión de colisiones con:
  - `ctm_estabilizador_renal`
  - `ctm_metabolica`
  - productos NK aún no cargados
- Verificación de consistencia con `source_doc` del producto

### Evidencia concreta de `exocell`

- `catalog.json`:
  - `product_line = gencell`
  - `id = exocell`
  - nombre canónico: `EXOCELL`
- Validación:
  - `1` línea
  - `3` productos
  - sin errores de catálogo

### Decisión actual

**`5.2` queda cerrado para `exocell`.**

### Cierre alcanzado para `nk_autologas`

- `nk_autologas` dado de alta como 4to producto de `gencell`
- Aliases: 6 variantes discriminantes (incluyen "autólogas" y "nivolumab")
- Sinónimos NK añadidos: natural killer, nivolumab, neoplasia, nsclc, dlbcl, tnbc
- Descripción Gencell actualizada a "medicina regenerativa, estética y oncología"
- Technologies: añadidos "Células NK autólogas" e "Inmunoterapia oncológica"
- Validación: `[Catalog] ✓ Validation passed (1 lines, 4 products)`

### Decisión actual

**`5.2` queda cerrado para `nk_autologas`.**
**Pendiente repetir para `nk_doble_bloqueo`.**

---

## 5.3 Alta en `knowledge_base.json`
**Estado:** Cerrado (exocell, nk_autologas)
**Bloquea avance:** No (pendiente solo nk_doble_bloqueo)

### Objetivo real del punto

Cargar Q&As reales por producto en `knowledge_base.json` respetando el contrato vigente, las categorías válidas y la trazabilidad por `source_doc`.

### Cierre alcanzado para `exocell`

- Se añadieron `18` Q&As de `exocell`
- Se cubrieron las `10` categorías cerradas del sistema
- Se usó `FICHA FIBROBLASTOS exocell.pdf` como fuente oficial
- La Q&A corporativa (`id: 1`) quedó actualizada para incluir EXOCELL y su fuente documental
- Se eliminó la fuga de alcance que mencionaba NK antes de cargar esos productos

### Qué cambió para `exocell`

- Nuevas entradas:
  - `ids 51–68`
- Ajustes de trazabilidad:
  - `id: 1` actualizada con `source_doc` completo
- Limpieza de alcance:
  - retirada referencia anticipada a NK en contenido de EXOCELL

### Cómo se validó para `exocell`

- Validador de KB OK al arrancar
- Contrato de datos completo
- IDs únicos
- Categorías válidas
- Verificación de `source_doc` exacto

### Evidencia concreta de `exocell`

- `knowledge_base.json`:
  - `total_preguntas = 68`
  - `18` Q&As nuevas para `exocell`
  - `source_doc = FICHA FIBROBLASTOS exocell.pdf`
- Validación:
  - contrato OK
  - IDs únicos
  - sin referencias NK dentro del bloque EXOCELL

### Decisión actual

**`5.3` queda cerrado para `exocell`.**

### Cierre alcanzado para `nk_autologas`

- 18 Q&As creados (ids 69–86) cubriendo las 10 categorías
- `source_doc` = `FICHA NKS natural killer autologa.pdf`
- Q&A id 1 (corporativa) actualizada para incluir NK Autólogas + source_doc ampliado
- Sin referencia a `nk_doble_bloqueo` (no cargado aún)
- `total_preguntas` = 86

### Decisión actual

**`5.3` queda cerrado para `nk_autologas`.**
**Queda pendiente repetir `5.3` para `nk_doble_bloqueo`.**

---

## 5.4 Ajustes semánticos mínimos si hacen falta
**Estado:** Cerrado (exocell, nk_autologas)
**Bloquea avance:** No

### Objetivo real del punto

Ajustar runtime o frontend **solo** si el catálogo y la KB ya cargados no bastan para que consultas naturales del producto lleguen correctamente al sistema.

### Apertura real para `exocell`

Este punto **sí** tuvo que abrirse para `exocell` porque había consultas naturales del producto que podían caer como saludo/vagas y no llegar al retrieval.

### Cierre alcanzado para `exocell`

- `main.py`:
  - ampliado `is_greeting_or_vague()` con vocabulario real de EXOCELL
  - añadido ejemplo EXOCELL a `GREETING_RESPONSE`
- `static/app.js`:
  - ampliado `isActionableQuery()` con el mismo vocabulario
  - ampliado `classifySearchIcon()` para EXOCELL / fibroblastos / rejuvenecimiento

### Evidencia concreta de `exocell`

- Cobertura añadida para términos de uso natural como:
  - `exocell`
  - `fibroblastos`
  - `rejuvenecimiento`
  - `arrugas`
  - `piel`
  - `subdérmica`
  - `firmeza`
  - `elasticidad`
  - `textura`
  - `placenta`
  - `dermatólogo`
  - `estético`

### Decisión actual

**`5.4` queda cerrado para `exocell`.**

### Apertura real para `nk_autologas`

El revisor detectó que consultas NK de primer turno (natural killer, nk autólogas, nivolumab, melanoma, nsclc, dlbcl, tnbc, oncología, "¿qué son las NK?") caían como saludo/vagas y no llegaban al RAG.

### Cierre alcanzado para `nk_autologas`

- `main.py`:
  - ampliado `is_greeting_or_vague()` con 21 términos NK/oncológicos
  - añadido patrón `que son` (antes solo `que es`)
- `static/app.js`:
  - ampliado `isActionableQuery()` con los mismos 21 términos + `que son`
  - ampliado `classifySearchIcon()` con natural killer, nk, nivolumab, oncología, melanoma, neoplasia

### Evidencia concreta de `nk_autologas`

- Cobertura añadida para términos NK/oncológicos:
  - `natural killer`, `nk`, `nks`, `nivolumab`
  - `neoplasia`, `oncolog`, `tumor`, `cancer`, `melanoma`
  - `nsclc`, `dlbcl`, `tnbc`, `lla`
  - `linfoma`, `leucemia`, `perforina`, `granzima`
  - `pd-1`, `pd-l1`, `mhc`, `apoptosis`
  - `quimioterapia`, `antitumoral`, `citotoxi`

### Decisión actual

**`5.4` queda cerrado para `nk_autologas`.**
**Solo se reabrirá si `nk_doble_bloqueo` muestra huecos reales de runtime.**

---

## 5.5 Regresión y validación cruzada
**Estado:** Activo (nk_autologas pendiente cierre revisor)
**Bloquea avance:** Sí

### Objetivo real del punto

Verificar que cada producto nuevo no rompa el comportamiento de los ya cargados y que no haya confusión entre productos hermanos o dominios distintos.

### Cierre alcanzado para `exocell`

- Retrieval correcto para consultas propias de EXOCELL
- No regresión sobre:
  - `ctm_estabilizador_renal`
  - `ctm_metabolica`
- Sin confusión operativa entre EXOCELL y los productos CTM
- Sin fuga anticipada hacia productos NK no cargados todavía
- El cierre documental y runtime quedó consolidado en `v4.12.2`

### Cómo se validó para `exocell`

- Validadores de catálogo y KB
- Batería manual de consultas de retrieval
- Revisión de no regresión sobre CTM
- Confirmación de no confusión entre productos ya cargados

### Evidencia concreta de `exocell`

- Validación reportada:
  - `9/9` queries correctas
  - sin regresión CTM
  - sin confusión entre productos
- Casos cubiertos:
  - `¿Qué es EXOCELL?`
  - `fibroblastos rejuvenecimiento`
  - consultas CTM siguen resolviendo a su producto correcto

### Decisión actual

**`5.5` queda cerrado para `exocell`.**

### Cierre alcanzado para `nk_autologas`

- Retrieval correcto para 7 queries propias de NK Autólogas (score 4.94–38.42)
- No regresión sobre CTM Renal, CTM Metabólica ni EXOCELL
- 13/13 queries totales correctas sin confusión entre 4 productos
- Sin fuga anticipada hacia `nk_doble_bloqueo` (no cargado aún)

### Decisión actual

**`5.5` pendiente de cierre para `nk_autologas` (requiere aprobación del revisor).**
**Queda pendiente repetir `5.5` para `nk_doble_bloqueo`.**

---

## 5.6 Versionado y documentación por batch
**Estado:** Ejecutado por lotes (exocell: `v4.12.2`, nk_autologas: `v4.13.1`)
**Bloquea avance:** No

### Objetivo real del punto

Cerrar cada lote aprobado con versión nueva, documentación alineada y superficies visibles consistentes.

### Cierre alcanzado para `exocell`

- La integración de EXOCELL quedó consolidada en **`v4.12.2`**
- `main.py`, `static/index.html` y `CHANGELOG.md` quedaron sincronizados
- `README.md` quedó actualizado a:
  - `68` Q&As
  - `3` productos actuales
  - inclusión de EXOCELL
- Este checklist quedó alineado con el cierre de EXOCELL y el avance a NK

### Dónde cambió para `exocell`

- `ABBE/main.py`
- `ABBE/static/index.html`
- `ABBE/CHANGELOG.md`
- `ABBE/README.md`
- `ABBE/CHECKLIST_ONBOARDING_GENCELL_5_PRODUCTOS.md`

### Evidencia concreta de `exocell`

- Versión operativa/documental:
  - `v4.12.2`
- Documentación:
  - `README.md` ya refleja EXOCELL y `68` Q&As
  - checklist actualizado con `exocell` cerrado

### Decisión actual

**`5.6` queda cerrado para `exocell`.**

### Cierre alcanzado para `nk_autologas`

- Versión: `v4.13.1`
- `main.py`, `index.html`, `CHANGELOG.md` sincronizados
- `README.md`: 86 Q&As, 4 productos actuales
- `CHECKLIST_ONBOARDING`: actualizado con estado NK Autólogas

### Decisión actual

**`5.6` ejecutado para `nk_autologas` en `v4.13.1`.**
**Queda pendiente repetir para `nk_doble_bloqueo`.**

---

## Secuencia aprobada de ejecución

1. `5.5` — cierre revisor de `nk_autologas`
2. `5.2` — alta de `nk_doble_bloqueo` en `catalog.json`
3. `5.3` — alta de `nk_doble_bloqueo` en `knowledge_base.json`
4. validadores
5. smoke mínimo y no regresión sobre CTM + EXOCELL + NK Autólogas
6. `5.4` solo si aparecen huecos reales
7. `5.5` — regresión y no confusión entre productos hermanos NK
8. `5.6` — versión + `CHANGELOG.md` + documentación del lote aprobado
9. repetir el ciclo con:
   - `nk_doble_bloqueo`

---

## Riesgos críticos del batch

1. `EXOCELL` reintroduce vocabulario estético de forma legítima.
2. `nk_autologas` y `nk_doble_bloqueo` son productos hermanos con alto riesgo de confusión.
3. `EXOCELL` contraindica neoplasia, mientras los productos NK se orientan a neoplasia.
4. La discriminación por `product.id` será crítica para el retrieval.
5. No deben entrar comparativas si no existe soporte documental y competidores cargados.

---

## Historial breve de decisiones fijadas

- El batch actual queda limitado a **Gencell**
- El batch actual contiene **5 productos totales**
- MyFiller queda fuera de este batch
- Los PDFs nuevos quedan confirmados como fuente oficial
- `competitors: []` se mantiene en este batch
- El orden operativo aprobado es `exocell` → `nk_autologas` → `nk_doble_bloqueo`
- `5.1` queda cerrado
- `5.2` queda cerrado para `exocell`
- `5.3` queda cerrado para `exocell` con `18` Q&As (`ids 51–68`)
- `5.4` queda cerrado para `exocell` tras ampliar runtime/frontend con vocabulario real del producto
- `5.5` queda cerrado para `exocell` con no regresión y sin confusión operativa
- `5.6` queda cerrado para `exocell` en `v4.12.2`
- `5.2` queda cerrado para `nk_autologas` (4 productos en catálogo)
- `5.3` queda cerrado para `nk_autologas` con `18` Q&As (`ids 69–86`)
- `5.4` queda cerrado para `nk_autologas` tras ampliar runtime/frontend con vocabulario NK/oncológico + patrón `que son`
- `5.5` pendiente de cierre para `nk_autologas` (requiere aprobación revisor)
- `5.6` ejecutado para `nk_autologas` en `v4.13.1`
- El siguiente punto activo: cierre de `nk_autologas` por revisor, luego arrancar con `nk_doble_bloqueo`