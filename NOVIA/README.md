# NOVIA — Asistente IA de Ventas Farmacéuticas

Asistente de inteligencia artificial diseñado para representantes médicos de **Novacutan** (Above Pharma). NOVIA ayuda con información de productos, manejo de objeciones y argumentos de venta personalizados por especialidad médica.

## Características

- **Sistema multi-agente** con 3 agentes especializados:
  - **Productos** — Información técnica, indicaciones, protocolos (metodología FAB)
  - **Objeciones** — Manejo de objeciones de precio, eficacia, seguridad (Feel-Felt-Found)
  - **Argumentos** — Estrategias de venta por especialidad (SPIN Selling, Challenger Sale)
- **RAG híbrido** con stemming español, sinónimos y búsqueda TF-IDF + keywords
- **Streaming en tiempo real** via WebSocket con renderizado incremental
- **Voz bidireccional** — STT (Whisper) + TTS (ElevenLabs, voz mexicana)
- **PWA** — Instalable como app móvil
- **Infografías** — Generación on-demand de resúmenes visuales
- **Sistema de mood** — Personalización visual según estado de ánimo

## Requisitos previos

- Python 3.11+
- Cuenta en [Groq](https://console.groq.com/) (API key para LLM + STT)
- Cuenta en [ElevenLabs](https://elevenlabs.io/) (API key para TTS)

## Instalación

```bash
# Clonar e instalar dependencias
cd NOVIA
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GROQ_API_KEY` | Si | API key de Groq (LLM Llama 3.3 + Whisper STT) |
| `ELEVENLABS_API_KEY` | Si | API key de ElevenLabs (TTS) |
| `ELEVENLABS_VOICE_ID` | No | ID de voz ElevenLabs (ver `.env.example`) |

## Uso

```bash
# Desarrollo local
uvicorn main:app --host 0.0.0.0 --port 7862 --reload

# Docker
docker build -t novia .
docker run -p 7862:7862 --env-file .env novia
```

Abrir `http://localhost:7862` en el navegador.

**Credenciales de prueba:** Ver `.env` o consultar al equipo

## Arquitectura

```
┌─────────────┐     WebSocket      ┌──────────────┐
│   Frontend   │ ◄───────────────► │   FastAPI     │
│  (SPA + PWA) │                   │   main.py     │
└─────────────┘                   └──────┬───────┘
                                         │
                                  ┌──────▼───────┐
                                  │ Orchestrator  │ ← Clasifica intención
                                  └──────┬───────┘
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                   ┌────────────┐ ┌────────────┐ ┌────────────┐
                   │ Productos  │ │ Objeciones │ │ Argumentos │
                   │ (Scientist)│ │ (Diplomat) │ │ (Strategist│
                   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                         └──────────────┼──────────────┘
                                  ┌─────▼──────┐
                                  │ RAG Engine │ ← Búsqueda híbrida
                                  └─────┬──────┘
                                  ┌─────▼──────┐
                                  │  Groq LLM  │ ← Streaming response
                                  └────────────┘
```

## Estructura de archivos

```
NOVIA/
├── main.py                  # Backend FastAPI, WebSocket, TTS/STT proxy
├── agents/
│   ├── orchestrator.py      # Router de intenciones (LLM + reglas)
│   ├── base_agent.py        # Clase base con métodos RAG compartidos
│   ├── rag_engine.py        # Motor de búsqueda (TF-IDF + keywords + sinónimos)
│   ├── agent_productos.py   # Info técnica de productos Novacutan
│   ├── agent_objeciones.py  # Manejo de objeciones comerciales
│   └── agent_argumentos.py  # Argumentos de venta por especialidad
├── static/
│   ├── index.html           # SPA (login → welcome → chat)
│   ├── app.js               # Cliente: WebSocket, voz, estado, UI
│   ├── style.css            # Design system con mood-theming
│   └── manifest.json        # Configuración PWA
├── knowledge_base.json      # ~170 pares Q&A categorizados
├── user_data.json           # Persistencia de historial por usuario
├── requirements.txt         # Dependencias Python
├── Dockerfile               # Deploy para Hugging Face Spaces
├── .env.example             # Template de variables de entorno
└── CHANGELOG.md             # Historial de desarrollo
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Sirve la SPA (index.html) |
| `GET` | `/api/health` | Health check |
| `WS` | `/ws/chat` | Chat bidireccional (texto + voz) |
| `POST` | `/api/history/save` | Guardar historial de búsquedas |
| `POST` | `/api/history/load` | Cargar historial de búsquedas |
| `GET` | `/api/test-infographic` | Test de generación de infografías |

## Knowledge Base

La base de conocimiento (`knowledge_base.json`) contiene ~170 pares pregunta/respuesta organizados en categorías:

- `empresa_marca` — Información de Novacutan y Above Pharma
- `tecnologia_dvs` — Tecnología DVS (Dynamic Volumetric Stabilization)
- `productos_biopro` — BioPRO (biomodulador)
- `productos_fbio_dvs` — FBio DVS Light/Medium/Volume (fillers)
- `protocolos_aplicacion` — Técnicas de aplicación y protocolos
- `comparativas_competencia` — Comparativas con Juvederm, Restylane, etc.
- `objeciones` — Objeciones frecuentes y respuestas
- `argumentos_venta` — Argumentos por especialidad médica
- `seguridad_contraindicaciones` — Seguridad y contraindicaciones
- `complicaciones` — Manejo de complicaciones
- `cuidados_post` — Cuidados post-procedimiento
- `zonas_tecnicas` — Zonas anatómicas de aplicación

## Deploy

El proyecto está configurado para **Hugging Face Spaces**:

```bash
docker build -t novia .
# Se ejecuta en puerto 7862 con usuario non-root (requisito HF Spaces)
```

## Stack tecnológico

| Componente | Tecnología |
|------------|-----------|
| Backend | FastAPI + Uvicorn |
| LLM | Groq API (Llama 3.3-70b-versatile) |
| STT | Groq Whisper v3 (español) |
| TTS | ElevenLabs v2 (voz Camila MX) |
| Frontend | Vanilla JS + streaming-markdown |
| RAG | Custom (TF-IDF + keywords + stemming español) |
| Containerización | Docker (python:3.11-slim) |

---

Desarrollado por **Prisma Consul** para **Above Pharma**.
