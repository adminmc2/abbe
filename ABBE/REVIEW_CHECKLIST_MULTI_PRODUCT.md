# REVIEW_CHECKLIST_MULTI_PRODUCT

> Documento temporal de control de revisión.  
> Se actualiza después de cada punto cerrado y se elimina al finalizar la revisión.

## Contexto operativo actual

- Proyecto en migración multi-producto de **Above Pharma**
- **No** se está migrando el DNA de Novacutan; se está desacoplando la app y cargando productos nuevos
- La carga es **producto por producto**
- Decisión de agentes: **por intención** (`productos`, `objeciones`, `argumentos`)
- **No quedan puntos activos** en este checklist
- `3.1`, `3.2`, `3.3` y `4.1` quedan cerrados; la revisión queda finalizada

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
| 4. Documentación, configuración e higiene | **Cerrado** | `4.1` cerrado; documentación, versionado y superficies visibles alineadas a `v4.11.0` |

---

### Estado actualizado por puntos afectados

| Punto | Estado | Motivo |
|---|---|---|
| 3.1 Inventario de residuos legacy visibles y hardcodes runtime | **Cerrado** | Inventario completo, clasificado y utilizable |
| 3.2 Parametrización del frontend principal y eliminación de hardcodes visibles no legacy | **Cerrado** | UI principal ya no se comporta como demo/single-user por hardcodes visibles |
| 3.3 Limpieza de residuos activos del dominio anterior | **Cerrado** | Limpieza legacy ejecutada en `main.py`, `app.js`, `orb.js`, `style.css`, eliminación de HTML auxiliares públicos y validación grep `0 resultados` |
| 4.1 Documentación / versionado y consistencia visible final | **Cerrado** | Versión, documentación operativa y referencias visibles/documentales alineadas a `v4.11.0` |

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

### Qué se validó

- `ABBE/static/index.html`
- `ABBE/static/app.js`
- `ABBE/static/style.css`
- `ABBE/static/manifest.json`
- `ABBE/static/orb.js`
- HTML auxiliares públicos en `ABBE/static/`
- `ABBE/main.py` en los puntos que exponían copy o vocabulario operativo

### Evidencia concreta

#### Hallazgos que alimentaron `3.2`
- `Hola, Jorge` y `Tu plan, Jorge` hardcoded en `index.html`
- `profile.jpg` fijo para todos los usuarios
- versión visible `4.0.2` en login
- cache-busters desalineados en `style.css`, `favicon/icons/manifest`, `orb.js` y `app.js`
- `PLAN_TASKS` como dataset demo fijo mostrado como si fuera estado real del usuario
- `SEED_SEARCHES` documentado como hardcode visible no crítico y no persistente

#### Hallazgos que alimentaron `3.3`
- vocabulario legacy de estética / Novacutan en `app.js`
- `GREETING_RESPONSE` con ejemplos legacy en `main.py`
- `/api/test-infographic` con copy legacy en `main.py`
- `pharma_patterns` con vocabulario legacy en `main.py`
- `novacutanHue()` en `orb.js`
- HTML auxiliares públicos no productivos en `static/`, incluyendo páginas con copy `Novacutan` accesibles por URL directa

#### Hallazgos inertes / no bloqueantes
- comentarios `Novacutan` en `style.css` y `orb.js`
- comentarios internos en `app.js`
- páginas auxiliares con comentarios legacy no visibles, cuando el problema real ya quedaba cubierto por su condición de superficie pública no productiva

### Decisión actual

**`3.1` queda confirmado como base de `3.2` y `3.3`.**

---

## 3.2 Parametrización del frontend principal y eliminación de hardcodes visibles no legacy
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- `Jorge` dejó de aparecer hardcoded en la UI principal.
- La identidad visible usa `display name` separado de `abbe_user`.
- El avatar universal `profile.jpg` fue sustituido por avatar genérico basado en iniciales.
- La versión visible del frontend dejó de estar desalineada respecto a la versión activa.
- Los cache-busters de assets dejaron de estar mezclados.
- El plan dejó de mostrar dataset demo como si fueran datos reales del usuario.
- `SEED_SEARCHES` permanece visual-only y no persistente.
- Los residuos legacy específicos quedaron diferidos a `3.3`.

### Qué cambió

- Render dinámico de nombre visible en welcome y plan vía `updateGreetingUI()`
- Separación entre:
  - `abbe_user` → identidad normalizada
  - `abbe_display_name` → nombre visible preservando capitalización original
- Avatar por iniciales en lugar de imagen fija universal
- Alineación de versión visible y cache-busters del frontend
- `PLAN_TASKS` vaciado
- Placeholder vacío en plan hasta disponer de datos reales

### Dónde cambió

- `ABBE/static/index.html`
- `ABBE/static/app.js`
- `ABBE/static/style.css`
- `ABBE/main.py`
- `ABBE/CHANGELOG.md`

### Cómo se validó

- Revisión directa de implementación en frontend principal
- Verificación de persistencia de `abbe_display_name` en login y Face ID
- Verificación de render dinámico de greeting / plan / avatar
- Verificación de versión visible y query strings de assets
- Verificación de plan vacío sin dataset demo hardcoded

### Evidencia concreta

#### `index.html`
- Greeting base neutra: `Hola`
- Plan base neutra: `Tu plan`
- Avatar genérico inicial: `<span class="profile-initials">?</span>`
- Footer visible alineado con la versión actual
- Assets con query strings alineados entre sí

#### `app.js`
- `getDisplayName()` y `updateGreetingUI()` controlan greeting, plan y avatar
- `handleLogin()` guarda:
  - `abbe_user = username.trim().toLowerCase()`
  - `abbe_display_name = username.trim()`
- `handleFaceID()` preserva `abbe_display_name`
- `handleLogout()` limpia `abbe_display_name`
- `PLAN_TASKS = []`
- `renderPlanTasks()` deja placeholder:
  - `Aún no tienes tareas programadas`

#### `style.css`
- Nueva clase `.profile-initials` para avatar textual

### Observación no bloqueante

- `getDisplayName()` mantiene fallback a `abbe_user` como compatibilidad si falta `abbe_display_name` en sesiones antiguas.
- No reabre `3.2`.

### Decisión actual

**`3.2` queda cerrado.**

---

## 3.3 Limpieza de residuos activos del dominio anterior
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- Se eliminaron los residuos legacy operativos detectados en frontend y backend expuesto.
- Se alineó el vocabulario operativo entre `app.js` y `main.py`.
- Se neutralizó el branding runtime residual en `orb.js`.
- Se eliminaron las superficies públicas auxiliares no productivas dentro de `static/`.
- Se limpió el versionado visible a `v4.11.0`.

### Qué cambió

- `GREETING_RESPONSE` reescrito con ejemplos CTM / Gencell actuales
- `/api/test-infographic` reescrito a medicina regenerativa / CTM
- `pharma_patterns` limpiado de vocabulario estética / fillers legacy
- prompts y copy operativo backend alineados al dominio actual
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
  - `pharma_patterns` y prompts operativos ya no conservan vocabulario legacy de fillers / estética
  - docstring, `FastAPI.version` y `/api/health` en `4.11.0`
- `app.js`:
  - `isActionableQuery()` limpiado
  - `classifySearchIcon()` limpiado
  - mapa de iconos limpiado
- `orb.js`:
  - `brandHue()` sustituye a `novacutanHue()`
- `style.css`:
  - comentarios branding legacy eliminados o renombrados a Above Pharma
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
**Estado:** Cerrado  
**Bloquea avance:** No

### Cierre alcanzado

- La versión visible y operativa quedó alineada a `v4.11.0` en backend, frontend y documentación principal.
- `README.md` dejó de apuntar a `.env` como fuente de credenciales de prueba.
- `smoke_26_manual.md` quedó alineado a la versión operativa actual.
- `manifest.json` quedó consistente con el branding final del proyecto.
- `regression_report.md` se mantiene como artefacto generado vigente y no requiere edición manual.
- No quedan referencias activas a artefactos obsoletos como `regression_report.txt`.

### Qué cambió

- Ajuste documental de credenciales de prueba en `README.md`
- Alineación de versión/precondiciones en `regression/smoke_26_manual.md`
- Registro de cierre documental en `CHANGELOG.md`
- Verificación final de consistencia entre:
  - `main.py`
  - `static/index.html`
  - `static/manifest.json`
  - documentación raíz
  - documentación de regresión

### Dónde cambió

- `ABBE/README.md`
- `ABBE/regression/smoke_26_manual.md`
- `ABBE/CHANGELOG.md`

### Cómo se validó

- Revisión directa de las superficies en alcance de `4.1`
- Verificación de versión visible en frontend y backend
- Verificación de branding en `manifest.json`
- Confirmación de ausencia de referencias obsoletas a `regression_report.txt`
- Revisión de documentación operativa y artefactos de regresión vigentes

### Evidencia concreta

- `ABBE/main.py`:
  - docstring en `4.11.0`
  - `FastAPI.version = "4.11.0"`
  - `/api/health` devuelve `4.11.0`
- `ABBE/static/index.html`:
  - footer visible `Versión 4.11.0`
  - assets con `?v=4.11.0`
- `ABBE/static/manifest.json`:
  - branding actual: `Abbe - Above Pharma`
- `ABBE/README.md`:
  - credenciales de prueba ya no apuntan a `.env`
  - texto alineado a consulta con el equipo de desarrollo
- `ABBE/regression/smoke_26_manual.md`:
  - precondiciones actualizadas a `v4.11.0+`
- `ABBE/regression/regression_report.md`:
  - artefacto vigente en ruta correcta
  - no requiere edición manual para el cierre de `4.1`
- `ABBE/CHANGELOG.md`:
  - `v4.11.0` documentada como versión actual
  - cierre documental de `4.1` reflejado
- Verificación final:
  - no quedan referencias activas a `regression_report.txt`
  - no quedan versiones antiguas visibles en superficies activas fuera del histórico documental

### Decisión actual

**Se cierra `4.1`.**  
**Se cierra el bloque 4.**  
**Se cierra la revisión completa.**

---

# Estado final de la revisión

## Revisión cerrada

- No quedan puntos activos en este checklist.
- Los bloques `1`, `2`, `3` y `4` quedan cerrados.
- La versión operativa/documental final validada es `v4.11.0`.

### Siguiente acción

**Eliminar este archivo** tras consolidar el cierre en la documentación permanente del proyecto.

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
- `4.1` queda cerrado con documentación, versionado y consistencia visible final alineados a `v4.11.0`
- El bloque 4 queda finalizado
- La revisión completa queda cerrada y este checklist queda listo para eliminación