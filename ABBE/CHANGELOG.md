# CHANGELOG - Above Pharma (Abbe)

Historial completo de desarrollo, problemas encontrados y soluciones aplicadas.

---

## v3.8.4 — 2026-04-21 (ACTUAL)

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
- **LLM**: Groq API (Kimi K2 o Llama 3.3 como respaldo)
- **STT**: Groq Whisper
- **TTS**: ElevenLabs (voz Camila MX)
- **Frontend**: Vanilla JS + streaming-markdown + marked.js (fallback) + DOMPurify
- **RAG**: Motor custom con stemming español, sinónimos, búsqueda híbrida (keyword + embedding)

### Modelo LLM actual
`moonshotai/kimi-k2-instruct` via Groq (fallback: `llama-3.3-70b-versatile`).
Para cambiar modelo, editar `LLM_MODEL` en `agents/orchestrator.py`.

### Puertos
- Abbe (Novacutan): 7862
- Puro Omega: 7860
