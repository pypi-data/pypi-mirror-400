"""
CSSL Syntax Highlighting

Provides syntax highlighting for CSSL code.
Can be used with:
- PyQt5/6 QSyntaxHighlighter
- VSCode/TextMate grammar export
- Terminal ANSI colors
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto
import re


class TokenCategory(Enum):
    """Categories for syntax highlighting"""
    KEYWORD = auto()          # service-init, struct, define, if, while, etc.
    BUILTIN = auto()          # print, len, typeof, etc.
    OPERATOR = auto()         # <==, ==>, ->, <-, +, -, etc.
    STRING = auto()           # "string" or 'string'
    STRING_INTERP = auto()    # <variable> in strings - NEW
    NUMBER = auto()           # 123, 45.67
    COMMENT = auto()          # # comment or // comment
    MODULE_REF = auto()       # @Module, @VSRAM, @Desktop
    SELF_REF = auto()         # s@StructName, s@Backend.Loop
    IDENTIFIER = auto()       # variable names
    PROPERTY = auto()         # service-name:, service-version:
    BOOLEAN = auto()          # True, False, true, false
    NULL = auto()             # null, None
    PACKAGE_KW = auto()       # package, package-includes - NEW
    TYPE_LITERAL = auto()     # list, dict - NEW
    # v4.1.0: Multi-language support
    SUPPORTS_KW = auto()      # supports keyword (magenta)
    LIBINCLUDE_KW = auto()    # libinclude (yellow/gold)
    LANG_PREFIX = auto()      # Language prefix before $ (cyan): cpp$, py$, java$
    LANG_INSTANCE = auto()    # Instance name after $ (orange): cpp$ClassName


@dataclass
class HighlightRule:
    """Rule for syntax highlighting"""
    pattern: str
    category: TokenCategory
    group: int = 0  # Regex group to highlight


# CSSL Keywords
KEYWORDS = {
    'service-init', 'service-run', 'service-include',
    'struct', 'define', 'main',
    'if', 'else', 'elif', 'while', 'for', 'foreach', 'in', 'range',
    'switch', 'case', 'default', 'break', 'continue', 'return',
    'try', 'catch', 'finally', 'throw',
    'and', 'or', 'not',
    'start', 'stop', 'wait_for', 'on_event', 'emit_event',
    'await',
    # NEW: Extended keywords
    'package', 'package-includes', 'exec', 'as', 'global',
    # v4.1.0: Multi-language support (handled separately for special colors)
    # 'supports', 'libinclude' - see MULTI_LANG_KEYWORDS
}

# v4.1.0: Multi-language keywords with special highlighting
MULTI_LANG_KEYWORDS = {'supports', 'libinclude'}

# v4.1.0: Language identifiers for cross-language instance access
LANGUAGE_IDS = {'cpp', 'py', 'python', 'java', 'csharp', 'js', 'javascript'}

# NEW: Package-related keywords for special highlighting
PACKAGE_KEYWORDS = {'package', 'package-includes'}

# NEW: Type literals
TYPE_LITERALS = {'list', 'dict'}

# CSSL Built-in Functions
BUILTINS = {
    # Output
    'print', 'println', 'debug', 'error', 'warn', 'log',
    # Type conversion
    'int', 'float', 'str', 'bool', 'list', 'dict',
    # Type checking
    'typeof', 'isinstance', 'isint', 'isfloat', 'isstr', 'isbool', 'islist', 'isdict', 'isnull',
    # String
    'len', 'upper', 'lower', 'trim', 'split', 'join', 'replace', 'contains', 'startswith', 'endswith',
    'substr', 'format', 'reverse', 'repeat',
    # List
    'append', 'extend', 'insert', 'remove', 'pop', 'index', 'count', 'sort', 'sorted', 'filter', 'map',
    # Dict
    'keys', 'values', 'items', 'get', 'set', 'has', 'merge', 'delete',
    # Math
    'abs', 'round', 'floor', 'ceil', 'min', 'max', 'sum', 'pow', 'sqrt', 'sin', 'cos', 'tan', 'log10',
    'random', 'randint', 'randrange', 'choice', 'shuffle', 'sample',
    # Time
    'now', 'timestamp', 'sleep', 'date', 'time', 'datetime', 'strftime', 'strptime',
    # File I/O
    'read_file', 'write_file', 'append_file', 'file_exists', 'delete_file',
    'mkdir', 'rmdir', 'listdir', 'getcwd', 'chdir',
    # System
    'exit', 'getenv', 'setenv', 'exec', 'system', 'platform', 'argv',
    # JSON
    'json_encode', 'json_decode', 'json_load', 'json_dump',
    # Regex
    'regex_match', 'regex_search', 'regex_replace', 'regex_split', 'regex_findall',
    # Hash
    'md5', 'sha1', 'sha256', 'sha512', 'hash',
    # Other
    'copy', 'deepcopy', 'assert', 'range', 'enumerate', 'zip', 'any', 'all',
    'include', 'cso_root', 'createcmd', 'wait_for_booted', 'emit', 'on_event'
}


class CSSLSyntaxRules:
    """Collection of syntax highlighting rules for CSSL"""

    @staticmethod
    def get_rules() -> List[HighlightRule]:
        """Get all highlighting rules in priority order"""
        rules = []

        # Comments (highest priority - should match first)
        # NEW: Both # and // style comments
        rules.append(HighlightRule(
            pattern=r'#[^\n]*',
            category=TokenCategory.COMMENT
        ))
        rules.append(HighlightRule(
            pattern=r'//[^\n]*',
            category=TokenCategory.COMMENT
        ))

        # Strings
        rules.append(HighlightRule(
            pattern=r'"(?:[^"\\]|\\.)*"',
            category=TokenCategory.STRING
        ))
        rules.append(HighlightRule(
            pattern=r"'(?:[^'\\]|\\.)*'",
            category=TokenCategory.STRING
        ))

        # NEW: String interpolation <variable> in strings
        rules.append(HighlightRule(
            pattern=r'<[A-Za-z_][A-Za-z0-9_]*>',
            category=TokenCategory.STRING_INTERP
        ))

        # NEW: Package keywords (special highlighting)
        rules.append(HighlightRule(
            pattern=r'\b(package|package-includes)\b',
            category=TokenCategory.PACKAGE_KW
        ))

        # NEW: Type literals (list, dict)
        rules.append(HighlightRule(
            pattern=r'\b(list|dict)\b(?!\s*\()',
            category=TokenCategory.TYPE_LITERAL
        ))

        # v4.1.0: Multi-language support keywords
        # 'supports' keyword (magenta) - must be before regular keywords
        rules.append(HighlightRule(
            pattern=r'\bsupports\b',
            category=TokenCategory.SUPPORTS_KW
        ))

        # 'libinclude' keyword (yellow/gold)
        rules.append(HighlightRule(
            pattern=r'\blibinclude\b',
            category=TokenCategory.LIBINCLUDE_KW
        ))

        # v4.1.0: Language$Instance patterns (cpp$ClassName, py$Object)
        # Match language prefix before $ (cyan)
        rules.append(HighlightRule(
            pattern=r'\b(cpp|py|python|java|csharp|js|javascript)\$',
            category=TokenCategory.LANG_PREFIX,
            group=1
        ))
        # Match instance name after $ (orange)
        rules.append(HighlightRule(
            pattern=r'\b(?:cpp|py|python|java|csharp|js|javascript)\$([A-Za-z_][A-Za-z0-9_]*)',
            category=TokenCategory.LANG_INSTANCE,
            group=1
        ))

        # Self-references (s@Name, s@Backend.Loop)
        rules.append(HighlightRule(
            pattern=r's@[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*',
            category=TokenCategory.SELF_REF
        ))

        # Module references (@Module, @VSRAM.Read)
        rules.append(HighlightRule(
            pattern=r'@[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*',
            category=TokenCategory.MODULE_REF
        ))

        # Properties (key: value in service-init)
        rules.append(HighlightRule(
            pattern=r'\b(service-name|service-version|service-author|service-description|execution|executation)\s*:',
            category=TokenCategory.PROPERTY,
            group=1
        ))

        # Keywords
        keyword_pattern = r'\b(' + '|'.join(re.escape(k) for k in KEYWORDS) + r')\b'
        rules.append(HighlightRule(
            pattern=keyword_pattern,
            category=TokenCategory.KEYWORD
        ))

        # Builtins
        builtin_pattern = r'\b(' + '|'.join(re.escape(b) for b in BUILTINS) + r')\s*\('
        rules.append(HighlightRule(
            pattern=builtin_pattern,
            category=TokenCategory.BUILTIN,
            group=1
        ))

        # Boolean literals
        rules.append(HighlightRule(
            pattern=r'\b(True|False|true|false)\b',
            category=TokenCategory.BOOLEAN
        ))

        # Null literals
        rules.append(HighlightRule(
            pattern=r'\b(null|None|none)\b',
            category=TokenCategory.NULL
        ))

        # Numbers
        rules.append(HighlightRule(
            pattern=r'\b\d+\.?\d*\b',
            category=TokenCategory.NUMBER
        ))

        # Special operators
        rules.append(HighlightRule(
            pattern=r'<==|==>|->|<-',
            category=TokenCategory.OPERATOR
        ))

        # Comparison operators
        rules.append(HighlightRule(
            pattern=r'==|!=|<=|>=|<|>',
            category=TokenCategory.OPERATOR
        ))

        return rules


# Default color schemes
class ColorScheme:
    """Color scheme for syntax highlighting"""

    # CSSL Theme (Orange accent, dark background)
    CSSL_THEME = {
        TokenCategory.KEYWORD: '#508cff',      # Blue
        TokenCategory.BUILTIN: '#ff8c00',      # Orange
        TokenCategory.OPERATOR: '#c8c8d2',     # Light gray
        TokenCategory.STRING: '#50c878',       # Green
        TokenCategory.STRING_INTERP: '#f1fa8c',# Yellow for interpolation - NEW
        TokenCategory.NUMBER: '#f0c040',       # Yellow
        TokenCategory.COMMENT: '#707080',      # Gray
        TokenCategory.MODULE_REF: '#ff8c00',   # Orange
        TokenCategory.SELF_REF: '#60c8dc',     # Cyan
        TokenCategory.IDENTIFIER: '#f0f0f5',   # White
        TokenCategory.PROPERTY: '#c8a8ff',     # Purple
        TokenCategory.BOOLEAN: '#ff8c00',      # Orange
        TokenCategory.NULL: '#ff6464',         # Red
        TokenCategory.PACKAGE_KW: '#bd93f9',   # Purple for package - NEW
        TokenCategory.TYPE_LITERAL: '#8be9fd', # Cyan for type literals - NEW
        # v4.1.0: Multi-language support colors
        TokenCategory.SUPPORTS_KW: '#ff79c6',  # Magenta/Pink for 'supports'
        TokenCategory.LIBINCLUDE_KW: '#f1fa8c',# Yellow/Gold for 'libinclude'
        TokenCategory.LANG_PREFIX: '#8be9fd',  # Cyan for language prefix (cpp$)
        TokenCategory.LANG_INSTANCE: '#ffb86c',# Orange for instance name ($ClassName)
    }

    # Light theme variant
    LIGHT_THEME = {
        TokenCategory.KEYWORD: '#0000ff',      # Blue
        TokenCategory.BUILTIN: '#c65d00',      # Dark orange
        TokenCategory.OPERATOR: '#444444',     # Dark gray
        TokenCategory.STRING: '#008000',       # Green
        TokenCategory.STRING_INTERP: '#b8860b',# DarkGoldenrod for interpolation - NEW
        TokenCategory.NUMBER: '#a06000',       # Brown
        TokenCategory.COMMENT: '#808080',      # Gray
        TokenCategory.MODULE_REF: '#c65d00',   # Dark orange
        TokenCategory.SELF_REF: '#008b8b',     # Dark cyan
        TokenCategory.IDENTIFIER: '#000000',   # Black
        TokenCategory.PROPERTY: '#800080',     # Purple
        TokenCategory.BOOLEAN: '#c65d00',      # Dark orange
        TokenCategory.NULL: '#ff0000',         # Red
        TokenCategory.PACKAGE_KW: '#8b008b',   # DarkMagenta for package - NEW
        TokenCategory.TYPE_LITERAL: '#008b8b', # Dark cyan for type literals - NEW
        # v4.1.0: Multi-language support colors
        TokenCategory.SUPPORTS_KW: '#d63384',  # Dark Magenta for 'supports'
        TokenCategory.LIBINCLUDE_KW: '#b8860b',# DarkGoldenrod for 'libinclude'
        TokenCategory.LANG_PREFIX: '#0d6efd',  # Blue for language prefix (cpp$)
        TokenCategory.LANG_INSTANCE: '#fd7e14',# Orange for instance name ($ClassName)
    }


def highlight_cssl(source: str, scheme: Dict[TokenCategory, str] = None) -> List[Tuple[int, int, str, TokenCategory]]:
    """
    Highlight CSSL source code.

    Args:
        source: CSSL source code
        scheme: Color scheme dict (defaults to CSSL_THEME)

    Returns:
        List of (start, end, color, category) tuples
    """
    if scheme is None:
        scheme = ColorScheme.CSSL_THEME

    highlights = []
    rules = CSSLSyntaxRules.get_rules()

    # Track which positions are already highlighted (for priority)
    highlighted_positions = set()

    for rule in rules:
        try:
            pattern = re.compile(rule.pattern)
            for match in pattern.finditer(source):
                if rule.group > 0 and rule.group <= len(match.groups()):
                    start = match.start(rule.group)
                    end = match.end(rule.group)
                else:
                    start = match.start()
                    end = match.end()

                # Check if position already highlighted
                pos_range = range(start, end)
                if any(p in highlighted_positions for p in pos_range):
                    continue

                # Add highlight
                color = scheme.get(rule.category, '#ffffff')
                highlights.append((start, end, color, rule.category))

                # Mark positions as highlighted
                highlighted_positions.update(pos_range)

        except re.error:
            continue

    # Sort by start position
    highlights.sort(key=lambda h: h[0])

    return highlights


def highlight_cssl_ansi(source: str) -> str:
    """
    Highlight CSSL source with ANSI terminal colors.

    Args:
        source: CSSL source code

    Returns:
        Source with ANSI color codes
    """
    # ANSI color codes
    ANSI_COLORS = {
        TokenCategory.KEYWORD: '\033[94m',      # Blue
        TokenCategory.BUILTIN: '\033[33m',      # Yellow/Orange
        TokenCategory.OPERATOR: '\033[37m',     # White
        TokenCategory.STRING: '\033[92m',       # Green
        TokenCategory.STRING_INTERP: '\033[93m',# Yellow for interpolation - NEW
        TokenCategory.NUMBER: '\033[93m',       # Yellow
        TokenCategory.COMMENT: '\033[90m',      # Gray
        TokenCategory.MODULE_REF: '\033[33m',   # Yellow/Orange
        TokenCategory.SELF_REF: '\033[96m',     # Cyan
        TokenCategory.IDENTIFIER: '\033[0m',    # Default
        TokenCategory.PROPERTY: '\033[95m',     # Magenta
        TokenCategory.BOOLEAN: '\033[33m',      # Yellow/Orange
        TokenCategory.NULL: '\033[91m',         # Red
        TokenCategory.PACKAGE_KW: '\033[95m',   # Magenta for package - NEW
        TokenCategory.TYPE_LITERAL: '\033[96m', # Cyan for type literals - NEW
        # v4.1.0: Multi-language support colors
        TokenCategory.SUPPORTS_KW: '\033[95m',  # Magenta for 'supports'
        TokenCategory.LIBINCLUDE_KW: '\033[93m',# Yellow for 'libinclude'
        TokenCategory.LANG_PREFIX: '\033[96m',  # Cyan for language prefix (cpp$)
        TokenCategory.LANG_INSTANCE: '\033[33m',# Orange/Yellow for instance name
    }
    RESET = '\033[0m'

    highlights = highlight_cssl(source, ColorScheme.CSSL_THEME)

    # Build highlighted string
    result = []
    last_end = 0

    for start, end, color, category in highlights:
        # Add unhighlighted text before this highlight
        if start > last_end:
            result.append(source[last_end:start])

        # Add highlighted text
        ansi_color = ANSI_COLORS.get(category, '')
        result.append(f"{ansi_color}{source[start:end]}{RESET}")
        last_end = end

    # Add remaining text
    if last_end < len(source):
        result.append(source[last_end:])

    return ''.join(result)


# PyQt5/6 Syntax Highlighter
def get_pyqt_highlighter():
    """
    Get a QSyntaxHighlighter class for CSSL.

    Returns:
        CSSLHighlighter class (requires PyQt5 or PyQt6)
    """
    try:
        from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
        from PyQt5.QtCore import QRegularExpression
    except ImportError:
        try:
            from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
            from PyQt6.QtCore import QRegularExpression
        except ImportError:
            return None

    class CSSLHighlighter(QSyntaxHighlighter):
        """Syntax highlighter for CSSL code in Qt editors"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self._rules = []
            self._setup_rules()

        def _setup_rules(self):
            """Setup highlighting rules"""
            scheme = ColorScheme.CSSL_THEME

            for rule in CSSLSyntaxRules.get_rules():
                fmt = QTextCharFormat()
                color = QColor(scheme.get(rule.category, '#ffffff'))
                fmt.setForeground(color)

                # Bold for keywords and builtins
                if rule.category in (TokenCategory.KEYWORD, TokenCategory.BUILTIN):
                    fmt.setFontWeight(QFont.Bold)

                # Italic for comments
                if rule.category == TokenCategory.COMMENT:
                    fmt.setFontItalic(True)

                self._rules.append((QRegularExpression(rule.pattern), fmt, rule.group))

        def highlightBlock(self, text):
            """Apply highlighting to a block of text"""
            for pattern, fmt, group in self._rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    if group > 0 and group <= match.lastCapturedIndex():
                        start = match.capturedStart(group)
                        length = match.capturedLength(group)
                    else:
                        start = match.capturedStart()
                        length = match.capturedLength()
                    self.setFormat(start, length, fmt)

    return CSSLHighlighter


# Export for external editors (TextMate/VSCode grammar format)
def export_textmate_grammar() -> dict:
    """
    Export CSSL syntax as TextMate grammar for VSCode.

    Returns:
        Dictionary suitable for JSON export as .tmLanguage.json
    """
    return {
        "scopeName": "source.cssl",
        "name": "CSSL",
        "fileTypes": ["cssl", "service"],
        "patterns": [
            {
                "name": "comment.line.cssl",
                "match": "#.*$"
            },
            {
                "name": "comment.line.double-slash.cssl",
                "match": "//.*$"
            },
            {
                "name": "string.quoted.double.cssl",
                "match": '"(?:[^"\\\\]|\\\\.)*"'
            },
            {
                "name": "string.quoted.single.cssl",
                "match": "'(?:[^'\\\\]|\\\\.)*'"
            },
            # v4.1.0: Multi-language support
            {
                "name": "keyword.control.supports.cssl",
                "match": "\\bsupports\\b"
            },
            {
                "name": "support.function.libinclude.cssl",
                "match": "\\blibinclude\\b"
            },
            {
                "name": "variable.language.lang-instance.cssl",
                "match": "\\b(cpp|py|python|java|csharp|js|javascript)\\$([A-Za-z_][A-Za-z0-9_]*)",
                "captures": {
                    "1": {"name": "entity.name.type.language.cssl"},
                    "2": {"name": "variable.other.instance.cssl"}
                }
            },
            {
                "name": "variable.other.self-reference.cssl",
                "match": "s@[A-Za-z_][A-Za-z0-9_]*(?:\\.[A-Za-z_][A-Za-z0-9_]*)*"
            },
            {
                "name": "variable.other.module-reference.cssl",
                "match": "@[A-Za-z_][A-Za-z0-9_]*(?:\\.[A-Za-z_][A-Za-z0-9_]*)*"
            },
            {
                "name": "keyword.other.package.cssl",
                "match": "\\b(package|package-includes)\\b"
            },
            {
                "name": "keyword.control.cssl",
                "match": "\\b(service-init|service-run|service-include|struct|define|class|constr|if|else|elif|while|for|foreach|in|switch|case|default|break|continue|return|try|catch|finally|throw|await|extends|overwrites|global|as|exec)\\b"
            },
            {
                "name": "keyword.operator.cssl",
                "match": "\\b(and|or|not)\\b"
            },
            {
                "name": "constant.language.cssl",
                "match": "\\b(True|False|true|false|null|None|none)\\b"
            },
            {
                "name": "constant.numeric.cssl",
                "match": "\\b\\d+\\.?\\d*\\b"
            },
            {
                "name": "keyword.operator.assignment.cssl",
                "match": "<==|==>|->|<-|::"
            },
            {
                "name": "support.type.cssl",
                "match": "\\b(list|dict)\\b(?!\\s*\\()"
            }
        ]
    }


# Export public API
__all__ = [
    'TokenCategory', 'HighlightRule', 'CSSLSyntaxRules', 'ColorScheme',
    'highlight_cssl', 'highlight_cssl_ansi', 'get_pyqt_highlighter',
    'export_textmate_grammar', 'KEYWORDS', 'BUILTINS',
    'PACKAGE_KEYWORDS', 'TYPE_LITERALS'  # NEW
]
