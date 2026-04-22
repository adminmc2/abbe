"""
Orquestador - Detecta intención y delega al agente apropiado
"""
import os
import re
from typing import Optional, Tuple
from openai import AsyncOpenAI

from .agent_productos import AgenteProductos
from .agent_objeciones import AgenteObjeciones
from .agent_argumentos import AgenteArgumentos
from .base_agent import BaseAgent


# Modelo LLM
LLM_MODEL = "moonshotai/kimi-k2-instruct"

# Cliente LLM lazy (se inicializa cuando se usa)
_llm_client = None

def get_llm_client():
    """Obtiene el cliente LLM (lazy initialization) — Kimi K2 via Groq"""
    global _llm_client
    if _llm_client is None:
        _llm_client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    return _llm_client


class Orchestrator:
    """
    Orquestador del sistema multi-agente.

    Analiza la intención del usuario y delega al agente especializado.
    """

    AGENT_MAP = {
        "productos": AgenteProductos,
        "objeciones": AgenteObjeciones,
        "argumentos": AgenteArgumentos
    }

    CLASSIFICATION_PROMPT = """Eres un clasificador de intenciones para un asistente de ventas farmacéutico de Above Pharma.

Analiza el mensaje del usuario y clasifícalo en UNA de estas categorías:

1. **productos** - Preguntas sobre:
   - Información técnica de productos (composición, presentación, tecnología)
   - Indicaciones y zonas de tratamiento
   - Protocolos de aplicación
   - Certificaciones, tecnología diferenciada
   - Qué producto recomendar para X zona o condición
   - Diferencias entre productos de la marca
   - Seguridad, contraindicaciones, complicaciones, cuidados post

2. **objeciones** - Cuando el usuario menciona:
   - Objeciones de PRECIO ("es caro", "muy costoso")
   - Objeciones de EFICACIA ("no funciona", "no hay resultados", "no dura")
   - Objeciones de MARCA ("no conozco", "ya uso otra marca", "por qué cambiar")
   - Comparativas negativas ("prefiero otra marca", "X es mejor")
   - Cualquier duda o rechazo que necesite ser rebatido

3. **argumentos** - Preguntas sobre:
   - Cómo vender a un especialista (dermatólogo, cirujano plástico, médico estético)
   - Argumentos de venta por especialidad
   - Perfiles de paciente ideal
   - Cómo presentar el producto
   - Estrategias de venta, pitch
   - Diferenciación frente a competencia (desde perspectiva de venta)

REGLAS:
- Si hay duda entre categorías, prioriza: objeciones > argumentos > productos
- Los saludos o preguntas generales van a "productos"
- Las comparativas van a "objeciones" si son negativas, a "argumentos" si buscan diferenciación

Responde SOLO con una palabra: productos, objeciones o argumentos"""

    def __init__(self):
        self.agents = {
            name: agent_class()
            for name, agent_class in self.AGENT_MAP.items()
        }
        self.default_agent = "productos"

    async def classify_intent(self, message: str) -> str:
        """
        Clasifica la intención del usuario usando el LLM.

        Returns:
            str: 'productos', 'objeciones' o 'argumentos'
        """
        try:
            response = await get_llm_client().chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.CLASSIFICATION_PROMPT},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=20
            )

            intent = response.choices[0].message.content.strip().lower()

            # Validar que sea una categoría válida
            if intent in self.AGENT_MAP:
                return intent

            # Intentar extraer la categoría del texto
            for category in self.AGENT_MAP.keys():
                if category in intent:
                    return category

            return self.default_agent

        except Exception as e:
            print(f"Error en clasificación: {e}")
            return self.default_agent

    # ── Patrones de objeción DIRECTA ──
    # Rechazo/resistencia explícita sin ambigüedad — siempre objeciones
    OBJECTION_DIRECT = [
        # Rechazo de eficacia
        r'\bno funciona\b', r'\bno sirve\b', r'\bno veo resultado',
        # Precio (con género: caro/cara, costoso/costosa)
        r'\bes car[oa]\b', r'\bmuy car[oa]\b', r'\bcostos[oa]\b',
        r'\bprecio\b.*\b(?:alto|elevado|car[oa])\b',
        # Marca / competencia
        r'\bya uso otra\b', r'\bpor qu[eé] cambiar\b',
        r'\bcompetencia\b', r'\botra marca\b',
        r'\bprefiere? (?:otra|otro|gen[eé]rico)',
        # Resistencia explícita
        r'\bobje[cs]i[oó]n',
        r'\bno (?:le |me )?convence\b',
        r'\bno (?:le |me )?(?:gusta|interesa|convence)',
    ]

    # ── Frame comercial ──
    # Señales de que el rep maneja una situación de resistencia/duda con el médico.
    # Solo verbos que implican resistencia real, NO verbos neutros (pregunta, dice).
    # "El médico pregunta la composición" es consulta técnica → productos.
    # "El médico duda de la eficacia" es resistencia → objeciones.
    COMMERCIAL_FRAME = [
        # Doctor + verbo de resistencia (NO pregunta/dice — son neutros)
        r'\bel (?:m[eé]dico|doctor) (?:me |le )?(?:duda|cuestiona|objeta|preocupa|no cree)',
        # Doctor + dice/dijo solo cuando va seguido de resistencia explícita
        r'\bel (?:m[eé]dico|doctor) (?:me |le )?(?:dice|dijo) que (?:no |es (?:muy )?car|le preocupa|duda|no (?:le |me )?convence)',
        # Solicitud de respuesta/manejo (frame inequívoco de objeción)
        r'\bc[oó]mo (?:le )?respondo\b',
        r'\bqu[eé] le digo\b',
        r'\bc[oó]mo (?:le )?(?:manejo|contesto|rebato)\b',
        # Situación hipotética de venta
        r'\bsi (?:me |el (?:m[eé]dico|doctor) )?dice que\b',
    ]

    # ── Patrones de argumentos ──
    # Contexto de venta, visita o especialidad
    ARGUMENT_PATTERNS = [
        r'\bc[oó]mo vend', r'\bc[oó]mo present', r'\bargumento',
        r'\bestrategi.* vent', r'\bperfil.* paciente',
        r'\bdiferencia.* competencia', r'\bventaja', r'\bpitch\b',
        # Especialidades con o sin contexto de venta
        r'\bdermat[oó]logo\b', r'\bcirujano\b', r'\bpl[aá]stico\b',
        r'\best[eé]tico\b', r'\best[eé]tica\b',
        r'\bginec[oó]logo\b', r'\binternista\b', r'\bnefr[oó]logo\b', r'\bneum[oó]logo\b',
        r'\bcardi[oó]logo\b', r'\bendocrin[oó]logo\b',
        r'\bespecialista\b', r'\bespecialidad\b',
    ]

    def classify_intent_rules(self, message: str) -> str:
        """
        Clasificación contextual por frame, no por vocabulario.

        Jerarquía:
          1. Objeción directa: rechazo/resistencia explícita → objeciones
          2. Frame comercial: doctor + duda/preocupación, solicitud de respuesta → objeciones
          3. Contexto de venta/especialidad → argumentos
          4. Default → productos (ficha técnica, info clínica, dudas generales)

        Términos como contraindicaciones, efectos secundarios, interacciones
        van a productos (consulta técnica) a menos que tengan frame comercial.
        """
        message_lower = message.lower()

        # Fase 1: ¿Hay rechazo/resistencia directa e inequívoca?
        for pattern in self.OBJECTION_DIRECT:
            if re.search(pattern, message_lower):
                return "objeciones"

        # Fase 2: ¿Hay frame comercial (manejo de situación con médico)?
        for pattern in self.COMMERCIAL_FRAME:
            if re.search(pattern, message_lower):
                return "objeciones"

        # Fase 3: ¿Hay contexto de venta/especialidad?
        for pattern in self.ARGUMENT_PATTERNS:
            if re.search(pattern, message_lower):
                return "argumentos"

        # Default: productos (incluye seguridad técnica neutra, ficha, protocolos)
        return "productos"

    def get_agent(self, agent_name: str) -> BaseAgent:
        """Obtiene una instancia del agente especificado."""
        return self.agents.get(agent_name, self.agents[self.default_agent])

    async def process_message(
        self,
        message: str,
        history: list = None,
        use_llm_classification: bool = True
    ) -> Tuple[str, BaseAgent, str]:
        """
        Procesa un mensaje y devuelve la respuesta del agente apropiado.

        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            use_llm_classification: Si usar LLM para clasificar (más preciso pero más lento)

        Returns:
            Tuple[intent, agent, context]: Intención detectada, agente usado y contexto RAG
        """
        # Clasificar intención
        if use_llm_classification:
            intent = await self.classify_intent(message)
        else:
            intent = self.classify_intent_rules(message)

        # Obtener agente
        agent = self.get_agent(intent)

        # Buscar contexto relevante
        results = agent.search_knowledge(message, top_k=5)
        context = agent.format_context(results, min_score=0.1)

        return intent, agent, context

    async def get_response(
        self,
        message: str,
        history: list = None
    ):
        """
        Obtiene respuesta con streaming del sistema.

        Args:
            message: Mensaje del usuario
            history: Historial de conversación

        Yields:
            Tuple[token, intent, agent_name]
        """
        intent, agent, context = await self.process_message(message, history)

        # Construir prompt con contexto
        system_prompt = f"""{agent.system_prompt}

INFORMACIÓN DE CONTEXTO (Base de conocimiento):
{context}

---
Responde basándote en el contexto anterior. Si no tienes información específica, indícalo."""

        # Construir mensajes
        messages = [{"role": "system", "content": system_prompt}]

        # Añadir historial
        if history:
            for h in history[-6:]:  # Últimos 6 mensajes
                messages.append(h)

        messages.append({"role": "user", "content": message})

        # Generar respuesta con streaming
        response = await get_llm_client().chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=1000
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content, intent, agent.name

    async def get_response_sync(
        self,
        message: str,
        history: list = None
    ) -> Tuple[str, str, str]:
        """
        Obtiene respuesta completa (sin streaming).

        Args:
            message: Mensaje del usuario
            history: Historial de conversación

        Returns:
            Tuple[response, intent, agent_name]
        """
        intent, agent, context = await self.process_message(message, history)

        # Construir prompt con contexto
        system_prompt = f"""{agent.system_prompt}

INFORMACIÓN DE CONTEXTO (Base de conocimiento):
{context}

---
Responde basándote en el contexto anterior. Si no tienes información específica, indícalo."""

        # Construir mensajes
        messages = [{"role": "system", "content": system_prompt}]

        # Añadir historial
        if history:
            for h in history[-6:]:
                messages.append(h)

        messages.append({"role": "user", "content": message})

        response = await get_llm_client().chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=False,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content, intent, agent.name


# Singleton del orquestador
_orchestrator_instance = None

def get_orchestrator() -> Orchestrator:
    """Obtiene la instancia singleton del orquestador."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
