# CLAUDE.md — ABBE (Above Pharma / Novacutan)

## Qué es este proyecto

ABBE es un asistente de ventas IA para representantes médicos de Novacutan (marca de Above Pharma). Es una aplicación web con backend FastAPI y frontend vanilla JS, desplegada en Hugging Face Spaces via Docker.

El asistente ayuda a los representantes con información de productos (biomoduladores y rellenos dérmicos), manejo de objeciones y argumentos de venta por especialidad médica.

## Estructura del proyecto

```
above pharma/
├── NOVIA/                          # Aplicación principal
│   ├── main.py                     # Backend FastAPI (entry point)
│   ├── agents/                     # Sistema multi-agente
│   │   ├── orchestrator.py         # Router de intenciones (clasifica → agente)
│   │   ├── base_agent.py           # Clase base con métodos RAG
│   │   ├── rag_engine.py           # Motor de búsqueda híbrido (TF-IDF + keywords)
│   │   ├── agent_productos.py      # Agente Científico (FAB methodology)
│   │   ├── agent_objeciones.py     # Agente Diplomático (Feel-Felt-Found)
│   │   └── agent_argumentos.py     # Agente Estratega (SPIN/Challenger Sale)
│   ├── static/                     # Frontend
│   │   ├── index.html              # SPA con 3 pantallas (login/welcome/chat)
│   │   ├── app.js                  # Lógica cliente (~3100 líneas)
│   │   ├── style.css               # Estilos (~2500 líneas)
│   │   └── manifest.json           # PWA config
│   ├── knowledge_base.json         # Base de conocimiento RAG (~170 Q&As)
│   ├── user_data.json              # Historial de usuarios
│   ├── requirements.txt            # Dependencias Python
│   ├── Dockerfile                  # Deploy HF Spaces (puerto 7862)
│   ├── .env                        # Variables de entorno (NO commitear)
│   └── CHANGELOG.md                # Historial de desarrollo
├── NOVIA.md                        # Documentación de producto y pricing
├── presentacion-above-pharma.md    # Presentación comercial
└── presentacion-above-pharma-general.md
```

## Stack tecnológico

- **Backend:** Python 3.11+, FastAPI, Uvicorn, AsyncOpenAI
- **LLM:** Groq API → Llama 3.3-70b-versatile (fallback: Kimi K2)
- **STT:** Groq Whisper v3 (español)
- **TTS:** ElevenLabs v2 (voz Camila MX)
- **Frontend:** Vanilla JS, streaming-markdown, marked.js (fallback), Phosphor Icons
- **RAG:** Motor custom con stemming español, sinónimos, TF-IDF + keywords
- **Deploy:** Docker → Hugging Face Spaces (puerto 7862)

## Cómo correr el proyecto

```bash
cd NOVIA
pip install -r requirements.txt
cp .env.example .env  # Configurar API keys
uvicorn main:app --host 0.0.0.0 --port 7862 --reload
```

## Variables de entorno requeridas

```
GROQ_API_KEY=           # LLM (Llama 3.3) + Whisper STT
ELEVENLABS_API_KEY=     # Text-to-speech
ELEVENLABS_VOICE_ID=    # ID de voz mexicana (ver .env.example)
```

## Arquitectura: Flujo de una consulta

```
Usuario → WebSocket /ws/chat
  → Orchestrator (clasifica intención con LLM + reglas)
    → Agente seleccionado (productos/objeciones/argumentos)
      → RAG Engine (busca contexto en knowledge_base.json)
        → LLM (genera respuesta con streaming)
          → WebSocket → Cliente (renderiza con streaming-markdown)
```

## Convenciones de código

- **Idioma del código:** Nombres de variables y funciones en inglés, comentarios y prompts en español
- **Agentes:** Cada agente tiene un system prompt extenso con metodología de ventas específica
- **Knowledge base:** JSON plano con pares pregunta/respuesta categorizados
- **Frontend:** SPA sin framework, estado global en objeto `state`, comunicación via WebSocket
- **Streaming:** Usar `streaming-markdown` para renderizado incremental (NO `marked.parse()` en cada token — causa O(n²), ver CHANGELOG v5.7.0)

## Credenciales de prueba

- Configuradas en `app.js`. No incluir en documentación pública.

## Puertos

- ABBE (Novacutan): `7862`
- Puro Omega (proyecto hermano): `7860`

## Notas importantes

- El proyecto se originó como fork de `puro_omega/` adaptado para Novacutan
- La knowledge base se extrajo de `GUIA_OPERATIVA_CHATBOT_NOVACUTAN.md`
- No hay tests automatizados; verificación manual via `/api/health` y DevTools
- El modelo LLM es configurable en `main.py` variable `LLM_MODEL`
