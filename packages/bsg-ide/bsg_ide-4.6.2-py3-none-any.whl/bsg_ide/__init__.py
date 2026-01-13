import sys
import importlib
from typing import Optional
from functools import lru_cache

# Lazy loading system
_MODULES = {
    'Editor': 'bsg_ide.core.editor',
    'Terminal': 'bsg_ide.core.terminal',
    'Presentation': 'bsg_ide.core.presentation'
}

def __getattr__(name: str):
    if name in _MODULES:
        module = importlib.import_module(_MODULES[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

@lru_cache(maxsize=1)
def get_config():
    """Cached configuration loader"""
    from .core.config import Config
    return Config.load()

def init_async():
    """Initialize async components"""
    from .utils.async_tools import run_async_init
    return run_async_init()
