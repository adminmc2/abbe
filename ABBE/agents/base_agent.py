"""
Clase base para todos los agentes.
Incluye política comparativa evaluada en runtime (no solo prompt).
"""
import re
from typing import List, Tuple, Optional, Dict
from abc import ABC, abstractmethod
from .rag_engine import get_rag_engine
from .catalog import get_empresa, get_product_alias_to_id_map, has_competitors


# ════════════════════════════════════════
# POLÍTICA COMPARATIVA — señales y reglas
# ════════════════════════════════════════

# Señales que indican intención comparativa en la consulta
COMPARATIVE_SIGNALS = [
    r'\bvs\b', r'\bversus\b', r'\bdiferencia\b', r'\bcomparativa\b',
    r'\bcomparar\b', r'\bcomparado\b', r'\bmejor que\b', r'\bpeor que\b',
    r'\botra marca\b', r'\bcompetencia\b', r'\bcompetidor\b',
    r'\bya uso\b', r'\bcambiar de\b', r'\bcambiar a\b',
    r'\bpor qué no usar\b', r'\bpor qué usar\b', r'\bpor qué elegir\b',
    r'\ben vez de\b', r'\balternativa\b',
    r'\bsi ya existen?\b', r'\bya existen?\b',
    r'\bsuperior\b', r'\binferior\b', r'\botra empresa\b',
    r'\botro laboratorio\b', r'\botro proveedor\b',
]

# Señales específicas de competidor de marca (subconjunto más agresivo)
BRAND_COMPETITOR_SIGNALS = [
    r'\botra marca\b', r'\bcompetencia\b', r'\bcompetidor\b',
    r'\botra empresa\b', r'\botro laboratorio\b', r'\botro proveedor\b',
    r'\bya uso otro\b',
]

# Claims de superioridad prohibidos sin soporte documental
SUPERIORITY_CLAIMS = [
    'mejor', 'superior', 'más eficaz', 'más seguro', 'más conveniente',
    'el único', 'el primero', 'sin igual', 'incomparable',
]

# Categorías de KB que pueden contener soporte comparativo válido
COMPARATIVE_CATEGORIES = {
    'objeciones_eficacia', 'objeciones_precio', 'objeciones_seguridad',
    'productos', 'argumentos_venta',
}


class BaseAgent(ABC):
    """Clase base abstracta para agentes especializados"""

    def __init__(self):
        self.rag = get_rag_engine()
        self.name = "BaseAgent"
        self.description = ""
        self.categories = []  # Categorías del RAG que este agente maneja

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Prompt de sistema específico del agente"""
        pass

    def search_knowledge(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """Busca en la base de conocimiento filtrado por las categorías del agente"""
        return self.rag.search(query, top_k=top_k, categories=self.categories if self.categories else None)

    def search_knowledge_with_fallback(self, query: str, top_k: int = 5,
                                       score_threshold: float = 8.0) -> List[Tuple[dict, float]]:
        """Búsqueda dual: primero filtrada por categorías, si no hay buenos resultados busca sin filtro"""

        # 1. Búsqueda filtrada por categorías del agente
        filtered_results = self.rag.search(
            query, top_k=top_k,
            categories=self.categories if self.categories else None
        )

        # 2. Evaluar calidad
        best_score = max((score for _, score in filtered_results), default=0.0)

        if best_score >= score_threshold:
            return filtered_results  # Buenos resultados, usar filtrados

        # 3. Fallback activado — log para métricas
        print(f"[FALLBACK] Query: '{query[:50]}' | Score: {best_score:.2f} | Agent: {self.name}")

        # 4. Búsqueda SIN filtro de categorías
        unfiltered_results = self.rag.search(query, top_k=top_k, categories=None)

        # 5. Combinar: boost 1.1x a resultados de categorías nativas
        combined = {}
        for qa, score in unfiltered_results:
            combined[qa['pregunta']] = (qa, score)

        for qa, score in filtered_results:
            key = qa['pregunta']
            if key in combined:
                combined[key] = (qa, max(score * 1.1, combined[key][1]))
            else:
                combined[key] = (qa, score)

        results = sorted(combined.values(), key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def enrich_context(self, query: str, results: List[Tuple[dict, float]]) -> str:
        """Enriquece el contexto RAG con conocimiento estructurado del agente.
        Override en subclases para aportar inteligencia específica."""
        return ""

    def format_context(self, results: List[Tuple[dict, float]], min_score: float = 3.0) -> str:
        """Formatea los resultados de búsqueda como HECHOS VERIFICADOS numerados para el LLM.
        Scores son raw BM25 — se normalizan localmente solo para display."""
        empresa = get_empresa()
        context_parts = []
        fact_num = 1

        # Normalizar a [0,1] solo para display (confianza relativa al top result)
        max_raw = max((s for _, s in results), default=0.0)

        for qa, score in results:
            if score >= min_score:
                display_score = score / max_raw if max_raw > 0 else 0.0
                source = qa.get('source_doc', 'fuente no especificada')
                context_parts.append(
                    f"HECHO VERIFICADO #{fact_num} (confianza: {display_score:.0%}):\n"
                    f"  Producto/Tema: {qa['pregunta']}\n"
                    f"  Datos confirmados: {qa['respuesta']}\n"
                    f"  Fuente: {source}"
                )
                fact_num += 1

        if not context_parts:
            return "NO HAY DATOS VERIFICADOS para esta consulta. NO inventes ningún dato."

        header = (
            f"═══ DATOS VERIFICADOS DE {empresa.upper()} ═══\n"
            "IMPORTANTE: Solo los datos listados abajo son REALES y VERIFICADOS.\n"
            "Cualquier dato que NO esté aquí abajo es INVENTADO y está PROHIBIDO usarlo.\n\n"
        )
        return header + "\n\n".join(context_parts)

    def evaluate_comparative_query(self, query: str, results: List[Tuple[dict, float]]) -> Dict:
        """Evalúa si la consulta es comparativa y si la comparación está soportada.

        Clasificación:
          - 'internal': compara productos del portafolio Above Pharma entre sí
          - 'therapeutic': compara vs tratamiento convencional/alternativas terapéuticas
          - 'competitor': compara vs marca/laboratorio externo

        La decisión NO depende solo de rag_coverage — mira si los resultados
        RAG contienen soporte comparativo válido (categoría + score mínimo).

        Retorna dict con: is_comparative, type, allowed, reason, has_superiority_claims
        """
        query_lower = query.lower()

        # 1. Detectar si la consulta es comparativa
        is_comparative = any(re.search(signal, query_lower) for signal in COMPARATIVE_SIGNALS)
        if not is_comparative:
            return {"is_comparative": False, "type": None, "allowed": True, "reason": "not_comparative"}

        # 2. Detectar claims de superioridad sin soporte
        has_superiority = any(claim in query_lower for claim in SUPERIORITY_CLAIMS)

        # 3. Clasificar tipo de comparativa
        is_brand = any(re.search(signal, query_lower) for signal in BRAND_COMPETITOR_SIGNALS)

        # Detectar si menciona productos internos del catálogo
        alias_map = get_product_alias_to_id_map()
        mentioned_products = set()
        for alias, pid in alias_map.items():
            if alias in query_lower:
                mentioned_products.add(pid)

        # 4. Determinar tipo y si está permitida
        if is_brand:
            comp_type = "competitor"
            # Solo permitida si el catálogo tiene competidores cargados
            allowed = has_competitors()
            reason = "competitors_loaded" if allowed else "no_competitors_in_catalog"

        elif len(mentioned_products) >= 2:
            comp_type = "internal"
            # Siempre permitida — comparar productos propios del portafolio
            allowed = True
            reason = "internal_portfolio"

        else:
            comp_type = "therapeutic"
            # Permitida solo si hay soporte comparativo en los resultados RAG
            has_support = any(
                qa.get('categoria') in COMPARATIVE_CATEGORIES and score >= 0.15
                for qa, score in results
            )
            allowed = has_support
            reason = "comparative_support_in_kb" if has_support else "no_comparative_support"

        return {
            "is_comparative": True,
            "type": comp_type,
            "allowed": allowed,
            "reason": reason,
            "has_superiority_claims": has_superiority,
        }

    def get_response_prompt(self, query: str, context: str) -> str:
        """Construye el prompt completo con contexto"""
        return f"""{self.system_prompt}

CONTEXTO DE LA BASE DE CONOCIMIENTO:
{context}

---
PREGUNTA DEL USUARIO: {query}

Responde basándote ÚNICAMENTE en el contexto proporcionado."""
