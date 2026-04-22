# CHANGELOG - Above Pharma (Abbe)

Historial completo de desarrollo, problemas encontrados y soluciones aplicadas.

---

## v4.0.3 — 2026-04-22 (ACTUAL)

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
