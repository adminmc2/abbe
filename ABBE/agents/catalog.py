"""
Carga y gestión del catálogo de productos Above Pharma.
Singleton — se carga una vez y se reutiliza en agentes y RAG.
"""
import json
import os
from typing import Dict, List, Optional

_catalog: Optional[dict] = None


def get_catalog() -> dict:
    """Obtiene el catálogo de productos (lazy singleton)."""
    global _catalog
    if _catalog is None:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'catalog.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                _catalog = json.load(f)
        else:
            _catalog = {"metadata": {"empresa": "Above Pharma"}, "product_lines": []}
    return _catalog


def reload_catalog():
    """Fuerza recarga del catálogo (útil tras agregar productos)."""
    global _catalog
    _catalog = None
    return get_catalog()


def get_empresa() -> str:
    """Nombre de la empresa."""
    return get_catalog().get('metadata', {}).get('empresa', 'Above Pharma')


def get_all_products() -> List[dict]:
    """Lista plana de todos los productos de todas las líneas."""
    products = []
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            products.append({**product, 'product_line': line['id'], 'line_name': line['name']})
    return products


def get_product_synonyms() -> Dict[str, List[str]]:
    """Genera diccionario de sinónimos desde el catálogo para el RAG."""
    synonyms = {}
    for line in get_catalog().get('product_lines', []):
        # Sinónimos de la línea
        for k, v in line.get('synonyms', {}).items():
            synonyms[k.lower()] = [s.lower() for s in v]
        # Sinónimos de productos (aliases)
        for product in line.get('products', []):
            name_lower = product['name'].lower()
            aliases = [a.lower() for a in product.get('aliases', [])]
            if aliases:
                synonyms[name_lower] = aliases
                for alias in aliases:
                    synonyms[alias] = [name_lower]
    return synonyms


def get_product_aliases() -> Dict[str, str]:
    """Genera mapa alias → nombre canónico para normalización."""
    aliases = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            canonical = product['name'].lower()
            for alias in product.get('aliases', []):
                aliases[alias.lower()] = canonical
    return aliases


def get_condition_product_map() -> Dict[str, List[str]]:
    """Genera mapa condición → productos recomendados desde el catálogo."""
    condition_map = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            for condition in product.get('conditions', []):
                cond_lower = condition.lower()
                if cond_lower not in condition_map:
                    condition_map[cond_lower] = []
                condition_map[cond_lower].append(product['name'])
    return condition_map


def get_portfolio_description() -> str:
    """Genera descripción del portafolio para inyectar en prompts de agentes."""
    lines = get_catalog().get('product_lines', [])
    if not lines:
        return "Portafolio pendiente de configuración. Responde con los datos del contexto RAG disponible."

    parts = []
    for line in lines:
        products = [p['name'] for p in line.get('products', [])]
        desc = line.get('description', '')
        if products:
            parts.append(f"**{line['name']}** ({desc}): {', '.join(products)}")
        else:
            parts.append(f"**{line['name']}**: {desc}")
    return '\n'.join(parts)


def get_product_keywords() -> List[str]:
    """Lista de keywords de producto para detección de intención."""
    keywords = []
    for line in get_catalog().get('product_lines', []):
        keywords.append(line['name'].lower())
        for tech in line.get('technologies', []):
            keywords.append(tech.lower())
        for product in line.get('products', []):
            keywords.append(product['name'].lower())
            keywords.extend([a.lower() for a in product.get('aliases', [])])
        keywords.extend([c.lower() for c in line.get('competitors', [])])
    return list(set(keywords))
