from .core.cpp_api import CppApi
from .core import cssl_bridge as CSSL
import warnings

__version__ = "4.3.0"
__all__ = ["CppApi", "CSSL"]

# Module-level cache for C++ modules
_api_instance = None
_loaded_modules = {}

def _get_api():
    """Get or create singleton CppApi instance."""
    global _api_instance
    if _api_instance is None:
        _api_instance = CppApi()
    return _api_instance

def __getattr__(name: str):
    """Enable: from includecpp import fast_list

    This hook is called when Python cannot find an attribute in this module.
    It allows dynamic C++ module loading via the import system.
    """
    if name.startswith('_'):
        raise AttributeError(f"module 'includecpp' has no attribute '{name}'")

    if name in _loaded_modules:
        return _loaded_modules[name]

    api = _get_api()

    if name not in api.registry:
        available = list(api.registry.keys())
        raise AttributeError(
            f"Module '{name}' not found. "
            f"Available: {available}. "
            f"Run 'includecpp rebuild' first."
        )

    if api.need_update(name):
        warnings.warn(
            f"Module '{name}' source files changed. "
            f"Run 'includecpp rebuild' to update.",
            UserWarning
        )

    module = api.include(name)
    _loaded_modules[name] = module
    return module

def __dir__():
    """List available attributes including C++ modules."""
    base = ['CppApi', 'CSSL', '__version__']
    try:
        api = _get_api()
        return sorted(set(base + list(api.registry.keys())))
    except Exception:
        return base
