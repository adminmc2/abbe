# CHANGELOG - Above Pharma (Abbe)

Historial completo de desarrollo, problemas encontrados y soluciones aplicadas.

---

## v4.14.2 — 2026-04-25 (ACTUAL)

### Deploy en Hugging Face Spaces

- Dockerfile: puerto cambiado de 7862 a 7860 (requisito HF Spaces) + COPY catalog.json
- Deploy en HF Space `mandocc2/abbe` (Protected, Docker, CPU Basic)
- Dominio custom `abbe.prismaconsul.com` via Cloudflare (CNAME → `mandocc2-abbe.hf.space`)
- Keepalive configurado en cron-job.org (ping cada 30 min a `/api/health`)
- README.md y CLAUDE.md actualizados con info de deploy

---

## v4.14.1 — 2026-04-24

### Bloque 5.4c/5.5c: Fix bloqueantes revisor NK Doble Bloqueo

- `main.py` `is_greeting_or_vague()`: añadidos 6 términos exclusivos NK DB (ipilimumab, ctla-4, doble bloqueo, mesotelioma, colorrectal, msi)
- `app.js` `isActionableQuery()`: mismos 6 términos exclusivos NK DB
- `agents/rag_engine.py`: product.id boost aumentado de 1.25 a 1.5 (+50%)
- `agents/rag_engine.py`: añadido mismatch damping de 0.85 (−15%) para Q&As de producto no-coincidente cuando se detecta producto específico; Q&As con product=null quedan neutrales
- Colisión NK hermanos corregida: "nk autologas nivolumab" → nk_autologas (antes: nk_doble_bloqueo)
- Smoke test: 17/17 queries (7 gate + 6 retrieval DB + 4 no regresión)
- `CHECKLIST_ONBOARDING`: corregidas inconsistencias de cierre prematuro detectadas por revisor

---

## v4.14.0 — 2026-04-24

### Bloque 5.2c/5.3c: Onboarding NK Doble Bloqueo Autólogas (último producto del batch Gencell)

- Producto `nk_doble_bloqueo` dado de alta en `catalog.json` v5.0 bajo línea Gencell (5to y último)
- Aliases: 7 variantes discriminantes (incluyen "doble bloqueo", "ipilimumab", "nks-db")
- Sinónimos añadidos: ipilimumab, ctla-4, doble bloqueo, mesotelioma, colorrectal
- 18 Q&As creados en `knowledge_base.json` (ids 87–104) cubriendo las 10 categorías
- Q&A id 92: comparativa explícita NK Autólogas vs NK Doble Bloqueo (diferencias de pretratamiento, indicaciones, efectos adversos)
- Fuente: `FICHA NKS natural killer DB autologa.pdf`
- Q&A id 1 (corporativa): actualizada para incluir NK Doble Bloqueo + source_doc completo (5 fichas)
- Total KB: 104 Q&As (50 CTM + 18 EXOCELL + 18 NK Autólogas + 18 NK Doble Bloqueo)

Validación:
- `[Catalog] ✓ Validation passed (1 lines, 5 products)`
- `[RAG] ✓ KB validation passed (104 Q&As, contract OK)`
- 14/15 queries smoke test passed
- Discriminación NK hermanos: indicaciones exclusivas resuelven correctamente (DLBCL→autólogas, mesotelioma→DB)
- Colisión esperada: "nk autologas nivolumab" → DB (ambos usan nivolumab; Q&A 92 ayuda al LLM a discriminar)
- No regresión CTM Renal, CTM Metabólica, EXOCELL

---

## v4.13.1 — 2026-04-24

### Bloque 5.4b: Ajustes semánticos NK Autólogas

- `main.py` `is_greeting_or_vague()`: añadidos 21 términos NK/oncológicos (natural killer, nk, nivolumab, neoplasia, oncolog, tumor, cancer, melanoma, nsclc, dlbcl, tnbc, lla, linfoma, leucemia, perforina, granzima, pd-1, pd-l1, mhc, apoptosis, quimioterapia, antitumoral, citotoxi)
- `main.py` `is_greeting_or_vague()`: añadido patrón `que son` (antes solo `que es`)
- `main.py` `is_greeting_or_vague()`: añadido `evolocumab` (gap pre-existente CTM Metabólica)
- `app.js` `isActionableQuery()`: mismos 21 términos NK + `que son` + `evolocumab`
- `app.js` `classifySearchIcon()`: añadidos natural killer, nk, nivolumab, oncolog, melanoma, neoplasia
- `README.md`: corregida sección Knowledge Base (68→86 Q&As)
- `CHECKLIST_ONBOARDING`: 5.4 cerrado para nk_autologas con evidencia detallada

Validación:
- 22/22 first-turn query smoke test passed (15 NK/oncológicas + 4 existentes + 3 greetings correctamente vague)

---

## v4.13.0 — 2026-04-24

### Bloque 5.2b/5.3b: Onboarding Natural Killer Autólogas

- Producto `nk_autologas` dado de alta en `catalog.json` bajo línea Gencell
- Aliases: natural killer autólogas, nk autólogas, nk autologas, natural killer autologas, nk nivolumab, nks autólogas
- Sinónimos añadidos: natural killer, nivolumab, neoplasia, nsclc, dlbcl, tnbc
- Descripción Gencell actualizada a "medicina regenerativa, estética y oncología"
- Technologies actualizado con "Células NK autólogas" e "Inmunoterapia oncológica"
- 18 Q&As creados en `knowledge_base.json` (ids 69–86) cubriendo las 10 categorías
- Fuente: `FICHA NKS natural killer autologa.pdf`
- Q&A id 1 (corporativa): actualizada para incluir NK Autólogas + source_doc ampliado
- Total KB: 86 Q&As (50 CTM + 18 EXOCELL + 18 NK Autólogas)

Validación:
- `[Catalog] ✓ Validation passed (1 lines, 4 products)`
- `[RAG] ✓ KB validation passed (86 Q&As, contract OK)`
- 13/13 queries smoke test passed
- NK Autólogas: top correctos en 7 queries (score 4.94–38.42)
- No regresión CTM Renal, CTM Metabólica, EXOCELL
- Sin confusión entre los 4 productos

---

## v4.12.2 — 2026-04-24

### Bloque 5.4: Ajustes semánticos EXOCELL + correcciones revisor

- `main.py` `is_greeting_or_vague()`: añadidos 14 términos EXOCELL (exocell, fibroblasto, rejuvenecimiento, arruga, piel, subdérmica, cutáneo, firmeza, elasticidad, textura, metaloproteinasa, mmp, placenta, dermatólogo/estético)
- `app.js` `isActionableQuery()`: mismos 14 términos añadidos al gate del frontend
- `app.js` `classifySearchIcon()`: añadidos exocell, fibroblasto, rejuvenecimiento al clasificador de producto
- `GREETING_RESPONSE`: añadido ejemplo EXOCELL
- `knowledge_base.json` id 1: `source_doc` ampliado con `FICHA FIBROBLASTOS exocell.pdf`
- `CHECKLIST_ONBOARDING`: corregida inconsistencia entre tabla global y secciones detalladas

---

## v4.12.1 — 2026-04-24

### Correcciones post-revisión EXOCELL

- Q&A id 59: eliminada referencia a productos NK no cargados (fuga de alcance)
- Q&A id 1: actualizada descripción corporativa para incluir EXOCELL
- Q&As 63, 64, 67: eliminadas frases comparativas sin soporte documental ("se mantiene en el tiempo", "no es un relleno", "va más allá de rellenos/bioestimulación")
- `catalog.json`: eliminado "oncología" de descripción Gencell (producto NK aún no cargado)
- `README.md`: actualizado a 68 Q&As y 3 productos
- `CHECKLIST_ONBOARDING`: estado actualizado (5.2/5.3 cerrados para exocell)

Validación:
- `[Catalog] ✓ Validation passed (1 lines, 3 products)`
- `[RAG] ✓ KB validation passed (68 Q&As, contract OK)`
- 9/9 queries smoke test passed (EXOCELL + CTM sin regresión)
- Sin referencias NK en Q&As de EXOCELL

---

## v4.12.0 — 2026-04-24

### Bloque 5.2a/5.3a: Onboarding EXOCELL (fibroblastos alogénicos)

- Producto EXOCELL dado de alta en `catalog.json` bajo línea Gencell (id: `exocell`)
- Aliases: exocell, fibroblastos, fibroblastos alogénicos, fibroblastos de placenta, fibroblastos placentarios
- Sinónimos añadidos: exocell, fibroblastos, mmp, rejuvenecimiento
- 18 Q&As creados en `knowledge_base.json` (ids 51–68) cubriendo las 10 categorías
- Fuente: `FICHA FIBROBLASTOS exocell.pdf`
- Descripción de línea Gencell actualizada para incluir estética
- Total KB: 68 Q&As (50 CTM + 18 EXOCELL)

Validación:
- `[Catalog] ✓ Validation passed (1 lines, 3 products)`
- `[RAG] ✓ KB validation passed (68 Q&As, contract OK)`
- Retrieval EXOCELL: top 3 correctos (score 10.28+)
- No regresión CTM Renal: top 3 correctos (score 40.68+)
- No regresión CTM Metabólica: top 3 correctos (score 36.80+)
- Sin confusión entre productos

---

## v4.11.0 — 2026-04-23

### Bloque 3.3: Limpieza de residuos legacy activos

- `GREETING_RESPONSE` reescrito con ejemplos CTM/Gencell (eliminados "rejuvenecimiento facial" y "dermatólogo")
- `/api/test-infographic` texto de prueba reescrito a medicina regenerativa (eliminados "ácido hialurónico", "medicina estética")
- `pharma_patterns` en `is_greeting_or_vague()` limpiado de vocabulario estética/fillers (eliminados relleno, filler, hialuronico, reticulante, microesfera, zonas faciales, técnicas de inyección cosmética)
- `isActionableQuery()` en app.js limpiado de vocabulario legacy (alineado con backend)
- `classifySearchIcon()` limpiado: eliminados `hialuronic|relleno`, agregados `celula.?madre|estabilizador`
- Mapa de íconos: `hialuronico` → `estabilizador`
- `novacutanHue()` renombrado a `brandHue()` en orb.js (shader + alias)
- Comentarios "Novacutan" eliminados de orb.js y style.css
- 6 HTML auxiliares eliminados de `/static/`: generate-icons, icon-generator, logo-test, orb-preview, orb-small-test, preview-icon
- System prompts en main.py actualizados: ejemplo de extrapolación y template de producto alineados a CTM
- Versión y cache-busters alineados a v4.11.0

Validación: `grep -RInE "Novacutan|hialuron|relleno|filler|reticulante|microesfera|rejuvenecimiento facial|dermatolog|cirujano plastico" static main.py` → **0 resultados**

### Bloque 4.1: Consistencia de documentación y versionado

- `README.md`: corregida referencia de credenciales (apuntaba a `.env`, ahora a equipo de desarrollo)
- `regression/smoke_26_manual.md`: versión de precondiciones actualizada de `v4.9.3+` a `v4.11.0+`

---

## v4.10.1 — 2026-04-23

### Bloque 3.2: Parametrización del frontend principal

- `Hola, Jorge` y `Tu plan, Jorge` reemplazados por display name dinámico de sesión
- Avatar fijo `profile.jpg` sustituido por iniciales del usuario
- Versión visible corregida de `4.0.2` a `4.10.1` en login footer
- Cache-busters de assets alineados a `4.10.1` (style.css, app.js, orb.js, iconos, manifest)
- `PLAN_TASKS` dataset demo eliminado; plan muestra placeholder vacío hasta datos reales
- Separación display name (`abbe_display_name`) de identidad normalizada (`abbe_user`)
- Face ID preserva display name original al registrar y autenticar
- Fix: `regression_report.txt` → `regression_report.md` en CHANGELOG anterior

---

## v4.10.0 — 2026-04-23

### Bloque 2.7: Suite de regresión

- Nueva carpeta `ABBE/regression/` con suite de diagnóstico para bloques 2.2–2.6
- Runner unificado `run_all.py` con modos offline/runtime y filtro por bloque
- Artefacto de salida `regression_report.md`
- Smoke manual de 2.6 (`smoke_26_manual.md`) documentando flujo de navegador real
- README de ejecución

Scripts por bloque:
- 2.2: `diag_retrieval.py` (RAG BM25, 4 niveles de cobertura)
- 2.3: `diag_routing.py`, `diag_adversarial.py`, `diag_multiturn.py`
- 2.4: `diag_runtime_24.py`
- 2.5: `diag_25_noresults.py`, `diag_25_runtime.py`
- 2.6: `diag_26_historial.py`, `diag_26_final.py`

---

## v4.9.3 — 2026-04-23

### Bloque 2.6 fix: Sync no destruye búsquedas locales durante fetch

**Problema — Sync borra queries hechas durante el fetch:** `syncSearchHistory()` se dispara al login (async). Si el usuario hacía una consulta antes de que el servidor respondiera, la respuesta del sync (vacía o con datos viejos) destruía la búsqueda recién guardada.

**Corrección en `app.js`:**
- Rama servidor vacío: si hay datos locales frescos, push al servidor en vez de borrar
- Rama servidor más reciente: re-lee localStorage post-await, mergea búsquedas locales-only con las del servidor
- Resultado: queries hechas durante el fetch nunca se pierden

---

## v4.9.2 — 2026-04-23

### Bloque 2.6 fix: Race condition sync + normalización de identidad

**Problema 1 — Race condition en `syncSearchHistory()`:** La función capturaba `username` al inicio pero usaba `getSearchesKey()` (que lee `abbe_user` actual) al aplicar la respuesta. Si el usuario cambiaba durante el fetch, la respuesta se escribía en la key del nuevo usuario.

**Corrección en `app.js`:**
- `syncSearchHistory()` captura `syncKey` al inicio y lo usa en todo el callback
- Guard post-fetch: si `abbe_user` cambió, descarta la respuesta
- `pushSearchHistory()` construye `pushKey` fijo al inicio, no depende de `getSearchesKey()`

**Problema 2 — Normalización de username inconsistente:** `getSearchesKey()` usaba `toLowerCase()` pero `handleLogin()` guardaba el username solo con `trim()`. El backend recibía case-sensitive, el localStorage usaba case-insensitive.

**Corrección en `app.js`:**
- `handleLogin()`: `username.trim().toLowerCase()` al guardar `abbe_user`
- `handleFaceID()` registro: `faceIdUser` normalizado a lowercase
- Criterio unificado: username siempre normalizado en ambos lados

---

## v4.9.1 — 2026-04-23

### Bloque 2.6 fix: Aislamiento real de frontend multiusuario

**Problema 1 — Key localStorage global:** `abbe_recent_searches` era una sola clave compartida por todos los usuarios en el mismo navegador. En dispositivo compartido, un usuario veía/empujaba historial de otro.

**Corrección en `app.js`:**
- `RECENT_SEARCHES_KEY` (constante) → `getSearchesKey()` (función dinámica)
- Key scoped: `abbe_recent_searches:<app_id>:<username_normalizado>`
- Sin usuario logueado, usa key anónima aislada

**Problema 2 — Sync no limpiaba en servidor vacío:** Si `/api/history/load` devolvía `[]` (usuario nuevo), el frontend conservaba búsquedas del usuario anterior en localStorage.

**Corrección en `app.js`:**
- Rama `else` en `syncSearchHistory()`: cuando servidor vacío, `localStorage.removeItem(getSearchesKey())` + re-render

**Problema 3 — Seed data persistente:** `init()` insertaba búsquedas demo en localStorage como historial real. En multiusuario, se subían al servidor contaminando datos.

**Corrección en `app.js`:**
- `SEED_DATA` eliminado de `init()` → `SEED_SEARCHES` como constante visual
- `renderRecentSearches()` muestra seeds si historial vacío, sin persistir en localStorage

**Problema 4 — Logout incompleto:** `handleLogout()` solo limpiaba auth keys, dejando chat DOM, `priorContext`, y WebSocket activo del usuario anterior.

**Corrección en `app.js`:**
- Logout cierra `state.websocket`, limpia `state.priorContext`, `state.currentMessage`, y `chatMessages` DOM

**Problema 5 — Face ID sin username:** `handleFaceID()` seteaba `abbe_logged_in` pero nunca `abbe_user`, rompiendo toda la cadena de aislamiento.

**Corrección en `app.js`:**
- Registro Face ID: requiere username del campo login, lo vincula con `abbe_faceid_user`
- Autenticación Face ID: usa **solo** el usuario vinculado (`abbe_faceid_user`), ignora campo manual
- Si credencial huérfana (sin usuario vinculado), pide reconfiguración

**Problema 6 — Flash visual al cambiar de usuario:** `handleLogout()` no limpiaba el DOM de búsquedas recientes. Al hacer login como usuario B, el welcome screen mostraba brevemente los items de A.

**Corrección en `app.js`:**
- `handleLogout()` limpia `recent-searches-list` DOM
- `handleLogin()` llama `renderRecentSearches()` antes de `syncSearchHistory()` para estado inmediato correcto

**Corrección en `main.py`:**
- Versión sincronizada a `4.9.1` en docstring, `FastAPI.version` y `/api/health`

---

## v4.9.0 — 2026-04-23

### Bloque 2.6: Persistencia y aislamiento de historial por usuario

**Problema 1 — Credencial única:** `VALID_CREDENTIALS` solo permitía login como "Jorge". Todos los representantes compartían una sola identidad, imposibilitando historial individual.

**Corrección en `app.js`:**
- `VALID_CREDENTIALS` → `SHARED_PASSWORD`: cualquier username no vacío + password compartida
- `handleLogin()` acepta `username.trim()` libre, guarda identidad real en `localStorage.abbe_user`

**Problema 2 — Demo mode reset:** `checkAuthOnLoad()` borraba `abbe_logged_in` y `abbe_user` en cada recarga, forzando re-login constante.

**Corrección en `app.js`:**
- Eliminado `localStorage.removeItem()` incondicional
- Si hay sesión activa, se llama `syncSearchHistory()` automáticamente para rehidratar

**Problema 3 — Legacy contamina historial:** `user_data.json` contenía historiales de Novacutan (José Luis, Pablo) que podían hidratarse como historial actual de ABBE.

**Corrección en `app.js` + `main.py`:**
- Nuevo parámetro `app_id` en endpoints `/api/history/save` y `/api/history/load`
- Frontend envía `app_id: "abbe_above_pharma"` en cada sync
- Backend almacena bajo `data[username].apps[app_id]` — legacy queda en raíz, inaccesible
- Backward compatible: sin `app_id`, endpoints funcionan como antes

**Problema 4 — Trazas sin usuario:** `audit_traces.jsonl` solo tenía `session_id` anónimo, sin correlación con usuario de frontend.

**Corrección en `app.js` + `main.py`:**
- Frontend envía `username` en payload WebSocket
- Backend captura `frontend_user` y lo persiste en `write_audit_trace()`

---

## v4.8.0 — 2026-04-23

### Bloque 2.5: NO RESULTS, anti-fabricación y detección comparativa robusta

**Problema 1 — Comparativas no detectadas:** El patrón `\bmejor que\b` exigía adyacencia, pero en español "Es mejor X que Y" interpone X entre ambas palabras. Consultas como "¿Es mejor el CTM Renal que la diálisis?" pasaban sin gobernanza comparativa.

**Corrección en `base_agent.py` — COMPARATIVE_SIGNALS:**
- `\bmejor que\b` → `\bmejor\b.{1,80}\bque\b` (no adyacente, límite 80 chars)
- `\bpeor que\b` → `\bpeor\b.{1,80}\bque\b`
- Agregados: `\bfrente a\b`, `\bcomparado con\b`
- Corregidos acentos: `\bpor qué\b` → `\bpor qu[eé]\b`

**Problema 2 — Threshold comparativo heredado:** `score >= 0.15` en `evaluate_comparative_query()` era un residuo de la escala normalizada antigua. Con BM25 raw (scores 3–30+), no filtraba nada.

**Corrección en `base_agent.py`:**
- `score >= 0.15` → `score >= 3.0` (alineado con `min_score` de `format_context()`)

**Problema 3 — Traza sin modo runtime:** `audit_traces.jsonl` no persistía el modo final de respuesta (normal/acotada/rechazo), impidiendo auditar decisiones de runtime.

**Corrección en `main.py`:**
- Nuevo campo `effective_mode` calculado post-comparativa: `"normal"`, `"acotada"`, `"rechazo"`
- Persistido en `write_audit_trace()`

**Diagnóstico (10 queries offline + 4 runtime):**
- Q1-Q4 (fuera de dominio / residuos): low/no_results correctos
- Q5 (comparativa no detectada): FIX aplicado — ahora detectada como therapeutic
- Q6 (competidor): correctamente bloqueada (competitors=[])
- Q7-Q8 (comparativas soportadas): funcionan correctamente
- Q9-Q10 (intra-dominio con gap): coverage HIGH por BM25 léxico, pero anti-fabricación del prompt contiene el riesgo (verificado en runtime Caso 3 — lupus)

---

## v4.7.1 — 2026-04-22

### Bloque 2.4 (fix concurrencia): search_meta como valor de retorno

**Problema resuelto:** `search_knowledge_with_fallback()` guardaba el meta del fallback en un atributo mutable del agente (`self.last_search_meta`). Como los agentes son singleton (reutilizados entre sesiones WebSocket), otra sesión concurrente podía sobreescribir el meta antes de que `main.py` lo leyera (hay múltiples `await` entre la búsqueda y la escritura de la traza).

**Corrección en `base_agent.py`:**
- `search_knowledge_with_fallback()` ahora retorna `(results, search_meta)` como tupla
- Eliminado atributo mutable `self.last_search_meta`
- El meta se captura como variable local en el caller — sin ventana de concurrencia

**Corrección en `main.py`:**
- `results, search_meta = agent.search_knowledge_with_fallback(...)` — captura inmediata
- Eliminada lectura tardía de `agent.last_search_meta` (post-await)

---

## v4.7.0 — 2026-04-22

### Bloque 2.4: coherencia agente↔retrieval y fallback auditable

**Problema resuelto:** `fallback_used` en `audit_traces.jsonl` se calculaba con una heurística en `main.py` (`rag_coverage in ("low", "no_results")`) que no correspondía al trigger real del fallback en `search_knowledge_with_fallback()` (score < 8.0). Un fallback activado con score entre 5.0 y 8.0 quedaba invisible en la auditoría.

**Corrección en `base_agent.py`:**
- `search_knowledge_with_fallback()` retorna `(results, search_meta)` con estado real del fallback
- search_meta contiene: `fallback_activated`, `score_before_fallback`, `score_after_fallback`
- La señal es la verdad del sistema — no hay duplicación de thresholds

**Corrección en `main.py`:**
- `fallback_used` reemplazado por `fallback_activated` + scores antes/después del fallback
- Campos nuevos en traza: `fallback_activated`, `score_before_fallback`, `score_after_fallback`
- Eliminada heurística duplicada

**Diagnóstico previo (12 queries):**
- productos: 4/4 coherentes (0 nativos en top-3 es esperado — categoría nativa `protocolos` tiene solo 2 entries)
- objeciones: 4/4 coherentes (3+ nativos en top-3 siempre)
- argumentos: 3/4 coherentes (Q12 "pitch internista" sin contenido nativo = gap de contenido, no de retrieval)
- Fallbacks activados: 1/12 (Q8, mejora score de 7.99 a 8.79)

---

## v4.6.0 — 2026-04-22

### Bloque 2.3: routing por intención basado en frame comercial

**Problema resuelto:** `classify_intent_rules()` usaba patrones de vocabulario planos que confundían seguridad técnica con objeciones (ej: "contraindicaciones" siempre iba a `objeciones`) y no detectaba objeciones con variantes naturales ("el médico duda", "muy cara", "el médico me dice").

**Corrección en `orchestrator.py`:**
- Separación de patrones en 3 capas: `OBJECTION_DIRECT` (resistencia inequívoca), `COMMERCIAL_FRAME` (doctor + duda/preocupación, solicitud de respuesta), `ARGUMENT_PATTERNS`
- Términos técnicos (contraindicaciones, efectos secundarios, interacciones) ya no disparan objeciones por sí solos — necesitan frame comercial
- Corregido género en patrones de precio: `caro/cara`, `costoso/costosa`
- Frame del médico: solo verbos de resistencia real (`duda`, `cuestiona`, `objeta`, `preocupa`, `no cree`). Verbos neutros (`pregunta`, `dice`) NO disparan objeciones por sí solos — `dice/dijo` solo con resistencia posterior ("dice que no", "dice que es caro", "dice que le preocupa")
- Añadido `cardiólogo` y `endocrinólogo` a ARGUMENT_PATTERNS
- Añadido frame hipotético: `si me dice que`

**Validación adversarial:** "El médico pregunta la composición / contraindicaciones / administración / melatonina" → 4/4 correctamente a `productos` (no sobrerutean a objeciones)

**Diagnóstico pre-fix:** 10/13 single-turn, 3/6 multi-turn (6 misroutes)
**Diagnóstico post-fix:** 13/13 single-turn, 6/6 multi-turn, 4/4 adversariales = **23/23** (0 misroutes)

**Tipos de error corregidos:**
- Seguridad técnica mal enviada a objeciones (Q4, Flow A-T2)
- Objeciones no detectadas por falta de variantes verbales (Q6, Q8, Flow C-T1)
- Objeciones no detectadas por género masculino en regex (Flow B-T2)

---

## v4.5.0 — 2026-04-22

### Bloque 2.2: thresholds, scores y cobertura RAG real

**Problema resuelto:** `rag_engine.py` normalizaba scores a `[0,1]` dividiendo por el máximo, lo que hacía que el top result **siempre** tuviera score 1.0. Combinado con `max_score >= 0.5` en main.py, toda query con resultados era clasificada como `high`. El bucket `medium` nunca aparecía.

**Corrección en `rag_engine.py`:**
- Eliminada la normalización a `[0,1]` — ahora `search()` devuelve raw BM25 scores
- El ranking no cambia (ordenar por raw es equivalente a ordenar por normalizado)

**Corrección en `base_agent.py`:**
- `format_context()`: normaliza scores localmente solo para display (confianza relativa al top result)
- `min_score` ajustado: 0.1 (normalizado) → 3.0 (raw BM25)
- `search_knowledge_with_fallback()`: threshold ajustado: 0.25 (normalizado, nunca activaba fallback) → 8.0 (raw, ahora funciona)

**Nueva lógica de cobertura en `main.py` (raw scores calibrados):**
- `high`: max_raw ≥ 10.0 y ≥2 strong docs → queries específicas con match claro
- `medium`: max_raw ≥ 5.0 → queries amplias o match parcial
- `low`: max_raw > 0 pero < 5.0 → match muy débil
- `no_results`: sin resultados → bucket separado con instrucciones propias

**Calibración con 12 queries diagnósticas:**
- Antes: 10 high, 0 medium, 2 low
- Después: 8 high, 2 medium, 0 low, 2 no_results
- `medium` ahora captura correctamente queries genéricas (ej: "¿Cómo funcionan las CTM?" max_raw=5.9)

**Trazabilidad:** `audit_traces.jsonl` ahora registra el raw score real usado para cobertura, no un score normalizado que siempre valía 1.0.

---

## v4.4.0 — 2026-04-22

### Bloque 2.1: discriminación por product.id en ranking

**Detección de producto en query (`rag_engine.py`):**
- Nuevo método `_detect_product()` — resuelve `product.id` desde la query usando:
  - Señal fuerte: `product.name` y `aliases` del catálogo
  - Señal secundaria: `keywords` (conditions, pretreatment, zones)
- Data-driven: no hardcodea nombres, todo viene del catálogo
- Retorna `None` si no detecta producto específico (queries ambiguas mantienen comportamiento anterior)

**Metadata boost por product.id (+25%):**
- Se aplica en `search()` después del boost por `product_line` (+30%)
- Solo se aplica si `_detect_product()` detecta un producto y el Q&A tiene el mismo `product.id`
- `product=null` queda neutral (no se penaliza ni se boostea)
- Resultado: confusiones en top-3 pasan de 2/24 a 1/24 (el caso residual tiene score 0.072, filtrado por `min_score=0.1`)

---

## v4.3.0 — 2026-04-22

### Bloque 1.5: política comparativa explícita con enforcement runtime

**Política comparativa con evaluación en runtime (`base_agent.py`):**
- Nuevo método `evaluate_comparative_query()` en `BaseAgent` — clasifica consultas comparativas en 3 tipos:
  - `internal`: comparación entre productos del portafolio Above Pharma (siempre permitida)
  - `therapeutic`: comparación vs tratamiento convencional/alternativas (permitida solo si hay soporte en KB)
  - `competitor`: comparación vs marca/laboratorio externo (permitida solo si `catalog.json` tiene competidores cargados)
- Detección por señales regex: `vs`, `versus`, `diferencia`, `comparar`, `mejor que`, `otra marca`, `competencia`, `ya uso`, `cambiar`, etc.
- Detección de claims de superioridad: `mejor`, `superior`, `más eficaz`, `el único`, etc.
- La decisión NO depende solo de `rag_coverage` — verifica si los resultados RAG contienen soporte comparativo válido (categoría + score ≥ 0.15)

**Helpers de competidores data-driven (`catalog.py`):**
- `has_competitors()` → `True` cuando se carguen competidores en `catalog.json` (hoy `False`)
- `get_competitors()` → lista de competidores con `product_line` (hoy `[]`)
- Diseño: cuando se añadan competidores al catálogo, la política se activa automáticamente sin cambios de código

**Inyección comparativa en main.py:**
- Instrucciones comparativas inyectadas en el prompt LLM según tipo y decisión:
  - Rechazo de competidor: no comparar con marcas externas, redirigir a fortalezas propias
  - Rechazo terapéutico: no comparar sin soporte documental, presentar datos disponibles
  - Permitida: comparar solo con datos verificados, sin claims absolutos
- Advertencia automática si el usuario usa lenguaje de superioridad sin soporte
- Campo `comparative` añadido al audit trace (`audit_traces.jsonl`) con: `type`, `allowed`, `reason`, `has_superiority_claims`

**Alineación de prompts:**
- `agent_argumentos.py`: docstring corregido — "Comparativas con competencia" reemplazado por nota de que se evalúan en runtime
- `agent_objeciones.py`: docstring alineado con política de competidores

---

## v4.2.0 — 2026-04-22

### Bloque 1.3: trazabilidad end-to-end

**Normalización de fuentes:**
- `source_doc` se parsea a `normalized_sources: List[str]` al cargar la KB
- Convención: `"A.pdf + B.pdf"` → `["A.pdf", "B.pdf"]`
- El JSON no cambia; la normalización es interna en runtime

**Trazas de auditoría persistentes (`audit_traces.jsonl`):**
- Archivo append-only con una traza JSONL por interacción
- Cada traza incluye: `timestamp`, `session_id`, `query`, `intent`, `agent`, `rag_coverage`, `max_score`, `no_results`, `fallback_used`, `retrieved_results` (con `qa_id`, `categoria`, `product`, `product_line`, `normalized_sources`, `score`), `response_text`
- `session_id` generado por conexión WebSocket (sin datos sensibles)
- Archivo excluido de git (`.gitignore`)
- Mejora futura: migrar a Postgres/Neon cuando el volumen lo requiera

**Trazabilidad en contexto LLM:**
- `format_context()` ahora incluye `Fuente: {source_doc}` en cada hecho verificado
- El LLM puede citar la fuente documental en sus respuestas

**Anti-fabrication reforzado:**
- Cobertura RAG baja: eliminada referencia a ácido hialurónico (residuo dominio anterior)
- Reglas más estrictas: no sintetizar comparativas sin datos, indicar explícitamente falta de información
- Límite reducido a 100 palabras en cobertura baja

---

## v4.1.0 — 2026-04-22

### Bloque 1.2: contrato de datos del catálogo + canonicalización

**Validador de catálogo:**
- Nuevo `_validate_catalog()` en `catalog.py` con campos obligatorios por línea y producto
- Valida IDs únicos, tipos correctos (listas, dicts), detección de aliases duplicados entre productos
- Mismo modo `KB_VALIDATION_MODE=warn|strict` que la KB
- `get_catalog()` ya no hace fallback silencioso: en `strict` lanza error si falta `catalog.json`

**Canonicalización `product.id`:**
- Canónico interno: `product.id` (ej: `ctm_estabilizador_renal`)
- Nombre visible: `product.name` (ej: `CTM Estabilizador Renal`)
- Nuevos helpers canónicos:
  - `get_product_by_id()` — busca producto por ID
  - `get_product_name_map()` — `product.id → product.name`
  - `get_product_alias_to_id_map()` — `alias → product.id` (para routing/boost)
  - `get_product_keywords_map()` — `product.id → [keywords]` (para boost estructurado)
- `get_condition_product_map()` ahora retorna `product.id` en vez de `product.name`
- `agent_productos.py` actualizado para resolver `id → name` via `get_product_name_map()`
- Helpers legacy (`get_product_aliases`, `get_product_synonyms`, etc.) mantenidos sin romper consumidores

---

## v4.0.3 — 2026-04-22

### Bloque 1.1: contrato de datos enforced

**Correcciones:**
- `Q&A #1`: `source_doc` corregido a ambas fichas (mencionaba Metabólica pero solo citaba Renal)
- `Q&A #40`: `source_doc` ya corregido en v4.0.2

**Allowlist de categorías:**
- Nueva constante `VALID_CATEGORIES` en `RAGEngine` (10 categorías, fuente única de verdad)
- El validador ahora rechaza categorías fuera de la lista cerrada

**Validador configurable (warn/strict):**
- Variable de entorno `KB_VALIDATION_MODE` controla el comportamiento:
  - `warn` (default): reporta errores sin detener el arranque (producción)
  - `strict`: lanza `ValueError` y bloquea startup (local/predeploy)

---

## v4.0.2 — 2026-04-22

### Segundo producto: CTM Metabólica — validación multi-producto

**Producto cargado: CTM Metabólica (Gencell)**
- `catalog.json`: nuevo producto `ctm_metabolica` con aliases, condiciones cardiovasculares/metabólicas, sinónimos (evolocumab, PCSK9, hipercolesterolemia, dislipidemia, colesterol, endotelial)
- `knowledge_base.json`: 25 Q&As nuevas (IDs 26-50): 7 producto/tech + 5 seguridad + 5 objeciones + 5 argumentos + 2 comparativas + 1 perfil paciente
- Actualizada Q&A de empresa (ID 1) para mencionar ambos pretratamientos
- Q&A comparativa (ID 40): diferencia explícita entre Estabilizador Renal y Metabólica
- Total KB: 50 Q&As (25 Renal + 25 Metabólica)

**Validación multi-producto BM25 (12 queries):**
- 6 product-specific: discriminación perfecta (colesterol → Metabólica, renal → Renal)
- 2 cross-product: comparativa y listado de productos en resultados
- 2 specialist: cardiólogo → Metabólica, nefrólogo → Renal
- 1 ambigua: muestra contraindicaciones de ambos productos
- 1 fuera de dominio: NO RESULTS (correcto)
- Metadata boost (+30%) funcionando correctamente con 2 productos

---

## v4.0.1 — 2026-04-21

### Primer producto cargado + limpieza frontend completa

**Primer producto: Gencell CTM Estabilizador Renal**
- `catalog.json`: línea Gencell Biotechnology con CTM Estabilizador Renal (aliases, condiciones, zonas, sinónimos)
- `knowledge_base.json`: 25 Q&As (15 producto/tech + 5 objeciones + 5 argumentos) extraídas del PDF de ficha técnica
- BM25 validado con 10 queries reales — ranking correcto en todos los casos

**Limpieza de hardcodes Novacutan en frontend:**
- `app.js`: ~18 ediciones — localStorage keys (`abbe_mood`, `abbe_recent_searches`), classifiers, icon map, demo tasks, seed data, fallback messages, pharmaKeywords regex (añadidos términos de medicina regenerativa)
- `index.html`: 12 FAQ chips reescritos para CTM/Gencell (productos, objeciones, argumentos)
- `manifest.json`: nombre PWA → "Abbe - Above Pharma"
- `style.css`: tooltip de fuente externa → "Above Pharma"
- `agents/__init__.py`: comentario → "Above Pharma"

**Validación:**
- 0 referencias a Novacutan/BioPRO/FBio/DVS en archivos críticos (agents/, main.py, app.js, index.html)
- BM25 10/10 queries con resultados relevantes y ranking correcto
- Notas cosméticas pendientes: orb.js y archivos de test HTML aún contienen "Novacutan" en nombres de funciones/paletas de color (no afectan funcionalidad ni UI)

---

## v4.0.0 — 2026-04-21

### Refactor: Infraestructura multi-producto Above Pharma

Transformación completa de plataforma mono-producto (Novacutan) a multi-producto (Above Pharma). Se preservan intactas las metodologías de venta (FAB, Feel-Felt-Found, SPIN/Challenger Sale).

**Nuevos archivos:**
- `catalog.json` — Catálogo de productos
- `agents/catalog.py` — Módulo de gestión de catálogo (sinónimos dinámicos, mapa de condiciones, portafolio parametrizado)

**RAG Engine v3.0:**
- TF-IDF reemplazado por **BM25** (Okapi BM25, sin dependencias externas)
- Sinónimos separados: médicos (estáticos) + producto (dinámicos desde catálogo)
- **Metadata boost**: +30% para Q&As que coincidan con la línea de producto detectada
- Aliases de producto cargados desde catálogo (no hardcodeados)

**Agentes parametrizados:**
- Prompts inyectan empresa y portafolio desde `catalog.json`
- `agent_productos.py`: CONDITION_PRODUCT_MAP ahora dinámico desde catálogo
- `agent_objeciones.py`: prompt parametrizado, metodología Feel-Felt-Found intacta
- `agent_argumentos.py`: prompt parametrizado, SPIN/Challenger intactos
- `base_agent.py`: header "DATOS VERIFICADOS" ahora usa nombre de empresa dinámico

**Orchestrator:**
- CLASSIFICATION_PROMPT genérico (sin productos hardcodeados)

**main.py:**
- Greeting, TTS prompt, pharma_patterns y anti-fabrication sin referencias a Novacutan
- Versión → 4.0.0

**Knowledge Base:**
- Schema v2.0 con campos metadata: `product_line`, `product`, `source_doc`, `featured_faq`
- Contenido Novacutan archivado (recuperable desde git history)

---

## v3.8.4 — 2026-04-21

### Fix: Botón Wake Word eliminado del DOM

- Botones "Hola, Abbe · off" comentados en HTML (welcome y chat screens) para que no aparezcan independientemente del caché de CSS.
- Reactivables descomentando el HTML.

---

## v3.8.3 — 2026-04-21

### Unificación de versiones, rebrand y mejoras de UX

- **Versión unificada** — Sincronizada versión en `main.py`, `index.html` y CHANGELOG a `3.8.3`.
- **Rebrand Novia → Abbe** — Renombrado el asistente en todo el proyecto: UI, backend, prompts, wake words, localStorage keys, PWA manifest, documentación y directorio (`NOVIA/` → `ABBE/`).
- **Greeting TTS actualizado** — Nuevo mensaje de bienvenida al tocar el orb en login: "Hola, me llamo Abbe y soy tu asistente inteligente que te ayudará en todos los procesos de decisión y venta para los productos de Above Pharma. Será un placer colaborar juntos."
- **Botón Wake Word oculto** — CSS `display: none` en `.wake-word-toggle`.
- **Documentación** — Creados `CLAUDE.md` (raíz) y `ABBE/README.md`. Eliminadas credenciales y voice IDs de la documentación.
- **CLAUDE.md** — Agregada convención de versionado y CHANGELOG obligatorio en cada cambio.
- **`.gitignore`** — Configurado en raíz con `user_data.json` excluido.

---

## v3.8.2 — 2026-02-03

### Fix: Browser freeze en respuestas largas

Se resuelve el bug crítico de congelamiento del browser en respuestas largas (FAQ "Extendida")
integrando la librería `streaming-markdown` para renderizado incremental del DOM.

**Problema principal:**
- Al seleccionar un chip de FAQ y elegir "Respuesta Extendida" (1000 tokens), el browser
  se congelaba completamente. No se podía hacer scroll, abrir DevTools ni interactuar.
- El status "Escribiendo..." se quedaba permanente, nunca cambiaba a "En línea".

**Causa raíz:**
El handler de tokens del WebSocket llamaba `renderMarkdown()` en CADA token recibido.
`renderMarkdown()` ejecuta `marked.parse(texto_completo) + DOMPurify.sanitize(html)`,
re-parseando TODO el documento acumulado (complejidad O(n²)). Con 500+ tokens:
Total: 1+2+3+...+500 = 125,250 operaciones de parseo.

**Intentos fallidos:**
1. `requestAnimationFrame` throttle — seguía congelando (O(n²) no cambia con frecuencia)
2. `textContent` durante streaming — sin formato markdown visible
3. `setTimeout` 150ms throttle — mejoró pero seguía congelando en respuestas largas

**Solución: `streaming-markdown`** (3KB gzip)
- Parser con estado que solo procesa el nuevo texto recibido (O(1) por token)
- Usa `appendChild()` — nunca destruye ni reconstruye nodos existentes
- Fallback a `marked.parse()` si CDN no disponible

---

## v3.5.0 — 2026-02-03

### AsyncOpenAI para streaming real

**Problema:** El streaming de tokens desde Groq no era fluido. Los tokens llegaban todos de golpe.

**Causa:** `main.py` usaba `OpenAI` (síncrono) que bloqueaba el event loop de asyncio/FastAPI.

**Solución:** Cambio a `AsyncOpenAI` con `async for chunk in stream:`, permitiendo streaming real.

```
puro_omega (sync):  419 tokens, todos llegan a 3.1s (burst de 0.01s)
novacutan (async):  403 tokens, distribuidos de 0.52s a 1.75s (streaming real de 1.23s)
```

---

## v3.0.0 — 2026-02-02/03

### Creación del proyecto Novacutan

El proyecto se creó duplicando `puro_omega/` y adaptando todo para la marca Novacutan:

| Campo | Puro Omega | Novacutan |
|-------|-----------|-----------|
| Asistente IA | Omia | **Abbe** |
| Wake word | "Hola, Omia" | **"Hola, Abbe"** |
| Puerto | 7860 | **7862** |
| Marca | Puro Omega | **Novacutan** |
| Productos | Omega-3, EPA/DHA | **BioPRO, FBio DVS Light/Medium/Volume** |

---

## Notas técnicas

### Stack tecnológico
- **Backend**: FastAPI + WebSocket + AsyncOpenAI
- **LLM**: Groq API → Llama 3.3-70b-versatile
- **STT**: Groq Whisper v3 (español)
- **TTS**: ElevenLabs v2 (voz Camila MX)
- **Frontend**: Vanilla JS + streaming-markdown + marked.js (fallback) + DOMPurify
- **RAG**: Motor custom BM25 (Okapi) + stemming español + sinónimos dinámicos + metadata boost

### Modelo LLM actual
`llama-3.3-70b-versatile` via Groq.
Para cambiar modelo, editar `LLM_MODEL` en `main.py`.

### Puertos
- Abbe (Above Pharma): 7862
- Puro Omega: 7860
