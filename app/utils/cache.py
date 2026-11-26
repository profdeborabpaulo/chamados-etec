"""Sistema de Cache em Memória Pythonic para dados de referência frequente.

Reduz acessos redundantes ao PostgreSQL/Supabase em consultas de tabelas
estáticas como salas, laboratórios, categorias técnicas e lista de técnicos.
"""

from typing import Dict, List, Any, Optional
from threading import Lock
from app.models.reference_data import Room, Category
from app.models.user import User

# Estruturas padrão caso o banco ainda esteja vazio ou em inicialização
DEFAULT_ROOM_CATEGORIES = {
    "sala_aula": {
        "label": "Salas de Aula",
        "salas": [f"Sala {i}" for i in range(1, 16)]
    },
    "lab_maker": {
        "label": "Laboratórios / Maker",
        "salas": [f"Laboratório {i}" for i in range(1, 6)] + ["Sala Maker"]
    },
    "administrativo": {
        "label": "Administrativo",
        "salas": ["Secretaria"]
    }
}

DEFAULT_CATEGORIES = [
    "Infraestrutura de Rede",
    "Problemas de Periféricos",
    "Hardware Interno",
    "Software / Sistema Operacional",
    "Projetor / Multimídia",
    "Outros"
]


class MemoryCache:
    """Cache thread-safe leve com suporte a invalidação programática."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value

    def invalidate(self, key: Optional[str] = None) -> None:
        """Invalida uma chave específica ou limpa todo o cache se key=None."""
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)


# Instância global do cache
app_cache = MemoryCache()


def get_cached_room_categories() -> Dict[str, Dict[str, Any]]:
    """Retorna salas agrupadas por categoria com cache."""
    cached = app_cache.get('room_categories')
    if cached is not None:
        return cached

    try:
        rooms = Room.query.order_by(Room.id.asc()).all()
        if rooms:
            data: Dict[str, Dict[str, Any]] = {
                "sala_aula": {"label": "Salas de Aula", "salas": []},
                "lab_maker": {"label": "Laboratórios / Maker", "salas": []},
                "administrativo": {"label": "Administrativo", "salas": []}
            }
            for room in rooms:
                cat = room.categoria
                if cat not in data:
                    data[cat] = {"label": cat.replace('_', ' ').title(), "salas": []}
                data[cat]["salas"].append(room.nome)
            
            app_cache.set('room_categories', data)
            return data
    except Exception:
        pass

    # Fallback seguro
    return DEFAULT_ROOM_CATEGORIES


def get_cached_categories() -> List[str]:
    """Retorna lista de categorias de problemas técnicos com cache."""
    cached = app_cache.get('categories')
    if cached is not None:
        return cached

    try:
        categories = Category.query.filter_by(ativo=True).order_by(Category.id.asc()).all()
        if categories:
            data = [c.nome for c in categories]
            app_cache.set('categories', data)
            return data
    except Exception:
        pass

    return DEFAULT_CATEGORIES


def get_cached_tecnicos() -> List[User]:
    """Retorna lista de técnicos para o modal de atribuição com cache."""
    cached = app_cache.get('tecnicos')
    if cached is not None:
        return cached

    try:
        tecnicos = User.query.filter(
            User.perfil.in_(['tecnico', 'admin']),
            User.ativo == True
        ).order_by(User.nome.asc()).all()
        
        if tecnicos:
            app_cache.set('tecnicos', tecnicos)
            return tecnicos
    except Exception:
        pass

    return []


def invalidate_app_cache() -> None:
    """Limpa todas as chaves em memória para recarga imediata dos dados do banco."""
    app_cache.invalidate()
