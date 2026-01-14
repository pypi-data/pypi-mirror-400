"""
CSSL Optimizer - Smart Performance Optimization System

This module provides:
1. Smart threshold-based switching between Python and C++
2. AST caching for repeated execution
3. Optimized runtime with C++ acceleration
4. Adaptive performance tuning based on code complexity

The optimizer automatically chooses the fastest execution path based on:
- Source code size
- Operation complexity
- Available C++ acceleration
- Cached AST availability
"""

import sys
import time
import hashlib
import weakref
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable
from dataclasses import dataclass, field
from functools import lru_cache
from threading import Lock


# =============================================================================
# Performance Thresholds
# =============================================================================

@dataclass
class PerformanceThresholds:
    """Configurable thresholds for optimization decisions."""

    # Source size thresholds (characters)
    small_source: int = 500          # Use Python for < 500 chars
    medium_source: int = 5000        # Mixed optimization
    large_source: int = 50000        # Full C++ acceleration

    # Token count thresholds
    small_tokens: int = 100          # Few tokens - Python is fine
    large_tokens: int = 1000         # Many tokens - use C++

    # Loop iteration thresholds
    small_loop: int = 100            # Small loops - Python OK
    large_loop: int = 1000           # Large loops - prefer C++ helpers

    # String operation thresholds
    small_string: int = 100          # Short strings - Python
    large_string: int = 10000        # Long strings - C++

    # Cache settings
    cache_enabled: bool = True
    cache_max_size: int = 100        # Max cached ASTs
    cache_ttl: float = 300.0         # 5 minutes TTL

    # Adaptive tuning
    adaptive_enabled: bool = True
    sample_size: int = 10            # Samples for timing


# Global thresholds instance
THRESHOLDS = PerformanceThresholds()


# =============================================================================
# AST Cache
# =============================================================================

@dataclass
class CachedAST:
    """Cached AST with metadata."""
    ast: Any
    source_hash: str
    created_at: float
    access_count: int = 0
    total_exec_time: float = 0.0

    @property
    def avg_exec_time(self) -> float:
        if self.access_count == 0:
            return 0.0
        return self.total_exec_time / self.access_count


class ASTCache:
    """
    Thread-safe AST cache with LRU eviction and TTL.

    Caches parsed ASTs to avoid re-parsing the same source code.
    Provides significant speedup for repeated execution.
    """

    def __init__(self, max_size: int = 100, ttl: float = 300.0):
        self._cache: Dict[str, CachedAST] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._ttl = ttl
        self._hits = 0
        self._misses = 0

    def _hash_source(self, source: str) -> str:
        """Create hash of source code."""
        return hashlib.md5(source.encode('utf-8')).hexdigest()

    def get(self, source: str) -> Optional[Any]:
        """Get cached AST for source code."""
        source_hash = self._hash_source(source)

        with self._lock:
            if source_hash in self._cache:
                cached = self._cache[source_hash]

                # Check TTL
                if time.time() - cached.created_at > self._ttl:
                    del self._cache[source_hash]
                    self._misses += 1
                    return None

                cached.access_count += 1
                self._hits += 1
                return cached.ast

            self._misses += 1
            return None

    def put(self, source: str, ast: Any) -> None:
        """Cache AST for source code."""
        source_hash = self._hash_source(source)

        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self._max_size:
                self._evict_lru()

            self._cache[source_hash] = CachedAST(
                ast=ast,
                source_hash=source_hash,
                created_at=time.time()
            )

    def record_execution(self, source: str, exec_time: float) -> None:
        """Record execution time for adaptive optimization."""
        source_hash = self._hash_source(source)

        with self._lock:
            if source_hash in self._cache:
                self._cache[source_hash].total_exec_time += exec_time

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find oldest/least accessed
        oldest_hash = min(
            self._cache.keys(),
            key=lambda h: (self._cache[h].access_count, -self._cache[h].created_at)
        )
        del self._cache[oldest_hash]

    def clear(self) -> None:
        """Clear all cached ASTs."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self.hit_rate,
        }


# Global AST cache
_AST_CACHE = ASTCache(
    max_size=THRESHOLDS.cache_max_size,
    ttl=THRESHOLDS.cache_ttl
)


# =============================================================================
# Smart Execution Context
# =============================================================================

@dataclass
class ExecutionContext:
    """Context for optimized execution decisions."""
    source: str
    source_size: int = 0
    token_count: int = 0
    has_loops: bool = False
    has_classes: bool = False
    has_functions: bool = False
    estimated_complexity: str = "simple"  # simple, medium, complex
    use_cpp_tokenizer: bool = True
    use_cpp_runtime: bool = True
    use_cache: bool = True
    cached_ast: Optional[Any] = None

    def __post_init__(self):
        self.source_size = len(self.source)
        self._analyze_source()

    def _analyze_source(self) -> None:
        """Quick analysis to determine optimization strategy."""
        src = self.source.lower()

        # Check for loops
        self.has_loops = any(kw in src for kw in ['for ', 'while ', 'foreach '])

        # Check for classes
        self.has_classes = 'class ' in src

        # Check for functions
        self.has_functions = any(kw in src for kw in ['define ', 'void ', 'int ', 'string '])

        # Estimate complexity
        if self.source_size < THRESHOLDS.small_source:
            self.estimated_complexity = "simple"
        elif self.source_size < THRESHOLDS.medium_source:
            self.estimated_complexity = "medium"
        else:
            self.estimated_complexity = "complex"

        # Decide C++ usage
        self.use_cpp_tokenizer = self.source_size >= THRESHOLDS.small_source
        self.use_cpp_runtime = self.estimated_complexity != "simple"


# =============================================================================
# Optimized Operations
# =============================================================================

class OptimizedOperations:
    """
    Provides optimized implementations that automatically choose
    between Python and C++ based on input size.
    """

    def __init__(self):
        self._cpp_module = None
        self._cpp_available = False
        self._load_cpp()

    def _load_cpp(self) -> None:
        """Load C++ module if available."""
        try:
            from . import _cpp_module, _CPP_AVAILABLE
            self._cpp_module = _cpp_module
            self._cpp_available = _CPP_AVAILABLE
        except ImportError:
            pass

    # -------------------------------------------------------------------------
    # String Operations
    # -------------------------------------------------------------------------

    def str_upper(self, s: str) -> str:
        """Optimized uppercase conversion."""
        if len(s) < THRESHOLDS.small_string or not self._cpp_available:
            return s.upper()

        if self._cpp_module and hasattr(self._cpp_module, 'str_upper'):
            return self._cpp_module.str_upper(s)
        return s.upper()

    def str_lower(self, s: str) -> str:
        """Optimized lowercase conversion."""
        if len(s) < THRESHOLDS.small_string or not self._cpp_available:
            return s.lower()

        if self._cpp_module and hasattr(self._cpp_module, 'str_lower'):
            return self._cpp_module.str_lower(s)
        return s.lower()

    def str_replace(self, s: str, old: str, new: str) -> str:
        """Optimized string replacement."""
        if len(s) < THRESHOLDS.small_string or not self._cpp_available:
            return s.replace(old, new)

        if self._cpp_module and hasattr(self._cpp_module, 'str_replace'):
            return self._cpp_module.str_replace(s, old, new)
        return s.replace(old, new)

    def str_split(self, s: str, sep: str) -> List[str]:
        """Optimized string split."""
        if len(s) < THRESHOLDS.small_string or not self._cpp_available:
            return s.split(sep)

        if self._cpp_module and hasattr(self._cpp_module, 'str_split'):
            return self._cpp_module.str_split(s, sep)
        return s.split(sep)

    def str_join(self, sep: str, items: List[str]) -> str:
        """Optimized string join."""
        if len(items) < THRESHOLDS.small_loop or not self._cpp_available:
            return sep.join(items)

        if self._cpp_module and hasattr(self._cpp_module, 'str_join'):
            return self._cpp_module.str_join(sep, items)
        return sep.join(items)

    def str_trim(self, s: str) -> str:
        """Optimized string trim."""
        if len(s) < THRESHOLDS.small_string or not self._cpp_available:
            return s.strip()

        if self._cpp_module and hasattr(self._cpp_module, 'str_trim'):
            return self._cpp_module.str_trim(s)
        return s.strip()

    # -------------------------------------------------------------------------
    # Math Operations
    # -------------------------------------------------------------------------

    def math_pow(self, base: float, exp: float) -> float:
        """Optimized power function."""
        if self._cpp_available and self._cpp_module and hasattr(self._cpp_module, 'math_pow'):
            return self._cpp_module.math_pow(base, exp)
        return base ** exp

    def math_clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Optimized clamp function."""
        if self._cpp_available and self._cpp_module and hasattr(self._cpp_module, 'math_clamp'):
            return self._cpp_module.math_clamp(value, min_val, max_val)
        return max(min_val, min(value, max_val))

    # -------------------------------------------------------------------------
    # Tokenization
    # -------------------------------------------------------------------------

    def tokenize(self, source: str) -> List[Any]:
        """Optimized tokenization with smart switching."""
        use_cpp = (
            self._cpp_available and
            len(source) >= THRESHOLDS.small_source and
            self._cpp_module and
            hasattr(self._cpp_module, 'Lexer')
        )

        if use_cpp:
            try:
                lexer = self._cpp_module.Lexer(source)
                return lexer.tokenize()
            except Exception:
                pass

        # Fallback to Python
        from .cssl_parser import CSSLLexer
        lexer = CSSLLexer(source)
        return lexer.tokenize()

    def is_keyword(self, word: str) -> bool:
        """Check if word is a CSSL keyword."""
        if self._cpp_available and self._cpp_module and hasattr(self._cpp_module, 'is_keyword'):
            return self._cpp_module.is_keyword(word)

        from .cssl_parser import KEYWORDS
        return word in KEYWORDS


# Global optimized operations instance
OPS = OptimizedOperations()


# =============================================================================
# Optimized Runtime
# =============================================================================

class OptimizedRuntime:
    """
    Optimized CSSL runtime with:
    - AST caching
    - Smart C++/Python switching
    - Performance monitoring
    """

    def __init__(self):
        self._cache = _AST_CACHE
        self._ops = OPS
        self._execution_times: List[float] = []

    def execute(self, source: str, service_engine=None) -> Any:
        """
        Execute CSSL source with optimizations.

        1. Check AST cache
        2. Choose optimal tokenization
        3. Parse (with caching)
        4. Execute with optimized runtime
        """
        start_time = time.perf_counter()

        # Create execution context
        ctx = ExecutionContext(source)

        # Check cache
        if THRESHOLDS.cache_enabled:
            cached_ast = self._cache.get(source)
            if cached_ast is not None:
                ctx.cached_ast = cached_ast

        # Execute
        try:
            if ctx.cached_ast is not None:
                # Use cached AST
                result = self._execute_ast(ctx.cached_ast, service_engine)
            else:
                # Parse and execute
                result = self._parse_and_execute(source, ctx, service_engine)

            # Record timing
            exec_time = time.perf_counter() - start_time
            self._execution_times.append(exec_time)
            if len(self._execution_times) > 100:
                self._execution_times = self._execution_times[-100:]

            if THRESHOLDS.cache_enabled:
                self._cache.record_execution(source, exec_time)

            return result

        except Exception as e:
            raise

    def _parse_and_execute(self, source: str, ctx: ExecutionContext, service_engine) -> Any:
        """Parse source and execute, with caching."""
        from .cssl_parser import CSSLParser
        from .cssl_runtime import CSSLRuntime

        # Tokenize (with smart switching)
        tokens = self._ops.tokenize(source)
        ctx.token_count = len(tokens)

        # Parse
        parser = CSSLParser(tokens)
        ast = parser.parse()

        # Cache AST
        if THRESHOLDS.cache_enabled:
            self._cache.put(source, ast)

        # Execute
        runtime = CSSLRuntime(service_engine)
        return runtime.execute_ast(ast)

    def _execute_ast(self, ast: Any, service_engine) -> Any:
        """Execute pre-parsed AST."""
        from .cssl_runtime import CSSLRuntime
        runtime = CSSLRuntime(service_engine)
        return runtime.execute_ast(ast)

    @property
    def avg_execution_time(self) -> float:
        """Average execution time in ms."""
        if not self._execution_times:
            return 0.0
        return sum(self._execution_times) / len(self._execution_times) * 1000

    @property
    def cache_stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        return self._cache.stats


# Global optimized runtime
_OPTIMIZED_RUNTIME = OptimizedRuntime()


# =============================================================================
# Public API
# =============================================================================

def run_optimized(source: str, service_engine=None) -> Any:
    """
    Run CSSL with full optimizations.

    This is the recommended way to execute CSSL for best performance:
    - Automatic C++/Python switching based on code size
    - AST caching for repeated execution
    - Optimized string/math operations

    Args:
        source: CSSL source code
        service_engine: Optional service engine for Python interop

    Returns:
        Execution result
    """
    return _OPTIMIZED_RUNTIME.execute(source, service_engine)


def get_optimizer_stats() -> Dict[str, Any]:
    """Get optimizer performance statistics."""
    from . import _CPP_AVAILABLE, _CPP_LOAD_SOURCE

    return {
        'cpp_available': _CPP_AVAILABLE,
        'cpp_source': _CPP_LOAD_SOURCE,
        'cache': _AST_CACHE.stats,
        'avg_exec_time_ms': _OPTIMIZED_RUNTIME.avg_execution_time,
        'thresholds': {
            'small_source': THRESHOLDS.small_source,
            'medium_source': THRESHOLDS.medium_source,
            'large_source': THRESHOLDS.large_source,
            'small_tokens': THRESHOLDS.small_tokens,
            'large_tokens': THRESHOLDS.large_tokens,
        }
    }


def configure_optimizer(
    cache_enabled: bool = None,
    cache_max_size: int = None,
    cache_ttl: float = None,
    small_source: int = None,
    large_source: int = None,
) -> None:
    """
    Configure optimizer settings.

    Args:
        cache_enabled: Enable/disable AST caching
        cache_max_size: Maximum cached ASTs
        cache_ttl: Cache TTL in seconds
        small_source: Threshold for "small" source (use Python)
        large_source: Threshold for "large" source (use C++)
    """
    global THRESHOLDS, _AST_CACHE

    if cache_enabled is not None:
        THRESHOLDS.cache_enabled = cache_enabled
    if cache_max_size is not None:
        THRESHOLDS.cache_max_size = cache_max_size
    if cache_ttl is not None:
        THRESHOLDS.cache_ttl = cache_ttl
    if small_source is not None:
        THRESHOLDS.small_source = small_source
    if large_source is not None:
        THRESHOLDS.large_source = large_source

    # Recreate cache with new settings
    _AST_CACHE = ASTCache(
        max_size=THRESHOLDS.cache_max_size,
        ttl=THRESHOLDS.cache_ttl
    )


def clear_cache() -> None:
    """Clear AST cache."""
    _AST_CACHE.clear()


def get_optimized_ops() -> OptimizedOperations:
    """Get the optimized operations instance."""
    return OPS


# =============================================================================
# Precompiled Patterns
# =============================================================================

class PrecompiledPattern:
    """
    Precompiled CSSL code for maximum performance.

    Use for frequently executed code patterns.
    """

    def __init__(self, source: str):
        self.source = source
        self._ast = None
        self._compile()

    def _compile(self) -> None:
        """Precompile the source to AST."""
        from .cssl_parser import parse_cssl_program
        self._ast = parse_cssl_program(self.source)

    def execute(self, service_engine=None) -> Any:
        """Execute precompiled pattern."""
        from .cssl_runtime import CSSLRuntime
        runtime = CSSLRuntime(service_engine)
        return runtime._execute_ast(self._ast)


def precompile(source: str) -> PrecompiledPattern:
    """
    Precompile CSSL source for repeated execution.

    Use this for code that will be executed many times:

        pattern = precompile('''
            define greet(name) {
                return "Hello " + name;
            }
        ''')

        for name in names:
            result = pattern.execute()

    Args:
        source: CSSL source code

    Returns:
        PrecompiledPattern that can be executed multiple times
    """
    return PrecompiledPattern(source)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    'run_optimized',
    'get_optimizer_stats',
    'configure_optimizer',
    'clear_cache',
    'get_optimized_ops',
    'precompile',
    'PrecompiledPattern',
    'OptimizedOperations',
    'OptimizedRuntime',
    'ASTCache',
    'ExecutionContext',
    'PerformanceThresholds',
    'THRESHOLDS',
    'OPS',
]
