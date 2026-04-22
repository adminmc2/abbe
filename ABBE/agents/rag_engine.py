"""
Motor RAG v4.0 — BM25 + sinónimos dinámicos + metadata boost + contrato de datos
Base de conocimiento compartida por todos los agentes de Above Pharma.
"""
import json
import math
import os
import re
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

from .catalog import (
    get_catalog, get_product_synonyms, get_product_aliases,
    get_product_keywords, get_product_alias_to_id_map, get_product_keywords_map,
)


# ============================================
# STEMMER ESPAÑOL SIMPLIFICADO
# ============================================
class SpanishStemmer:
    """Stemmer ligero para español basado en sufijos comunes"""

    SUFFIXES = [
        'ándose', 'iéndose', 'amente', 'mente',
        'ación', 'ición', 'ando', 'iendo', 'ador', 'edor', 'idor',
        'ante', 'ente', 'anza', 'encia', 'ible', 'able',
        'ivo', 'iva', 'oso', 'osa', 'dad', 'ión',
        'ar', 'er', 'ir', 'do', 'da', 'os', 'as', 'es',
    ]

    # Palabras que no deben ser stemmed (términos médicos y técnicos)
    EXCEPTIONS = {
        'hialuronidasa', 'embarazo', 'lifting', 'light', 'medium', 'volume',
    }

    @classmethod
    def stem(cls, word: str) -> str:
        """Reduce una palabra a su raíz"""
        word = word.lower()
        if word in cls.EXCEPTIONS or len(word) < 4:
            return word
        for suffix in cls.SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                return word[:-len(suffix)]
        return word


# ============================================
# SINÓNIMOS MÉDICOS ESTÁTICOS (genéricos para medicina estética)
# ============================================
MEDICAL_SYNONYMS: Dict[str, List[str]] = {
    # Ácido hialurónico
    'hialurónico': ['ácido hialurónico', 'ah', 'hialuronato'],
    'hialuronico': ['ácido hialurónico', 'ah', 'hialuronato'],
    'hialuronidasa': ['disolver', 'reversible', 'emergencia'],
    'biomodulador': ['bioestimulador', 'regenerador'],
    'relleno': ['filler', 'ácido hialurónico', 'dermal filler'],
    'filler': ['relleno', 'ácido hialurónico'],

    # Técnicas y protocolos
    'lifting': ['levantamiento', 'tensado', 'reafirmante'],
    'cánula': ['canula', 'instrumento', 'inyección'],
    'aguja': ['needle', 'instrumento', 'inyección'],
    'protocolo': ['técnica', 'procedimiento', 'tratamiento', 'aplicación'],
    'reticulante': ['reticulación', 'crosslinker'],

    # Zonas anatómicas
    'ojera': ['surco lagrimal', 'periorbital', 'tear trough'],
    'lagrimal': ['ojera', 'periorbital', 'tear trough'],
    'labio': ['labial', 'peribucal', 'boca', 'vermillion'],
    'mandíbula': ['mandibula', 'mandibular', 'jawline', 'ángulo mandibular'],
    'surco': ['nasogeniano', 'nasolabial', 'pliegue'],
    'pómulo': ['pomulo', 'malar', 'pómulos', 'mejilla'],
    'mentón': ['menton', 'chin', 'mentoniano'],

    # Condiciones estéticas
    'flacidez': ['laxitud', 'caída', 'descolgamiento', 'firmeza'],
    'arruga': ['línea', 'surco', 'pliegue', 'rítide'],
    'volumen': ['proyección', 'relleno', 'aumento', 'definición'],
    'rejuvenecimiento': ['anti-aging', 'regeneración', 'juventud'],
    'edema': ['hinchazón', 'inflamación', 'hinchado'],

    # Comparativas y objeciones
    'mejor': ['superior', 'óptimo', 'ideal', 'recomendado', 'preferible'],
    'diferencia': ['comparar', 'comparativa', 'versus', 'contra', 'diferente'],
    'precio': ['costo', 'coste', 'valor', 'económico', 'caro', 'barato'],

    # Seguridad
    'contraindicación': ['contraindicacion', 'riesgo', 'prohibido', 'no tratar'],
    'complicación': ['complicacion', 'problema', 'emergencia', 'adverso'],
    'embarazo': ['embarazada', 'gestación', 'lactancia'],
}


# ============================================
# BM25 INDEX
# ============================================
class BM25Index:
    """Índice BM25 (Okapi) para búsqueda léxica sin dependencias externas."""

    def __init__(self, tokenized_docs: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.n_docs = len(tokenized_docs)
        self.doc_lengths = [len(doc) for doc in tokenized_docs]
        self.avgdl = sum(self.doc_lengths) / self.n_docs if self.n_docs else 1

        # Document frequencies
        self.df: Dict[str, int] = Counter()
        for doc in tokenized_docs:
            for token in set(doc):
                self.df[token] += 1

        # Precompute IDF
        self.idf: Dict[str, float] = {}
        for token, freq in self.df.items():
            self.idf[token] = math.log((self.n_docs - freq + 0.5) / (freq + 0.5) + 1)

        # Term frequencies per document
        self.doc_tf: List[Counter] = [Counter(doc) for doc in tokenized_docs]

    def score(self, query_tokens: List[str]) -> List[float]:
        """Score all documents against query tokens."""
        scores = []
        for i in range(self.n_docs):
            s = 0.0
            dl = self.doc_lengths[i]
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf = self.doc_tf[i].get(token, 0)
                idf = self.idf[token]
                num = tf * (self.k1 + 1)
                den = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                s += idf * num / den
            scores.append(s)
        return scores


# ============================================
# RAG ENGINE
# ============================================
class RAGEngine:
    """Motor de búsqueda RAG con BM25, expansión de sinónimos y metadata boost."""

    STOPWORDS = {
        'el', 'la', 'los', 'las', 'de', 'del', 'en', 'un', 'una',
        'y', 'a', 'que', 'es', 'por', 'para', 'con', 'se', 'su',
        'al', 'lo', 'como', 'mas', 'pero', 'sus', 'le', 'ya', 'o',
        'cual', 'cuales', 'donde', 'cuando', 'si',
        'no', 'muy', 'sin', 'sobre', 'este', 'esta', 'esto', 'eso',
        'mi', 'tu', 'me', 'te', 'nos', 'les', 'tiene', 'hay',
    }

    def __init__(self, knowledge_base_path: str):
        self.qa_pairs: List[dict] = []
        self.stemmer = SpanishStemmer()
        self.bm25: Optional[BM25Index] = None

        # Merge synonyms: medical (static) + product (from catalog)
        self.synonyms: Dict[str, List[str]] = dict(MEDICAL_SYNONYMS)
        self.synonyms.update(get_product_synonyms())

        # Product aliases for normalization
        self.product_aliases: Dict[str, str] = get_product_aliases()

        # Product keywords for intent detection
        self.product_keywords: List[str] = get_product_keywords()

        # Load and index
        self.load_knowledge_base(knowledge_base_path)
        self._build_bm25_index()

    # Campos obligatorios por Q&A (contrato de datos)
    REQUIRED_FIELDS = {'id', 'categoria', 'pregunta', 'respuesta', 'source_doc', 'product_line', 'product'}
    NON_EMPTY_FIELDS = {'pregunta', 'respuesta', 'source_doc', 'categoria'}

    # Lista cerrada de categorías válidas (fuente única de verdad)
    VALID_CATEGORIES = {
        'empresa', 'productos', 'tecnologia', 'protocolos', 'seguridad',
        'objeciones_precio', 'objeciones_eficacia', 'objeciones_seguridad',
        'argumentos_venta', 'perfil_paciente',
    }

    def load_knowledge_base(self, path: str):
        """Carga la base de conocimiento desde JSON, normaliza fuentes y valida contrato de datos."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.qa_pairs = data.get('qa_pairs', [])

        # Normalizar source_doc → normalized_sources (lista interna canónica)
        for qa in self.qa_pairs:
            raw = qa.get('source_doc', '')
            if '+' in raw:
                qa['normalized_sources'] = [s.strip() for s in raw.split('+') if s.strip()]
            else:
                qa['normalized_sources'] = [raw] if raw else []

        self._validate_kb()
        print(f"[RAG] Cargadas {len(self.qa_pairs)} preguntas")

    def _validate_kb(self):
        """Valida contrato de datos: campos obligatorios, IDs únicos, categorías, referencias válidas.

        Modo controlado por KB_VALIDATION_MODE:
          - 'warn' (default): reporta errores sin detener el arranque
          - 'strict': lanza ValueError si hay errores (recomendado en local/predeploy)
        """
        errors = []
        ids_seen = set()
        catalog = get_catalog()
        valid_lines = {line['id'] for line in catalog.get('product_lines', [])}
        valid_products = {}
        for line in catalog.get('product_lines', []):
            for prod in line.get('products', []):
                valid_products[prod['id']] = line['id']

        for qa in self.qa_pairs:
            qid = qa.get('id', '?')

            # Campos obligatorios presentes
            missing = self.REQUIRED_FIELDS - set(qa.keys())
            if missing:
                errors.append(f"Q&A #{qid}: missing fields {missing}")

            # Campos no vacíos
            for field in self.NON_EMPTY_FIELDS:
                if field in qa and not qa[field]:
                    errors.append(f"Q&A #{qid}: empty '{field}'")

            # Categoría debe pertenecer a la allowlist
            cat = qa.get('categoria')
            if cat and cat not in self.VALID_CATEGORIES:
                errors.append(f"Q&A #{qid}: categoria '{cat}' not in VALID_CATEGORIES")

            # ID único
            if qid in ids_seen:
                errors.append(f"Q&A #{qid}: duplicate ID")
            ids_seen.add(qid)

            # product_line debe existir en catalog
            pl = qa.get('product_line')
            if pl and pl not in valid_lines:
                errors.append(f"Q&A #{qid}: product_line '{pl}' not in catalog")

            # product debe existir en su product_line
            prod = qa.get('product')
            if prod and prod not in valid_products:
                errors.append(f"Q&A #{qid}: product '{prod}' not in catalog")
            elif prod and valid_products.get(prod) != pl:
                errors.append(f"Q&A #{qid}: product '{prod}' not in line '{pl}'")

        if errors:
            mode = os.environ.get('KB_VALIDATION_MODE', 'warn')
            print(f"[RAG] ⚠ KB validation: {len(errors)} errors:")
            for e in errors:
                print(f"  {e}")
            if mode == 'strict':
                raise ValueError(f"KB validation failed ({len(errors)} errors). Fix data or set KB_VALIDATION_MODE=warn")
        else:
            print(f"[RAG] ✓ KB validation passed ({len(self.qa_pairs)} Q&As, contract OK)")

    def _build_bm25_index(self):
        """Construye el índice BM25 sobre pregunta + respuesta."""
        if not self.qa_pairs:
            self.bm25 = BM25Index([])
            print("[RAG] KB vacía — índice BM25 vacío")
            return

        documents = [qa['pregunta'] + ' ' + qa['respuesta'] for qa in self.qa_pairs]
        tokenized = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Index(tokenized)
        vocab_size = len(self.bm25.df)
        print(f"[RAG] Índice BM25 construido: {vocab_size} términos, {len(self.qa_pairs)} documentos")

    def _normalize(self, text: str) -> str:
        """Normaliza texto: minúsculas, sin acentos, unifica aliases de producto."""
        text = text.lower()
        # Unificar aliases de producto
        for alias, canonical in self.product_aliases.items():
            text = text.replace(alias, canonical)
        # Quitar acentos para búsqueda
        for acc, plain in {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n'}.items():
            text = text.replace(acc, plain)
        return text

    def _tokenize(self, text: str, apply_stemming: bool = True) -> List[str]:
        """Tokeniza texto con normalización y stemming opcional."""
        text = self._normalize(text)
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        tokens = [w for w in words if w not in self.STOPWORDS and len(w) > 2]
        if apply_stemming:
            tokens = [self.stemmer.stem(w) for w in tokens]
        return tokens

    def _expand_query(self, query: str) -> str:
        """Expande la query con sinónimos (query expansion, no tercer ranker)."""
        words = self._tokenize(query, apply_stemming=False)
        expanded = list(words)
        for word in words:
            if word in self.synonyms:
                expanded.extend(self.synonyms[word][:3])
        return ' '.join(expanded)

    def _detect_product_line(self, query: str) -> Optional[str]:
        """Detecta a qué línea de producto se refiere la query."""
        query_lower = query.lower()
        catalog = get_catalog()
        for line in catalog.get('product_lines', []):
            if line['name'].lower() in query_lower:
                return line['id']
            for product in line.get('products', []):
                if product['name'].lower() in query_lower:
                    return line['id']
                for alias in product.get('aliases', []):
                    if alias.lower() in query_lower:
                        return line['id']
        return None

    def _detect_product(self, query: str) -> Optional[str]:
        """Detecta a qué product.id se refiere la query.

        Señales usadas (en orden de prioridad):
          1. product.name o aliases explícitos del catálogo
          2. keywords del producto (conditions, pretreatment, zones)

        Retorna product.id o None si no se detecta producto específico.
        No hardcodea nombres — todo viene del catálogo.
        """
        query_lower = query.lower()

        # 1. Señal fuerte: nombre o alias del producto
        alias_to_id = get_product_alias_to_id_map()
        for alias, pid in alias_to_id.items():
            if alias in query_lower:
                return pid

        # 2. Señal secundaria: keywords (conditions, pretreatment, zones)
        kw_map = get_product_keywords_map()
        best_pid = None
        best_count = 0
        for pid, keywords in kw_map.items():
            count = sum(1 for kw in keywords if kw in query_lower and len(kw) > 3)
            if count > best_count:
                best_count = count
                best_pid = pid
        if best_count >= 1:
            return best_pid

        return None

    def search(self, query: str, top_k: int = 5, categories: Optional[List[str]] = None) -> List[Tuple[dict, float]]:
        """
        Búsqueda: BM25 con query expansion + metadata boost.

        Args:
            query: Texto de búsqueda
            top_k: Número de resultados
            categories: Lista de categorías para filtrar (None = todas)

        Returns:
            Lista de (qa_pair, score)
        """
        if not self.qa_pairs or self.bm25 is None:
            return []

        # 1. Expandir query con sinónimos
        expanded_query = self._expand_query(query)

        # 2. Tokenizar query expandida (con stemming)
        query_tokens = self._tokenize(expanded_query)
        if not query_tokens:
            return []

        # 3. BM25 scoring
        raw_scores = self.bm25.score(query_tokens)

        # 4. Detectar product_line y product.id para metadata boost
        detected_line = self._detect_product_line(query)
        detected_product = self._detect_product(query)

        # 5. Aplicar filtros, metadata boost y normalizar
        scored: List[Tuple[int, float]] = []
        for i, score in enumerate(raw_scores):
            qa = self.qa_pairs[i]

            # Filtro por categorías
            if categories and qa.get('categoria', '') not in categories:
                continue

            if score <= 0:
                continue

            # Metadata boost: +30% si coincide product_line
            if detected_line and qa.get('product_line') == detected_line:
                score *= 1.3

            # Metadata boost: +25% si coincide product.id
            # product=null queda neutral (no se penaliza ni se boostea)
            if detected_product and qa.get('product') == detected_product:
                score *= 1.25

            # Boost por coincidencia directa en pregunta
            query_norm = self._normalize(query)
            pregunta_norm = self._normalize(qa['pregunta'])
            query_words = set(self._tokenize(query, apply_stemming=False))
            direct_matches = sum(1 for w in query_words if w in pregunta_norm and len(w) > 3)
            if direct_matches > 0:
                score *= (1 + direct_matches * 0.2)

            scored.append((i, score))

        # 6. Normalizar scores a [0, 1]
        if scored:
            max_score = max(s for _, s in scored)
            if max_score > 0:
                scored = [(i, s / max_score) for i, s in scored]

        # 7. Ordenar y devolver top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        return [(self.qa_pairs[i], score) for i, score in scored[:top_k]]

    def get_categories(self) -> List[str]:
        """Retorna todas las categorías disponibles."""
        return list(set(qa.get('categoria', '') for qa in self.qa_pairs))


# Singleton del motor RAG
_rag_instance = None


def get_rag_engine() -> RAGEngine:
    """Obtiene la instancia singleton del RAG."""
    global _rag_instance
    if _rag_instance is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        kb_path = os.path.join(base_path, 'knowledge_base.json')
        _rag_instance = RAGEngine(kb_path)
    return _rag_instance
