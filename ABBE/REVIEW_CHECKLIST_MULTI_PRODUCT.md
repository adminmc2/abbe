# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando productos nuevos
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- El siguiente punto activo es `4.1`: **documentación / versionado y consistencia visible final**
- `3.1`, `3.2` y `3.3` quedan cerrados; el **bloque 3** queda finalizado

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
| 2. Retrieval, routing y seguridad | **Cerrado** | `2.1`–`2.7` cerrados; bloque 2 finalizado |
| 3. Frontend y desacople real | **Cerrado** | `3.1`–`3.3` cerrados; bloque 3 finalizado en `v4.11.0` |
| 4. Documentación, configuración e higiene | **En progreso** | `main.py`, `index.html`, assets y `CHANGELOG.md` ya reflejan `v4.11.0`; queda pendiente consistencia total de documentación y superficies restantes |

---

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 3.1 Inventario de residuos legacy visibles y hardcodes runtime | **Cerrado** | Inventario completo, clasificado y utilizable |
| 3.2 Parametrización del frontend principal y eliminación de hardcodes visibles no legacy | **Cerrado** | UI principal ya no se comporta como demo/single-user por hardcodes visibles |
| 3.3 Limpieza de residuos activos del dominio anterior | **Cerrado** | Limpieza legacy ejecutada en `main.py`, `app.js`, `orb.js`, `style.css` y eliminación de superficies públicas auxiliares |
| 4.1 Documentación / versionado y consistencia visible final | **Activo** | Falta cerrar verificación total de versión y documentación operativa tras `v4.11.0` |

---

## 3.1 Inventario de residuos legacy visibles y hardcodes runtime en frontend
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Ya existe inventario completo y clasificado de residuos legacy y hardcodes runtime en frontend.
- Se revisaron superficies principales y auxiliares accesibles por URL dentro de `static/`.
- Quedó separada la lista de hallazgos que alimentó `3.2` de la que alimentó `3.3`.
- `manifest.json` quedó sin hallazgos relevantes.
- Se documentaron no-hallazgos explícitos para `BioPRO`, `FBio`, `DVS` y `Puro Omega`.

### Qué cambió

- `GREETING_RESPONSE` reescrito con ejemplos CTM / Gencell actuales
- `/api/test-infographic` reescrito a medicina regenerativa / CTM
- `pharma_patterns` limpiado de vocabulario estética / fillers legacy
- `isActionableQuery()` limpiado y alineado con backend
- `classifySearchIcon()` limpiado
- mapa de iconos limpiado
- `novacutanHue()` renombrado a `brandHue()`
- comentarios legacy eliminados de `orb.js` y `style.css`
- HTML auxiliares públicos eliminados de `static/`
- versión y cache-busters alineados a `v4.11.0`

### Dónde cambió

- `ABBE/main.py`
- `ABBE/static/app.js`
- `ABBE/static/orb.js`
- `ABBE/static/style.css`
- `ABBE/static/index.html`
- `ABBE/CHANGELOG.md`

### Superficies eliminadas

- `ABBE/static/generate-icons.html`
- `ABBE/static/icon-generator.html`
- `ABBE/static/logo-test.html`
- `ABBE/static/orb-preview.html`
- `ABBE/static/orb-small-test.html`
- `ABBE/static/preview-icon.html`

### Cómo se validó

- Revisión directa de implementación en `main.py`, `app.js`, `orb.js`, `style.css` e `index.html`
- Confirmación de eliminación física de HTML auxiliares en `static/`
- Verificación de versión `v4.11.0` en backend, frontend y changelog
- Búsqueda final de residuos legacy en `static/` y `main.py`

### Evidencia concreta

- `main.py`:
  - `GREETING_RESPONSE` ya usa ejemplos CTM / Gencell
  - `/api/test-infographic` ya usa texto de medicina regenerativa
  - `is_greeting_or_vague()` ya no conserva vocabulario legacy de fillers / estética
  - docstring, `FastAPI.version` y `/api/health` en `4.11.0`
- `app.js`:
  - `isActionableQuery()` limpiado
  - `classifySearchIcon()` limpiado
  - mapa de iconos limpiado
- `orb.js`:
  - `brandHue()` sustituye a `novacutanHue()`
- `style.css`:
  - comentarios branding legacy eliminados
- `index.html`:
  - footer visible `Versión 4.11.0`
  - assets con `?v=4.11.0`
- `static/`:
  - ya no existen HTML auxiliares públicos no productivos
- `CHANGELOG.md`:
  - nueva entrada `v4.11.0`
  - validación documentada:
    - `grep -RInE "Novacutan|hialuron|relleno|filler|reticulante|microesfera|rejuvenecimiento facial|dermatolog|cirujano plastico" static main.py`
    - resultado: `0 resultados`

### Nota de alcance

- No se reabren `agents/rag_engine.py` ni `agent_argumentos.py`.
- Según el checklist vigente, `3.3` se limitó a superficies activas/públicas y copy backend expuesto al frontend.

### Decisión actual

**Se cierra `3.3`.**  
**Se cierra el bloque 3.**  
**Se habilita avance a `4.1`.**

---

## 4.1 Documentación / versionado y consistencia visible final
**Estado:** Activo  
**Bloquea avance:** Sí

### Objetivo real del punto

Verificar que la versión actual, el artefacto de regresión y la documentación operativa queden consistentes en todas las superficies restantes tras `v4.11.0`.

### Alcance mínimo

- `ABBE/main.py`
- `ABBE/static/index.html`
- `ABBE/static/manifest.json`
- `ABBE/CHANGELOG.md`
- `ABBE/README.md` si existe
- `ABBE/regression/README.md`

### Evidencia mínima requerida

1. qué cambió
2. dónde cambió
3. cómo se validó
4. evidencia concreta de:
   - versión visible consistente
   - referencias documentales consistentes
   - ausencia de nombres de artefactos obsoletos
   - ausencia de versiones antiguas visibles o activas fuera del changelog histórico

### Decisión actual

**No avanzar más en el bloque 4 sin cerrar `4.1`.**

---

# Siguiente punto activo

## 4.1 — Documentación / versionado y consistencia visible final

**No avanzar más sin cerrar `4.1`.**

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
- Las baterías de `2.2` y `2.3` se convirtieron en regresión fija en `2.7`
- `3.1` queda cerrado con inventario clasificado de residuos legacy y hardcodes runtime en frontend, incluyendo superficies auxiliares públicas
- `3.2` queda cerrado con display name visible, avatar genérico por iniciales, versión/cache-busters alineados y plan sin dataset demo
- `3.3` queda cerrado con limpieza legacy en `main.py`, `app.js`, `orb.js`, `style.css`, eliminación de HTML auxiliares públicos y validación grep `0 resultados`
- El bloque 3 queda finalizado en `v4.11.0`
- `4.1` pasa a ser el punto activo para consistencia total de documentación y versionado visible