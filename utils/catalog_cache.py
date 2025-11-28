import time
import threading
from typing import Callable, Any, Dict, Tuple

_cache_store: Dict[str, Tuple[float, Any]] = {}
_lock = threading.Lock()


def get_or_cache(key: str, ttl: int, loader: Callable[[], Any]) -> Any:
    """Retorna dato cacheado si vigente; de lo contrario ejecuta loader y almacena.

    Params:
        key: identificador único del recurso (ej. 'productos_activos').
        ttl: segundos de vida antes de recargar.
        loader: función sin argumentos que retorna el dato fresco.
    """
    now = time.time()
    with _lock:
        entry = _cache_store.get(key)
        if entry:
            ts, data = entry
            if now - ts < ttl:
                return data
        # cargar fresco fuera del lock para minimizar tiempo bloqueado
    data = loader()
    with _lock:
        _cache_store[key] = (now, data)
    return data


def invalidate(key: str) -> None:
    with _lock:
        _cache_store.pop(key, None)


def clear_all() -> None:
    with _lock:
        _cache_store.clear()
