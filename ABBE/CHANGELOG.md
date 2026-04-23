# CHANGELOG - Above Pharma (Abbe)

Historial completo de desarrollo, problemas encontrados y soluciones aplicadas.

---

## v4.9.3 — 2026-04-23 (ACTUAL)

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
