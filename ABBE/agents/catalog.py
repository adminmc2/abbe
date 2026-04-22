"""
Carga, validación y gestión del catálogo de productos Above Pharma.
Singleton — se carga una vez y se reutiliza en agentes y RAG.
"""
import json
import os
from typing import Dict, List, Optional, Tuple

_catalog: Optional[dict] = None

# Campos obligatorios por nivel (contrato de datos del catálogo)
REQUIRED_LINE_FIELDS = {'id', 'name', 'manufacturer', 'description', 'category', 'technologies', 'products', 'synonyms'}
REQUIRED_PRODUCT_FIELDS = {'id', 'name', 'type', 'pretreatment', 'pretreatment_mechanism', 'aliases', 'conditions', 'zones'}
LIST_FIELDS_LINE = {'technologies', 'products'}
LIST_FIELDS_PRODUCT = {'aliases', 'conditions', 'zones'}


def _validate_catalog(catalog: dict):
    """Valida contrato de datos del catálogo: campos obligatorios, IDs únicos, tipos correctos.

    Modo controlado por KB_VALIDATION_MODE:
      - 'warn' (default): reporta errores sin detener el arranque
      - 'strict': lanza ValueError si hay errores
    """
    errors = []
    line_ids = set()
    product_ids = set()
    all_aliases = {}  # alias → product_id (para detectar colisiones)

    lines = catalog.get('product_lines', [])
    if not lines:
        errors.append("catalog: no product_lines found")

    for line in lines:
        lid = line.get('id', '?')

        # Campos obligatorios de línea
        missing = REQUIRED_LINE_FIELDS - set(line.keys())
        if missing:
            errors.append(f"line '{lid}': missing fields {missing}")

        # ID único de línea
        if lid in line_ids:
            errors.append(f"line '{lid}': duplicate line ID")
        line_ids.add(lid)

        # Tipos correctos en línea
        for field in LIST_FIELDS_LINE:
            val = line.get(field)
            if val is not None and not isinstance(val, list):
                errors.append(f"line '{lid}': '{field}' must be a list, got {type(val).__name__}")

        # synonyms debe ser dict
        syns = line.get('synonyms')
        if syns is not None and not isinstance(syns, dict):
            errors.append(f"line '{lid}': 'synonyms' must be a dict, got {type(syns).__name__}")

        # Validar productos
        for product in line.get('products', []):
            pid = product.get('id', '?')

            # Campos obligatorios de producto
            pmissing = REQUIRED_PRODUCT_FIELDS - set(product.keys())
            if pmissing:
                errors.append(f"product '{pid}' in line '{lid}': missing fields {pmissing}")

            # ID único de producto (global)
            if pid in product_ids:
                errors.append(f"product '{pid}': duplicate product ID")
            product_ids.add(pid)

            # Tipos correctos en producto
            for field in LIST_FIELDS_PRODUCT:
                val = product.get(field)
                if val is not None and not isinstance(val, list):
                    errors.append(f"product '{pid}': '{field}' must be a list, got {type(val).__name__}")

            # Colisión de aliases entre productos
            for alias in product.get('aliases', []):
                alias_lower = alias.lower()
                if alias_lower in all_aliases and all_aliases[alias_lower] != pid:
                    errors.append(f"product '{pid}': alias '{alias}' collides with product '{all_aliases[alias_lower]}'")
                all_aliases[alias_lower] = pid

    if errors:
        mode = os.environ.get('KB_VALIDATION_MODE', 'warn')
        print(f"[Catalog] ⚠ Validation: {len(errors)} errors:")
        for e in errors:
            print(f"  {e}")
        if mode == 'strict':
            raise ValueError(f"Catalog validation failed ({len(errors)} errors). Fix data or set KB_VALIDATION_MODE=warn")
    else:
        total_products = sum(len(line.get('products', [])) for line in lines)
        print(f"[Catalog] ✓ Validation passed ({len(lines)} lines, {total_products} products)")


def get_catalog() -> dict:
    """Obtiene el catálogo de productos (lazy singleton). Valida al cargar."""
    global _catalog
    if _catalog is None:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'catalog.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                _catalog = json.load(f)
            _validate_catalog(_catalog)
        else:
            mode = os.environ.get('KB_VALIDATION_MODE', 'warn')
            msg = f"[Catalog] ⚠ catalog.json not found at {path}"
            print(msg)
            if mode == 'strict':
                raise FileNotFoundError(msg)
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


# ============================================
# HELPERS CANÓNICOS (product.id como clave interna)
# ============================================

def get_product_by_id(product_id: str) -> Optional[dict]:
    """Busca un producto por su ID canónico. Retorna el dict del producto o None."""
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            if product['id'] == product_id:
                return {**product, 'product_line': line['id'], 'line_name': line['name']}
    return None


def get_product_name_map() -> Dict[str, str]:
    """Mapa product.id → product.name (canónico interno → nombre visible)."""
    name_map = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            name_map[product['id']] = product['name']
    return name_map


def get_product_alias_to_id_map() -> Dict[str, str]:
    """Mapa alias → product.id (para routing y boost por producto)."""
    alias_map = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            pid = product['id']
            # El nombre del producto también es un alias hacia su id
            alias_map[product['name'].lower()] = pid
            for alias in product.get('aliases', []):
                alias_map[alias.lower()] = pid
    return alias_map


def get_product_keywords_map() -> Dict[str, List[str]]:
    """Mapa product.id → [keywords] (para boost estructurado por producto)."""
    kw_map = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            pid = product['id']
            keywords = [product['name'].lower()]
            keywords.extend([a.lower() for a in product.get('aliases', [])])
            keywords.extend([c.lower() for c in product.get('conditions', [])])
            keywords.extend([z.lower() for z in product.get('zones', [])])
            if product.get('pretreatment'):
                keywords.append(product['pretreatment'].lower())
            kw_map[pid] = list(set(keywords))
    return kw_map


def get_condition_product_map() -> Dict[str, List[str]]:
    """Mapa condición → [product.id] (canónico interno para routing)."""
    condition_map = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            for condition in product.get('conditions', []):
                cond_lower = condition.lower()
                if cond_lower not in condition_map:
                    condition_map[cond_lower] = []
                condition_map[cond_lower].append(product['id'])
    return condition_map


# ============================================
# HELPERS LEGACY (mantienen interfaz para consumidores existentes)
# ============================================

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
    """Mapa alias → nombre canónico (para normalización de texto en RAG).
    Nota: Para routing por product.id, usar get_product_alias_to_id_map().
    """
    aliases = {}
    for line in get_catalog().get('product_lines', []):
        for product in line.get('products', []):
            canonical = product['name'].lower()
            for alias in product.get('aliases', []):
                aliases[alias.lower()] = canonical
    return aliases


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


def has_competitors() -> bool:
    """True si alguna línea del catálogo tiene competidores cargados.
    Cuando se añadan competidores a catalog.json, la política comparativa
    se activa automáticamente sin cambios de código."""
    for line in get_catalog().get('product_lines', []):
        if line.get('competitors', []):
            return True
    return False


def get_competitors() -> List[dict]:
    """Lista de competidores de todas las líneas, con su product_line.
    Retorna [] mientras competitors esté vacío en catalog.json."""
    competitors = []
    for line in get_catalog().get('product_lines', []):
        for comp in line.get('competitors', []):
            competitors.append({**comp, 'product_line': line['id']})
    return competitors


def get_product_keywords() -> List[str]:
    """Lista plana de keywords de producto para detección de intención."""
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
