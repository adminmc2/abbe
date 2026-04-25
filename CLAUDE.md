# CLAUDE.md — ABBE (Above Pharma)

## Qué es este proyecto

ABBE es un asistente de ventas IA multi-producto para representantes médicos de Above Pharma. Es una aplicación web con backend FastAPI y frontend vanilla JS, desplegada en Hugging Face Spaces via Docker.

El asistente ayuda a los representantes con información de productos (terapias celulares y medicina regenerativa), manejo de objeciones y argumentos de venta por especialidad médica. Actualmente opera con la línea Gencell Biotechnology (CTM Estabilizador Renal y CTM Metabólica).

## Estructura del proyecto

```
above pharma/
├── ABBE/                           # Aplicación principal
│   ├── main.py                     # Backend FastAPI (entry point)
│   ├── agents/                     # Sistema multi-agente
│   │   ├── orchestrator.py         # Router de intenciones (clasifica → agente)
│   │   ├── base_agent.py           # Clase base con métodos RAG
│   │   ├── rag_engine.py           # Motor BM25 + sinónimos + metadata boost
│   │   ├── catalog.py              # Gestión de catálogo (sinónimos, aliases, keywords)
│   │   ├── agent_productos.py      # Agente Científico (FAB methodology)
│   │   ├── agent_objeciones.py     # Agente Diplomático (Feel-Felt-Found)
│   │   └── agent_argumentos.py     # Agente Estratega (SPIN/Challenger Sale)
│   ├── static/                     # Frontend
│   │   ├── index.html              # SPA con 3 pantallas (login/welcome/chat)
│   │   ├── app.js                  # Lógica cliente (~3100 líneas)
│   │   ├── style.css               # Estilos (~2500 líneas)
│   │   └── manifest.json           # PWA config
│   ├── catalog.json                # Catálogo de productos (líneas, aliases, sinónimos)
│   ├── knowledge_base.json         # Base de conocimiento RAG (50 Q&As, 2 productos)
│   ├── user_data.json              # Historial de usuarios
│   ├── requirements.txt            # Dependencias Python
│   ├── Dockerfile                  # Deploy HF Spaces (puerto 7860)
│   ├── .env                        # Variables de entorno (NO commitear)
│   └── CHANGELOG.md                # Historial de desarrollo
├── ABBE.md                         # Documentación de producto y pricing
├── presentacion-above-pharma.md    # Presentación comercial
└── presentacion-above-pharma-general.md
```

## Stack tecnológico

- **Backend:** Python 3.11+, FastAPI, Uvicorn, AsyncOpenAI
- **LLM:** Groq API → Llama 3.3-70b-versatile
- **STT:** Groq Whisper v3 (español)
- **TTS:** ElevenLabs v2 (voz Camila MX)
- **Frontend:** Vanilla JS, streaming-markdown, marked.js (fallback), Phosphor Icons
- **RAG:** Motor custom BM25 (Okapi) + stemming español + sinónimos dinámicos + metadata boost
- **Catálogo:** `catalog.json` con líneas de producto, aliases, sinónimos y keywords
- **Deploy:** Docker → Hugging Face Spaces (puerto 7860, Space `mandocc2/abbe`)

## Cómo correr el proyecto

```bash
cd ABBE
pip install -r requirements.txt
cp .env.example .env  # Configurar API keys
uvicorn main:app --host 0.0.0.0 --port 7862 --reload
```

## Variables de entorno requeridas

```
GROQ_API_KEY=           # LLM (Llama 3.3) + Whisper STT
ELEVENLABS_API_KEY=     # Text-to-speech
ELEVENLABS_VOICE_ID=    # ID de voz mexicana (ver .env.example)
KB_VALIDATION_MODE=     # 'warn' (default) o 'strict' (bloquea startup si KB o catálogo inválidos)
```

## Arquitectura: Flujo de una consulta

```
Usuario → WebSocket /ws/chat
  → Orchestrator (clasifica intención con LLM + reglas)
    → Agente seleccionado (productos/objeciones/argumentos)
      → RAG Engine (busca contexto en knowledge_base.json)
        → Política comparativa (evalúa tipo + soporte en KB)
          → LLM (genera respuesta con streaming + instrucciones comparativas)
            → audit_traces.jsonl (traza persistente)
              → WebSocket → Cliente (renderiza con streaming-markdown)
```

## Convenciones de código

- **Idioma del código:** Nombres de variables y funciones en inglés, comentarios y prompts en español
- **Agentes:** Cada agente tiene un system prompt extenso con metodología de ventas específica
- **Knowledge base:** JSON con pares pregunta/respuesta, contrato de datos obligatorio (id, categoria, pregunta, respuesta, source_doc, product_line, product). Validado al arrancar.
- **Política comparativa:** Evaluada en runtime por `evaluate_comparative_query()` en `base_agent.py`. Clasifica consultas en `internal`/`therapeutic`/`competitor` y decide si está soportada por la KB. Comparativas de competidor solo permitidas si `catalog.json` tiene competidores cargados (`has_competitors()`). Claims de superioridad requieren soporte documental explícito.
- **Frontend:** SPA sin framework, estado global en objeto `state`, comunicación via WebSocket
- **Streaming:** Usar `streaming-markdown` para renderizado incremental (NO `marked.parse()` en cada token — causa O(n²), ver CHANGELOG v3.8.2)

## Credenciales de prueba

- Configuradas en `app.js`. No incluir en documentación pública.

## Puertos

- ABBE local: `7862`
- ABBE HF Spaces (Docker): `7860`
- Puro Omega (proyecto hermano): `7860`

## Deploy

- **HF Space:** `mandocc2/abbe` (Protected, Docker)
- **URL directa:** `https://mandocc2-abbe.hf.space`
- **Dominio custom:** `https://abbe.prismaconsul.com` (Cloudflare proxy → HF Space)
- **Keepalive:** cron-job.org ping cada 30 min a `/api/health`
- **Push al Space:** clonar `https://huggingface.co/spaces/mandocc2/abbe`, copiar contenido de `ABBE/`, push

## Versionado y CHANGELOG

- **Cualquier cambio en el código implica una nueva versión.** Actualizar `ABBE/CHANGELOG.md` inmediatamente al hacer el cambio en local, NO esperar al commit.
- Solo hacer commit y push cuando el usuario lo pida explícitamente.
- Usar versionado semántico: `MAJOR.MINOR.PATCH` (ej: v3.8.3 → v3.8.4 para fix, v3.9.0 para feature)
- Marcar la versión actual con `(ACTUAL)` y quitar esa etiqueta de la anterior
- Incluir fecha en formato `YYYY-MM-DD`
- Describir brevemente qué cambió y por qué

## Notas importantes

- El proyecto se originó como fork de `puro_omega/`, adaptado primero para Novacutan y luego transformado en plataforma multi-producto Above Pharma (v4.0+)
- La knowledge base actual se extrajo de las fichas técnicas PDF de cada producto
- Los validadores de KB y catálogo se ejecutan al arrancar y verifican contrato de datos, categorías, IDs únicos y referencias cruzadas
- No hay tests automatizados; verificación manual via `/api/health` y DevTools
- El modelo LLM es configurable en `main.py` variable `LLM_MODEL`
