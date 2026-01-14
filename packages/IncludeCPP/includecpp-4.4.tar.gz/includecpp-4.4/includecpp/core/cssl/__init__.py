"""
CSSL - C-Style Scripting Language
Bundled with IncludeCPP for integrated scripting support.

Features:
- BruteForce Injection System: <==, ==>, +<==, -<==, <<==, ==>>
- Dynamic typing with 'dynamic' keyword
- Function modifiers: undefined, open, meta, super, closed, private, virtual
- Advanced data types: datastruct, shuffled, iterator, combo, dataspace
- Injection helpers: string::where, json::key, array::index, etc.
- Global references: @Name, r@Name, s@Name

Performance:
- C++ acceleration available via cssl_core module (10-20x speedup)
- Pre-built binaries bundled for Windows (x64) and Linux (x64)
- Falls back to local compilation if no pre-built available
- Use is_cpp_available() to check if C++ module is loaded
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Optional

# C++ acceleration state
_CPP_AVAILABLE = False
_cpp_module = None
_CPP_LOAD_SOURCE = None  # 'bundled', 'appdata', 'includecpp', None
_CPP_MODULE_PATH = None


def _load_module_from_path(path: Path) -> Optional[object]:
    """
    Load a Python extension module from file path.

    IncludeCPP builds modules with 'api' as the export name, containing
    submodules for each plugin. We load the 'api' module and return the
    'cssl_core' submodule.

    Args:
        path: Path to .pyd/.so module file

    Returns:
        Loaded cssl_core submodule, or None if loading failed
    """
    dll_handle = None
    try:
        # On Windows, add DLL directory to search path (for MinGW runtime DLLs)
        if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
            dll_dir = path.parent
            if dll_dir.exists():
                dll_handle = os.add_dll_directory(str(dll_dir))

        # IncludeCPP exports as 'api', with plugins as submodules
        spec = importlib.util.spec_from_file_location('api', str(path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Return the cssl_core submodule
            if hasattr(module, 'cssl_core'):
                return module.cssl_core
            return module
    except Exception:
        pass
    finally:
        # Clean up DLL directory handle
        if dll_handle is not None:
            try:
                dll_handle.close()
            except Exception:
                pass
    return None


def _try_load_bundled() -> bool:
    """
    Try to load pre-built bundled module from package directory.

    Checks cpp/build/ and bin/ directories for platform-matching module.

    Returns:
        True if module loaded successfully
    """
    global _CPP_AVAILABLE, _cpp_module, _CPP_LOAD_SOURCE, _CPP_MODULE_PATH

    try:
        from .cssl_compiler import CSSLCompilerConfig

        config = CSSLCompilerConfig()
        config.setup_first_run()

        suffixes = config.get_all_possible_suffixes()
        package_dir = Path(__file__).parent

        build_dirs = [
            package_dir / 'cpp' / 'build',
            package_dir / 'bin',
        ]

        for build_dir in build_dirs:
            if not build_dir.exists():
                continue

            for suffix in suffixes:
                module_path = build_dir / f'cssl_core{suffix}'
                if module_path.exists():
                    module = _load_module_from_path(module_path)
                    if module:
                        _cpp_module = module
                        _CPP_AVAILABLE = True
                        _CPP_LOAD_SOURCE = 'bundled'
                        _CPP_MODULE_PATH = str(module_path)
                        return True
    except ImportError:
        # cssl_compiler not available yet - try basic loading
        pass

    return False


def _try_load_from_appdata() -> bool:
    """
    Try to load locally compiled module from APPDATA.

    If a module was previously compiled locally, load it.

    Returns:
        True if module loaded successfully
    """
    global _CPP_AVAILABLE, _cpp_module, _CPP_LOAD_SOURCE, _CPP_MODULE_PATH

    try:
        from .cssl_compiler import CSSLCompilerConfig, get_cssl_build_dir

        config = CSSLCompilerConfig()
        config.setup_first_run()

        suffixes = config.get_all_possible_suffixes()
        build_dir = get_cssl_build_dir()

        for suffix in suffixes:
            module_path = build_dir / f'cssl_core{suffix}'
            if module_path.exists():
                module = _load_module_from_path(module_path)
                if module:
                    _cpp_module = module
                    _CPP_AVAILABLE = True
                    _CPP_LOAD_SOURCE = 'appdata'
                    _CPP_MODULE_PATH = str(module_path)
                    return True
    except ImportError:
        pass

    return False


def _try_load_from_includecpp() -> bool:
    """
    Try to load from IncludeCPP's module system.

    This works if user built cssl_core via 'includecpp rebuild'.

    Returns:
        True if module loaded successfully
    """
    global _CPP_AVAILABLE, _cpp_module, _CPP_LOAD_SOURCE, _CPP_MODULE_PATH

    try:
        from includecpp import cssl_core as module
        _cpp_module = module
        _CPP_AVAILABLE = True
        _CPP_LOAD_SOURCE = 'includecpp'
        _CPP_MODULE_PATH = getattr(module, '__file__', None)
        return True
    except ImportError:
        return False


def _try_compile_locally() -> bool:
    """
    Try to compile cssl_core locally if no pre-built available.

    Only attempts if user has a C++ compiler installed.

    Returns:
        True if compilation succeeded and module loaded
    """
    global _CPP_AVAILABLE, _cpp_module, _CPP_LOAD_SOURCE, _CPP_MODULE_PATH

    try:
        from .cssl_compiler import CSSLCompilerConfig, compile_cssl_core

        config = CSSLCompilerConfig()
        if not config.can_compile():
            return False

        # Try to compile
        module_path = compile_cssl_core()
        if module_path and module_path.exists():
            module = _load_module_from_path(module_path)
            if module:
                _cpp_module = module
                _CPP_AVAILABLE = True
                _CPP_LOAD_SOURCE = 'compiled'
                _CPP_MODULE_PATH = str(module_path)
                return True
    except ImportError:
        pass

    return False


def _initialize_cpp_module():
    """
    Initialize C++ module - try all loading methods in order.

    Loading order:
    1. Bundled module (pre-built in package)
    2. APPDATA module (previously compiled locally)
    3. IncludeCPP import (if user ran includecpp rebuild)
    4. Local compilation (if compiler available)
    """
    # Try bundled first (fastest, most reliable for users)
    if _try_load_bundled():
        return

    # Try APPDATA (previously compiled locally)
    if _try_load_from_appdata():
        return

    # Try includecpp import
    if _try_load_from_includecpp():
        return

    # Last resort: try to compile locally (if compiler available)
    # Note: This is slow on first run, but only happens once
    # Disabled by default - uncomment to enable auto-compilation
    # _try_compile_locally()


# Initialize on import
_initialize_cpp_module()


# =============================================================================
# Public API
# =============================================================================

def is_cpp_available() -> bool:
    """Check if C++ acceleration is available."""
    return _CPP_AVAILABLE


def get_cpp_version() -> Optional[str]:
    """Get C++ module version, or None if not available."""
    if _CPP_AVAILABLE and _cpp_module and hasattr(_cpp_module, 'version'):
        try:
            return _cpp_module.version()
        except Exception:
            pass
    return None


def get_cpp_platform() -> Optional[str]:
    """Get the platform the C++ module was loaded for."""
    return sys.platform if _CPP_AVAILABLE else None


def get_cpp_info() -> dict:
    """
    Get detailed C++ acceleration info.

    Returns:
        dict with keys:
        - available: bool - whether C++ is available
        - source: str - where module was loaded from
        - version: str - module version
        - platform: dict - platform info
        - module_path: str - path to loaded module
        - can_compile: bool - whether local compilation is possible
    """
    result = {
        'available': _CPP_AVAILABLE,
        'source': _CPP_LOAD_SOURCE,
        'version': get_cpp_version(),
        'module_path': _CPP_MODULE_PATH,
    }

    try:
        from .cssl_compiler import CSSLCompilerConfig
        config = CSSLCompilerConfig()
        result['platform'] = config.get_platform_info()
        result['compiler'] = config.get_compiler()
        result['can_compile'] = config.can_compile()
    except ImportError:
        result['platform'] = {'platform': sys.platform}
        result['compiler'] = None
        result['can_compile'] = False

    return result


def compile_cpp_module(force: bool = False) -> bool:
    """
    Manually trigger C++ module compilation.

    Use this if you want to enable C++ acceleration and have a compiler.

    Args:
        force: If True, recompile even if module exists

    Returns:
        True if compilation succeeded
    """
    global _CPP_AVAILABLE, _cpp_module, _CPP_LOAD_SOURCE, _CPP_MODULE_PATH

    try:
        from .cssl_compiler import compile_cssl_core

        module_path = compile_cssl_core(force=force)
        if module_path and module_path.exists():
            module = _load_module_from_path(module_path)
            if module:
                _cpp_module = module
                _CPP_AVAILABLE = True
                _CPP_LOAD_SOURCE = 'compiled'
                _CPP_MODULE_PATH = str(module_path)
                return True
    except ImportError:
        pass

    return False


# =============================================================================
# Import CSSL modules
# =============================================================================

from .cssl_parser import (
    parse_cssl, parse_cssl_program, tokenize_cssl,
    CSSLSyntaxError, CSSLLexer, CSSLParser, ASTNode,
    KEYWORDS, TYPE_GENERICS, TYPE_PARAM_FUNCTIONS, INJECTION_HELPERS
)
from .cssl_runtime import (
    CSSLRuntime, CSSLRuntimeError, CSSLServiceRunner, run_cssl, run_cssl_file,
    register_filter, unregister_filter, get_custom_filters
)
from .cssl_types import (
    DataStruct, Shuffled, Iterator, Combo, DataSpace, OpenQuote,
    OpenFind, Parameter, Stack, Vector, Array,
    create_datastruct, create_shuffled, create_iterator,
    create_combo, create_dataspace, create_openquote, create_parameter,
    create_stack, create_vector, create_array
)


# =============================================================================
# Fast tokenize with C++ acceleration
# =============================================================================

def fast_tokenize(source: str):
    """
    Tokenize CSSL source code.

    Uses C++ Lexer if available (10-20x faster), otherwise Python.

    Args:
        source: CSSL source code string

    Returns:
        List of tokens
    """
    if _CPP_AVAILABLE and _cpp_module and hasattr(_cpp_module, 'Lexer'):
        try:
            lexer = _cpp_module.Lexer(source)
            return lexer.tokenize()
        except Exception:
            pass
    return tokenize_cssl(source)


# =============================================================================
# Optimizer - Smart Performance System
# =============================================================================

from .cssl_optimizer import (
    run_optimized, get_optimizer_stats, configure_optimizer, clear_cache,
    get_optimized_ops, precompile, PrecompiledPattern,
    OptimizedOperations, OptimizedRuntime, ASTCache,
    ExecutionContext, PerformanceThresholds, THRESHOLDS, OPS
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # C++ Acceleration
    'is_cpp_available', 'get_cpp_version', 'get_cpp_platform', 'get_cpp_info',
    'fast_tokenize', 'compile_cpp_module',
    # Optimizer (NEW)
    'run_optimized', 'get_optimizer_stats', 'configure_optimizer', 'clear_cache',
    'get_optimized_ops', 'precompile', 'PrecompiledPattern',
    'OptimizedOperations', 'OptimizedRuntime', 'ASTCache',
    'ExecutionContext', 'PerformanceThresholds', 'THRESHOLDS', 'OPS',
    # Parser
    'parse_cssl', 'parse_cssl_program', 'tokenize_cssl',
    'CSSLSyntaxError', 'CSSLLexer', 'CSSLParser', 'ASTNode',
    'KEYWORDS', 'TYPE_GENERICS', 'TYPE_PARAM_FUNCTIONS', 'INJECTION_HELPERS',
    # Runtime
    'CSSLRuntime', 'CSSLRuntimeError', 'CSSLServiceRunner',
    'run_cssl', 'run_cssl_file',
    # Filter Registration
    'register_filter', 'unregister_filter', 'get_custom_filters',
    # Data Types
    'DataStruct', 'Shuffled', 'Iterator', 'Combo', 'DataSpace', 'OpenQuote',
    'OpenFind', 'Parameter', 'Stack', 'Vector', 'Array',
    'create_datastruct', 'create_shuffled', 'create_iterator',
    'create_combo', 'create_dataspace', 'create_openquote', 'create_parameter',
    'create_stack', 'create_vector', 'create_array'
]
