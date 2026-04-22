# ABBE — Asistente IA de Ventas Farmacéuticas

Asistente de inteligencia artificial multi-producto para representantes médicos de **Above Pharma**. ABBE ayuda con información de productos (terapias celulares y medicina regenerativa), manejo de objeciones y argumentos de venta personalizados por especialidad médica.

## Características

- **Sistema multi-agente** con 3 agentes especializados:
  - **Productos** — Información técnica, indicaciones, protocolos (metodología FAB)
  - **Objeciones** — Manejo de objeciones de precio, eficacia, seguridad (Feel-Felt-Found)
  - **Argumentos** — Estrategias de venta por especialidad (SPIN Selling, Challenger Sale)
- **RAG con BM25** (Okapi), stemming español, sinónimos dinámicos y metadata boost por producto
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
cd ABBE
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GROQ_API_KEY` | Sí | API key de Groq (LLM Llama 3.3 + Whisper STT) |
| `ELEVENLABS_API_KEY` | Sí | API key de ElevenLabs (TTS) |
| `ELEVENLABS_VOICE_ID` | No | ID de voz ElevenLabs (ver `.env.example`) |
| `KB_VALIDATION_MODE` | No | `warn` (default) o `strict` (bloquea startup si KB o catálogo inválidos) |

## Uso

```bash
# Desarrollo local
uvicorn main:app --host 0.0.0.0 --port 7862 --reload

# Docker
docker build -t abbe .
docker run -p 7862:7862 --env-file .env abbe
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
ABBE/
├── main.py                  # Backend FastAPI, WebSocket, TTS/STT proxy
├── agents/
│   ├── orchestrator.py      # Router de intenciones (LLM + reglas)
│   ├── base_agent.py        # Clase base con métodos RAG compartidos
│   ├── rag_engine.py        # Motor BM25 + sinónimos + metadata boost + validador
│   ├── catalog.py           # Gestión de catálogo (sinónimos, aliases, keywords)
│   ├── agent_productos.py   # Info técnica de productos Above Pharma
│   ├── agent_objeciones.py  # Manejo de objeciones comerciales
│   └── agent_argumentos.py  # Argumentos de venta por especialidad
├── static/
│   ├── index.html           # SPA (login → welcome → chat)
│   ├── app.js               # Cliente: WebSocket, voz, estado, UI
│   ├── style.css            # Design system con mood-theming
│   └── manifest.json        # Configuración PWA
├── catalog.json             # Catálogo de productos (líneas, aliases, sinónimos)
├── knowledge_base.json      # 50 pares Q&A con contrato de datos validado
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

La base de conocimiento (`knowledge_base.json`) contiene 50 pares pregunta/respuesta con contrato de datos validado al arrancar. Cada Q&A incluye campos obligatorios: `id`, `categoria`, `pregunta`, `respuesta`, `source_doc`, `product_line`, `product`.

### Categorías (lista cerrada, 10):

- `empresa` — Información corporativa de la línea
- `productos` — Información técnica de cada producto
- `tecnologia` — Mecanismos de acción y tecnología diferenciada
- `protocolos` — Protocolos de aplicación y administración
- `seguridad` — Contraindicaciones y seguridad
- `objeciones_precio` — Objeciones de precio
- `objeciones_eficacia` — Objeciones de eficacia
- `objeciones_seguridad` — Objeciones de seguridad
- `argumentos_venta` — Argumentos por especialidad médica
- `perfil_paciente` — Perfiles de paciente candidato

### Productos actuales:
- **Gencell CTM Estabilizador Renal** — CTM pre-tratadas con melatonina (25 Q&As)
- **Gencell CTM Metabólica** — CTM pre-tratadas con evolocumab (25 Q&As)

## Deploy

El proyecto está configurado para **Hugging Face Spaces**:

```bash
docker build -t abbe .
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
| RAG | Custom BM25 (Okapi) + stemming español + sinónimos dinámicos |
| Containerización | Docker (python:3.11-slim) |

---

Desarrollado por **Prisma Consul** para **Above Pharma**.
