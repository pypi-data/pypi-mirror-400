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
"""

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

__all__ = [
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
