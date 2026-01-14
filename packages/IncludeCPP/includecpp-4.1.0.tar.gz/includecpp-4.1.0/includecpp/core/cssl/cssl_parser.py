"""
CSSL Parser - Lexer and Parser for CSSL Language

Features:
- Complete tokenization of CSSL syntax
- AST (Abstract Syntax Tree) generation
- Enhanced error reporting with line/column info
- Support for service files and standalone programs
- Special operators: <== (inject), ==> (receive), -> <- (flow)
- Module references (@Module) and self-references (s@Struct)
"""

import re
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


class CSSLSyntaxError(Exception):
    """Syntax error with detailed location information"""

    def __init__(self, message: str, line: int = 0, column: int = 0, source_line: str = ""):
        self.line = line
        self.column = column
        self.source_line = source_line

        # Build detailed error message
        location = f" at line {line}" if line else ""
        if column:
            location += f", column {column}"

        full_message = f"CSSL Syntax Error{location}: {message}"

        if source_line:
            full_message += f"\n  {source_line}"
            if column > 0:
                full_message += f"\n  {' ' * (column - 1)}^"

        super().__init__(full_message)


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    STRING = auto()
    STRING_INTERP = auto()  # <variable> in strings
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    TYPE_LITERAL = auto()  # list, dict as type literals
    TYPE_GENERIC = auto()  # datastruct<T>, shuffled<T>, iterator<T>, combo<T>
    OPERATOR = auto()
    # Basic injection operators
    INJECT_LEFT = auto()        # <==
    INJECT_RIGHT = auto()       # ==>
    # BruteForce Injection operators - Copy & Add
    INJECT_PLUS_LEFT = auto()   # +<==
    INJECT_PLUS_RIGHT = auto()  # ==>+
    # BruteForce Injection operators - Move & Remove
    INJECT_MINUS_LEFT = auto()  # -<==
    INJECT_MINUS_RIGHT = auto() # ===>-
    # BruteForce Injection operators - Code Infusion
    INFUSE_LEFT = auto()        # <<==
    INFUSE_RIGHT = auto()       # ==>>
    INFUSE_PLUS_LEFT = auto()   # +<<==
    INFUSE_PLUS_RIGHT = auto()  # ==>>+
    INFUSE_MINUS_LEFT = auto()  # -<<==
    INFUSE_MINUS_RIGHT = auto() # ==>>-
    # Flow operators
    FLOW_RIGHT = auto()
    FLOW_LEFT = auto()
    EQUALS = auto()
    COMPARE_EQ = auto()
    COMPARE_NE = auto()
    COMPARE_LT = auto()
    COMPARE_GT = auto()
    COMPARE_LE = auto()
    COMPARE_GE = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    AMPERSAND = auto()  # & for references
    BLOCK_START = auto()
    BLOCK_END = auto()
    PAREN_START = auto()
    PAREN_END = auto()
    BRACKET_START = auto()
    BRACKET_END = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOUBLE_COLON = auto()  # :: for injection helpers (string::where, json::key, etc)
    COMMA = auto()
    DOT = auto()
    AT = auto()
    GLOBAL_REF = auto()  # r@<name> global variable declaration
    SELF_REF = auto()    # s@<name> self-reference to global struct
    SHARED_REF = auto()  # $<name> shared object reference
    CAPTURED_REF = auto()  # %<name> captured reference (for infusion)
    THIS_REF = auto()      # this-><name> class member reference
    PACKAGE = auto()
    PACKAGE_INCLUDES = auto()
    AS = auto()
    COMMENT = auto()
    NEWLINE = auto()
    EOF = auto()
    # Super-functions for .cssl-pl payload files (v3.8.0)
    SUPER_FUNC = auto()    # #$run(), #$exec(), #$printl() - pre-execution hooks
    # Append operator for constructor/function extension
    PLUS_PLUS = auto()     # ++ for constructor/function append (keeps old + adds new)
    MINUS_MINUS = auto()   # -- for potential future use
    # Multi-language support (v4.1.0)
    LANG_INSTANCE_REF = auto()  # cpp$InstanceName, py$Object - cross-language instance access


KEYWORDS = {
    # Service structure
    'service-init', 'service-run', 'service-include', 'struct', 'define', 'main', 'class', 'constr', 'extends', 'overwrites', 'new', 'this', 'super',
    # Control flow
    'if', 'else', 'elif', 'while', 'for', 'foreach', 'in', 'range',
    'switch', 'case', 'default', 'break', 'continue', 'return',
    'try', 'catch', 'finally', 'throw',
    # Literals
    'True', 'False', 'null', 'None', 'true', 'false',
    # Logical operators
    'and', 'or', 'not',
    # Async/Events
    'start', 'stop', 'wait_for', 'on_event', 'emit_event', 'await',
    # Package system
    'package', 'package-includes', 'exec', 'as', 'global',
    # CSSL Type Keywords
    'int', 'string', 'float', 'bool', 'void', 'json', 'array', 'vector', 'stack',
    'list', 'dictionary', 'dict', 'instance', 'map',  # Python-like types
    'dynamic',      # No type declaration (slow but flexible)
    'undefined',    # Function errors ignored
    'open',         # Accept any parameter type
    'datastruct',   # Universal container (lazy declarator)
    'dataspace',    # SQL/data storage container
    'shuffled',     # Unorganized fast storage (multiple returns)
    'iterator',     # Advanced iterator with tasks
    'combo',        # Filter/search spaces
    'structure',    # Advanced C++/Py Class
    'openquote',    # SQL openquote container
    # CSSL Function Modifiers
    'const',        # Immutable function (like C++)
    'meta',         # Source function (must return)
    'super',        # Force execution (no exceptions)
    'closed',       # Protect from external injection
    'private',      # Disable all injections
    'virtual',      # Import cycle safe
    'sqlbased',     # SQL-based function
    'public',       # Explicitly public (default)
    'static',       # Static method/function
    # CSSL Include Keywords
    'include', 'get',
    # Multi-language support (v4.1.0)
    'supports', 'libinclude',
}

# Function modifiers that can appear in any order before function name
FUNCTION_MODIFIERS = {
    'undefined', 'open', 'meta', 'super', 'closed', 'private', 'virtual',
    'sqlbased', 'const', 'public', 'static', 'global', 'shuffled'
}

# Type literals that create empty instances
TYPE_LITERALS = {'list', 'dict'}

# Generic type keywords that use <T> syntax
TYPE_GENERICS = {
    'datastruct', 'dataspace', 'shuffled', 'iterator', 'combo',
    'vector', 'stack', 'array', 'openquote', 'list', 'dictionary', 'map'
}

# Functions that accept type parameters: FuncName<type>(args)
TYPE_PARAM_FUNCTIONS = {
    'OpenFind'  # OpenFind<string>(0)
}

# Injection helper prefixes (type::helper=value)
INJECTION_HELPERS = {
    'string', 'integer', 'json', 'array', 'vector', 'combo', 'dynamic', 'sql'
}

# Language identifiers for multi-language support (v4.1.0)
# Used in lang$instance patterns like cpp$MyClass, py$Object
LANGUAGE_IDS = {
    'cpp', 'py', 'python', 'java', 'csharp', 'js', 'javascript'
}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


class CSSLLexer:
    """Tokenizes CSSL source code into a stream of tokens."""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        # Store source lines for error messages
        self.source_lines = source.split('\n')

    def get_source_line(self, line_num: int) -> str:
        """Get a specific source line for error reporting"""
        if 0 < line_num <= len(self.source_lines):
            return self.source_lines[line_num - 1]
        return ""

    def error(self, message: str):
        """Raise a syntax error with location info"""
        raise CSSLSyntaxError(
            message,
            line=self.line,
            column=self.column,
            source_line=self.get_source_line(self.line)
        )

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break

            char = self.source[self.pos]

            # Super-functions (#$) or Comments (# and // style)
            if char == '#':
                if self._peek(1) == '$':
                    # Super-function: #$run(), #$exec(), #$printl()
                    self._read_super_function()
                else:
                    # Regular comment
                    self._skip_comment()
            elif char == '/' and self._peek(1) == '/':
                # C-style // comment - NEW
                self._skip_comment()
            elif char == '\n':
                self._add_token(TokenType.NEWLINE, '\n')
                self._advance()
                self.line += 1
                self.column = 1
            elif char in '"\'':
                self._read_string(char)
            elif char == '`':
                # Raw string (no escape processing) - useful for JSON
                self._read_raw_string()
            elif char.isdigit() or (char == '-' and self._peek(1).isdigit()):
                self._read_number()
            elif char == 'r' and self._peek(1) == '@':
                # r@<name> global variable declaration (same as 'global')
                self._read_global_ref()
            elif char == 's' and self._peek(1) == '@':
                # s@<name> self-reference to global struct
                self._read_self_ref()
            elif char.isalpha() or char == '_':
                self._read_identifier()
            elif char == '@':
                self._add_token(TokenType.AT, '@')
                self._advance()
            elif char == '$':
                # $<name> shared object reference
                self._read_shared_ref()
            elif char == '%':
                # Check if this is %<name> captured reference or % modulo operator
                next_char = self._peek(1)
                if next_char and (next_char.isalpha() or next_char == '_'):
                    # %<name> captured reference (for infusion)
                    self._read_captured_ref()
                else:
                    # % modulo operator
                    self._add_token(TokenType.MODULO, '%')
                    self._advance()
            elif char == '&':
                # & for references
                if self._peek(1) == '&':
                    self._add_token(TokenType.AND, '&&')
                    self._advance()
                    self._advance()
                else:
                    self._add_token(TokenType.AMPERSAND, '&')
                    self._advance()
            elif char == '{':
                self._add_token(TokenType.BLOCK_START, '{')
                self._advance()
            elif char == '}':
                self._add_token(TokenType.BLOCK_END, '}')
                self._advance()
            elif char == '(':
                self._add_token(TokenType.PAREN_START, '(')
                self._advance()
            elif char == ')':
                self._add_token(TokenType.PAREN_END, ')')
                self._advance()
            elif char == '[':
                self._add_token(TokenType.BRACKET_START, '[')
                self._advance()
            elif char == ']':
                self._add_token(TokenType.BRACKET_END, ']')
                self._advance()
            elif char == ';':
                self._add_token(TokenType.SEMICOLON, ';')
                self._advance()
            elif char == ':':
                # Check for :: (double colon for injection helpers)
                if self._peek(1) == ':':
                    self._add_token(TokenType.DOUBLE_COLON, '::')
                    self._advance()
                    self._advance()
                else:
                    self._add_token(TokenType.COLON, ':')
                    self._advance()
            elif char == ',':
                self._add_token(TokenType.COMMA, ',')
                self._advance()
            elif char == '.':
                self._add_token(TokenType.DOT, '.')
                self._advance()
            elif char == '+':
                # Check for ++ (append operator for constructor/function extension)
                if self._peek(1) == '+':
                    self._add_token(TokenType.PLUS_PLUS, '++')
                    self._advance()
                    self._advance()
                # Check for BruteForce Injection: +<== or +<<==
                elif self._peek(1) == '<' and self._peek(2) == '<' and self._peek(3) == '=' and self._peek(4) == '=':
                    self._add_token(TokenType.INFUSE_PLUS_LEFT, '+<<==')
                    for _ in range(5): self._advance()
                elif self._peek(1) == '<' and self._peek(2) == '=' and self._peek(3) == '=':
                    self._add_token(TokenType.INJECT_PLUS_LEFT, '+<==')
                    for _ in range(4): self._advance()
                else:
                    self._add_token(TokenType.PLUS, '+')
                    self._advance()
            elif char == '*':
                self._add_token(TokenType.MULTIPLY, '*')
                self._advance()
            elif char == '/':
                # Check if this is a // comment (handled above) or division
                if self._peek(1) != '/':
                    self._add_token(TokenType.DIVIDE, '/')
                    self._advance()
                else:
                    # Already handled by // comment check above, but just in case
                    self._skip_comment()
            elif char == '<':
                self._read_less_than()
            elif char == '>':
                self._read_greater_than()
            elif char == '=':
                self._read_equals()
            elif char == '!':
                self._read_not()
            elif char == '-':
                self._read_minus()
            elif char == '|':
                if self._peek(1) == '|':
                    self._add_token(TokenType.OR, '||')
                    self._advance()
                    self._advance()
                else:
                    self._advance()
            else:
                self._advance()

        self._add_token(TokenType.EOF, '')
        return self.tokens

    def _advance(self):
        self.pos += 1
        self.column += 1

    def _peek(self, offset=0) -> str:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return ''

    def _add_token(self, token_type: TokenType, value: Any):
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self._advance()

    def _skip_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self._advance()

    def _read_string(self, quote_char: str):
        self._advance()
        start = self.pos
        result = []
        while self.pos < len(self.source) and self.source[self.pos] != quote_char:
            if self.source[self.pos] == '\\' and self.pos + 1 < len(self.source):
                # Handle escape sequences
                next_char = self.source[self.pos + 1]
                if next_char == 'n':
                    result.append('\n')
                elif next_char == 't':
                    result.append('\t')
                elif next_char == 'r':
                    result.append('\r')
                elif next_char == '\\':
                    result.append('\\')
                elif next_char == quote_char:
                    result.append(quote_char)
                elif next_char == '"':
                    result.append('"')
                elif next_char == "'":
                    result.append("'")
                else:
                    result.append(self.source[self.pos])
                    result.append(next_char)
                self._advance()
                self._advance()
            else:
                result.append(self.source[self.pos])
                self._advance()
        value = ''.join(result)
        self._add_token(TokenType.STRING, value)
        self._advance()

    def _read_raw_string(self):
        """Read raw string with backticks - no escape processing.

        Useful for JSON: `{"id": "2819e1", "name": "test"}`
        """
        self._advance()  # Skip opening backtick
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != '`':
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 0
            self._advance()
        value = self.source[start:self.pos]
        self._add_token(TokenType.STRING, value)
        self._advance()  # Skip closing backtick

    def _read_number(self):
        start = self.pos
        if self.source[self.pos] == '-':
            self._advance()
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            self._advance()
        value = self.source[start:self.pos]
        if '.' in value:
            self._add_token(TokenType.NUMBER, float(value))
        else:
            self._add_token(TokenType.NUMBER, int(value))

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()
        value = self.source[start:self.pos]

        # Check for language$instance pattern (v4.1.0)
        # e.g., cpp$MyClass, py$Object, java$Service
        if value.lower() in LANGUAGE_IDS and self.pos < len(self.source) and self.source[self.pos] == '$':
            lang_id = value
            self._advance()  # skip '$'
            # Read instance name
            instance_start = self.pos
            while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                self._advance()
            instance_name = self.source[instance_start:self.pos]
            if instance_name:
                self._add_token(TokenType.LANG_INSTANCE_REF, {'lang': lang_id, 'instance': instance_name})
                return
            # If no instance name, revert and treat as normal identifier
            self.pos = start
            while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                self._advance()
            value = self.source[start:self.pos]

        if value in ('True', 'true'):
            self._add_token(TokenType.BOOLEAN, True)
        elif value in ('False', 'false'):
            self._add_token(TokenType.BOOLEAN, False)
        elif value in ('null', 'None', 'none'):
            self._add_token(TokenType.NULL, None)
        elif value in TYPE_LITERALS:
            # NEW: list and dict as type literals (e.g., cache = list;)
            self._add_token(TokenType.TYPE_LITERAL, value)
        elif value == 'as':
            # NEW: 'as' keyword for foreach ... as ... syntax
            self._add_token(TokenType.AS, value)
        elif value in KEYWORDS:
            self._add_token(TokenType.KEYWORD, value)
        else:
            self._add_token(TokenType.IDENTIFIER, value)

    def _read_super_function(self):
        """Read #$<name>(...) super-function call for .cssl-pl payloads.

        Super-functions are pre-execution hooks that run when a payload is loaded.
        Valid super-functions: #$run(), #$exec(), #$printl()

        Syntax:
            #$run(initFunction);        // Call a function at load time
            #$exec(setup());            // Execute expression at load time
            #$printl("Payload loaded"); // Print at load time
        """
        start = self.pos
        self._advance()  # skip '#'
        self._advance()  # skip '$'

        # Read the super-function name (run, exec, printl, etc.)
        name_start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()
        func_name = self.source[name_start:self.pos]

        # Store as #$<name> token value
        value = f'#${func_name}'
        self._add_token(TokenType.SUPER_FUNC, value)

    def _read_self_ref(self):
        """Read s@<name> or s@<name>.<member>... self-reference"""
        start = self.pos
        self._advance()  # skip 's'
        self._advance()  # skip '@'

        # Read the identifier path (Name.Member.SubMember)
        path_parts = []
        while self.pos < len(self.source):
            # Read identifier part
            part_start = self.pos
            while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                self._advance()
            if self.pos > part_start:
                path_parts.append(self.source[part_start:self.pos])

            # Check for dot to continue path
            if self.pos < len(self.source) and self.source[self.pos] == '.':
                self._advance()  # skip '.'
            else:
                break

        value = '.'.join(path_parts)
        self._add_token(TokenType.SELF_REF, value)

    def _read_global_ref(self):
        """Read r@<name> global variable declaration (equivalent to 'global')"""
        start = self.pos
        self._advance()  # skip 'r'
        self._advance()  # skip '@'

        # Read the identifier
        name_start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()

        value = self.source[name_start:self.pos]
        self._add_token(TokenType.GLOBAL_REF, value)

    def _read_shared_ref(self):
        """Read $<name> shared object reference"""
        self._advance()  # skip '$'

        # Read the identifier (shared object name)
        name_start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()

        value = self.source[name_start:self.pos]
        if not value:
            self.error("Expected identifier after '$'")
        self._add_token(TokenType.SHARED_REF, value)

    def _read_captured_ref(self):
        """Read %<name> captured reference (captures value at definition time for infusions)"""
        self._advance()  # skip '%'

        # Read the identifier (captured reference name)
        name_start = self.pos
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self._advance()

        value = self.source[name_start:self.pos]
        if not value:
            self.error("Expected identifier after '%'")
        self._add_token(TokenType.CAPTURED_REF, value)

    def _read_less_than(self):
        # Check for <<== (code infusion left)
        if self._peek(1) == '<' and self._peek(2) == '=' and self._peek(3) == '=':
            self._add_token(TokenType.INFUSE_LEFT, '<<==')
            for _ in range(4): self._advance()
        # Check for <== (basic injection left)
        elif self._peek(1) == '=' and self._peek(2) == '=':
            self._add_token(TokenType.INJECT_LEFT, '<==')
            for _ in range(3): self._advance()
        elif self._peek(1) == '=':
            self._add_token(TokenType.COMPARE_LE, '<=')
            self._advance()
            self._advance()
        elif self._peek(1) == '-':
            self._add_token(TokenType.FLOW_LEFT, '<-')
            self._advance()
            self._advance()
        else:
            self._add_token(TokenType.COMPARE_LT, '<')
            self._advance()

    def _read_greater_than(self):
        if self._peek(1) == '=':
            self._add_token(TokenType.COMPARE_GE, '>=')
            self._advance()
            self._advance()
        else:
            self._add_token(TokenType.COMPARE_GT, '>')
            self._advance()

    def _read_equals(self):
        # Check for ==>>+ (code infusion right plus)
        if self._peek(1) == '=' and self._peek(2) == '>' and self._peek(3) == '>' and self._peek(4) == '+':
            self._add_token(TokenType.INFUSE_PLUS_RIGHT, '==>>+')
            for _ in range(5): self._advance()
        # Check for ==>>- (code infusion right minus)
        elif self._peek(1) == '=' and self._peek(2) == '>' and self._peek(3) == '>' and self._peek(4) == '-':
            self._add_token(TokenType.INFUSE_MINUS_RIGHT, '==>>-')
            for _ in range(5): self._advance()
        # Check for ==>> (code infusion right)
        elif self._peek(1) == '=' and self._peek(2) == '>' and self._peek(3) == '>':
            self._add_token(TokenType.INFUSE_RIGHT, '==>>')
            for _ in range(4): self._advance()
        # Check for ==>+ (injection right plus)
        elif self._peek(1) == '=' and self._peek(2) == '>' and self._peek(3) == '+':
            self._add_token(TokenType.INJECT_PLUS_RIGHT, '==>+')
            for _ in range(4): self._advance()
        # Check for ==>- (injection right minus - moves & removes)
        elif self._peek(1) == '=' and self._peek(2) == '>' and self._peek(3) == '-':
            self._add_token(TokenType.INJECT_MINUS_RIGHT, '==>-')
            for _ in range(4): self._advance()
        # Check for ==> (basic injection right)
        elif self._peek(1) == '=' and self._peek(2) == '>':
            self._add_token(TokenType.INJECT_RIGHT, '==>')
            for _ in range(3): self._advance()
        elif self._peek(1) == '=':
            self._add_token(TokenType.COMPARE_EQ, '==')
            self._advance()
            self._advance()
        else:
            self._add_token(TokenType.EQUALS, '=')
            self._advance()

    def _read_not(self):
        if self._peek(1) == '=':
            self._add_token(TokenType.COMPARE_NE, '!=')
            self._advance()
            self._advance()
        else:
            self._add_token(TokenType.NOT, '!')
            self._advance()

    def _read_minus(self):
        # Check for -<<== (code infusion minus left)
        if self._peek(1) == '<' and self._peek(2) == '<' and self._peek(3) == '=' and self._peek(4) == '=':
            self._add_token(TokenType.INFUSE_MINUS_LEFT, '-<<==')
            for _ in range(5): self._advance()
        # Check for -<== (injection minus left - move & remove)
        elif self._peek(1) == '<' and self._peek(2) == '=' and self._peek(3) == '=':
            self._add_token(TokenType.INJECT_MINUS_LEFT, '-<==')
            for _ in range(4): self._advance()
        # Check for -==> (injection right minus)
        elif self._peek(1) == '=' and self._peek(2) == '=' and self._peek(3) == '>':
            self._add_token(TokenType.INJECT_MINUS_RIGHT, '-==>')
            for _ in range(4): self._advance()
        elif self._peek(1) == '>':
            self._add_token(TokenType.FLOW_RIGHT, '->')
            self._advance()
            self._advance()
        else:
            self._add_token(TokenType.MINUS, '-')
            self._advance()


@dataclass
class ASTNode:
    type: str
    value: Any = None
    children: List['ASTNode'] = field(default_factory=list)
    line: int = 0
    column: int = 0


class CSSLParser:
    """Parses CSSL tokens into an Abstract Syntax Tree."""

    def __init__(self, tokens: List[Token], source_lines: List[str] = None):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.pos = 0
        self.source_lines = source_lines or []

    def get_source_line(self, line_num: int) -> str:
        """Get a specific source line for error reporting"""
        if 0 < line_num <= len(self.source_lines):
            return self.source_lines[line_num - 1]
        return ""

    def error(self, message: str, token: Token = None):
        """Raise a syntax error with location info"""
        if token is None:
            token = self._current()
        raise CSSLSyntaxError(
            message,
            line=token.line,
            column=token.column,
            source_line=self.get_source_line(token.line)
        )

    def parse(self) -> ASTNode:
        """Parse a service file (wrapped in braces)"""
        root = ASTNode('service', children=[])

        if not self._match(TokenType.BLOCK_START):
            self.error(f"Expected '{{' at start of service, got {self._current().type.name}")

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._match_keyword('service-init'):
                root.children.append(self._parse_service_init())
            elif self._match_keyword('service-include'):
                root.children.append(self._parse_service_include())
            elif self._match_keyword('service-run'):
                root.children.append(self._parse_service_run())
            # NEW: package block support
            elif self._match_keyword('package'):
                root.children.append(self._parse_package())
            # NEW: package-includes block support
            elif self._match_keyword('package-includes'):
                root.children.append(self._parse_package_includes())
            # NEW: struct at top level
            elif self._match_keyword('struct'):
                root.children.append(self._parse_struct())
            # NEW: define at top level
            elif self._match_keyword('define'):
                root.children.append(self._parse_define())
            else:
                self._advance()

        self._match(TokenType.BLOCK_END)
        return root

    def _is_function_modifier(self, value: str) -> bool:
        """Check if a keyword is a function modifier"""
        return value in FUNCTION_MODIFIERS

    def _is_type_keyword(self, value: str) -> bool:
        """Check if a keyword is a type declaration"""
        return value in ('int', 'string', 'float', 'bool', 'void', 'json', 'array', 'vector', 'stack',
                        'list', 'dictionary', 'dict', 'instance', 'map', 'openquote', 'parameter',
                        'dynamic', 'datastruct', 'dataspace', 'shuffled', 'iterator', 'combo', 'structure')

    def _looks_like_function_declaration(self) -> bool:
        """Check if current position looks like a C-style function declaration.

        Supports flexible ordering of modifiers, types, non-null (*), and global (@):

        Patterns:
        - int funcName(...)
        - undefined int funcName(...)
        - vector<string> funcName(...)
        - undefined void funcName(...)
        - private super virtual meta FuncName(...)
        - private string *@Myfunc(...)
        - const define myFunc(...)
        - global private const void @Func(...)
        - shuffled *[string] getNumbers(...)
        - datastruct<dynamic> HelloCode(...)
        - datastruct<dynamic> HelloCode() : extends @MyFunc { }

        Distinguishes functions from variables:
        - datastruct<dynamic> MyVar;           <- variable (no () { })
        - datastruct<dynamic> HelloCode() { }  <- function (has () { })
        """
        saved_pos = self.pos
        has_modifiers = False
        has_type = False

        try:
            # Skip modifiers in any order (global, private, const, undefined, etc.)
            while self._check(TokenType.KEYWORD) and self._is_function_modifier(self._current().value):
                self._advance()
                has_modifiers = True

            # Check for 'define' keyword (special case: const define myFunc())
            if self._check(TokenType.KEYWORD) and self._current().value == 'define':
                self.pos = saved_pos
                return False  # Let _parse_define handle this

            # Check for type keyword (int, string, void, vector, datastruct, etc.)
            if self._check(TokenType.KEYWORD) and self._is_type_keyword(self._current().value):
                self._advance()
                has_type = True

                # Skip generic type parameters <T> or <T, U>
                if self._check(TokenType.COMPARE_LT):
                    depth = 1
                    self._advance()
                    while depth > 0 and not self._is_at_end():
                        if self._check(TokenType.COMPARE_LT):
                            depth += 1
                        elif self._check(TokenType.COMPARE_GT):
                            depth -= 1
                        self._advance()

            # Check for * prefix (non-null) or *[type] (type exclusion)
            if self._check(TokenType.MULTIPLY):
                self._advance()
                # Check for type exclusion: *[string], *[int], etc.
                if self._check(TokenType.BRACKET_START):
                    self._advance()  # [
                    while not self._check(TokenType.BRACKET_END) and not self._is_at_end():
                        self._advance()
                    if self._check(TokenType.BRACKET_END):
                        self._advance()  # ]

            # Check for @ prefix (global function)
            if self._check(TokenType.AT):
                self._advance()

            # Now we should be at the function name (identifier)
            if self._check(TokenType.IDENTIFIER):
                self._advance()

                # Check if followed by (
                # IMPORTANT: Only a function declaration if we have modifiers OR type
                # Plain identifier() is a function CALL, not a declaration
                if self._check(TokenType.PAREN_START):
                    if has_modifiers or has_type:
                        self.pos = saved_pos
                        return True
                    else:
                        # No modifiers/type = function call, not declaration
                        self.pos = saved_pos
                        return False

                # If we have a type and identifier but no (, it's a variable
                if has_type and not self._check(TokenType.PAREN_START):
                    self.pos = saved_pos
                    return False

            self.pos = saved_pos
            return False

        except Exception:
            self.pos = saved_pos
            return False

    def _looks_like_typed_variable(self) -> bool:
        """Check if current position looks like a typed variable declaration.

        Patterns:
        - int x;
        - stack<string> myStack;
        - vector<int> nums = [1,2,3];

        Distinguishes from function declarations by checking for '(' after identifier.
        """
        saved_pos = self.pos

        # Check for type keyword
        if self._check(TokenType.KEYWORD) and self._is_type_keyword(self._current().value):
            self._advance()

            # Skip generic type parameters <T>
            if self._check(TokenType.COMPARE_LT):
                depth = 1
                self._advance()
                while depth > 0 and not self._is_at_end():
                    if self._check(TokenType.COMPARE_LT):
                        depth += 1
                    elif self._check(TokenType.COMPARE_GT):
                        depth -= 1
                    self._advance()

            # Check for identifier NOT followed by ( (that would be a function)
            if self._check(TokenType.IDENTIFIER):
                self._advance()
                # If followed by '(' it's a function, not a variable
                is_var = not self._check(TokenType.PAREN_START)
                self.pos = saved_pos
                return is_var

        self.pos = saved_pos
        return False

    def _parse_typed_function(self, is_global: bool = False) -> ASTNode:
        """Parse C-style typed function declaration with flexible modifier ordering.

        Supports any order of modifiers, types, non-null (*), and global (@):

        Patterns:
        - int Add(int a, int b) { }
        - global int Add(int a, int b) { }
        - int @Add(int a, int b) { }
        - undefined int Func() { }
        - open void Handler(open Params) { }
        - vector<string> GetNames() { }
        - private string *@Myfunc() { }
        - const define myFunc() { }
        - global private const void @Func() { }
        - shuffled *[string] getNumbers() { }
        - datastruct<dynamic> HelloCode() { }
        - meta datastruct<string> MyData() { }  // meta allows any returns
        - datastruct<dynamic> HelloCode() : extends @MyFunc { }

        Typed functions (with return type like int, string, void) MUST return that type.
        Functions with 'meta' modifier can return any type regardless of declaration.
        Functions with 'define' are dynamic (any return type allowed).
        """
        modifiers = []
        return_type = None
        generic_type = None
        non_null = False
        exclude_type = None
        is_const = False

        # Phase 1: Collect all modifiers, type, non-null, and global indicators
        # These can appear in any order before the function name

        parsing_prefix = True
        while parsing_prefix and not self._is_at_end():
            # Check for modifiers (global, private, const, undefined, etc.)
            if self._check(TokenType.KEYWORD) and self._is_function_modifier(self._current().value):
                mod = self._advance().value
                if mod == 'global':
                    is_global = True
                elif mod == 'const':
                    is_const = True
                    modifiers.append(mod)
                else:
                    modifiers.append(mod)
                continue

            # Check for type keyword (int, string, void, vector, datastruct, etc.)
            if self._check(TokenType.KEYWORD) and self._is_type_keyword(self._current().value) and return_type is None:
                return_type = self._advance().value

                # Check for generic type <T> or <T, U>
                if self._check(TokenType.COMPARE_LT):
                    self._advance()  # skip <
                    generic_parts = []
                    depth = 1
                    while depth > 0 and not self._is_at_end():
                        if self._check(TokenType.COMPARE_LT):
                            depth += 1
                            generic_parts.append('<')
                        elif self._check(TokenType.COMPARE_GT):
                            depth -= 1
                            if depth > 0:
                                generic_parts.append('>')
                        elif self._check(TokenType.COMMA):
                            generic_parts.append(',')
                        else:
                            generic_parts.append(str(self._current().value))
                        self._advance()
                    generic_type = ''.join(generic_parts)
                continue

            # Check for * prefix (non-null) or *[type] (type exclusion)
            if self._check(TokenType.MULTIPLY):
                self._advance()
                # Check for type exclusion filter: *[string], *[int], etc.
                if self._check(TokenType.BRACKET_START):
                    self._advance()  # consume [
                    exclude_type = self._advance().value  # get type name
                    self._expect(TokenType.BRACKET_END)
                else:
                    non_null = True
                continue

            # Check for @ prefix (global function)
            if self._check(TokenType.AT):
                self._advance()
                is_global = True
                continue

            # If we've reached an identifier, we're at the function name
            if self._check(TokenType.IDENTIFIER):
                parsing_prefix = False
            else:
                # Unknown token in prefix, break out
                parsing_prefix = False

        # Phase 2: Get function name
        if not self._check(TokenType.IDENTIFIER):
            self.error(f"Expected function name, got {self._current().type.name}")
        name = self._advance().value

        # Phase 3: Parse parameters
        params = []
        self._expect(TokenType.PAREN_START)

        while not self._check(TokenType.PAREN_END) and not self._is_at_end():
            param_info = {}

            # Handle 'open' keyword for open parameters
            if self._match_keyword('open'):
                param_info['open'] = True

            # Handle const parameters
            if self._match_keyword('const'):
                param_info['const'] = True

            # Handle type annotations (builtin types like int, string, etc.)
            if self._check(TokenType.KEYWORD) and self._is_type_keyword(self._current().value):
                param_info['type'] = self._advance().value

                # Check for generic type parameter <T>
                if self._check(TokenType.COMPARE_LT):
                    self._advance()
                    generic_parts = []
                    depth = 1
                    while depth > 0 and not self._is_at_end():
                        if self._check(TokenType.COMPARE_LT):
                            depth += 1
                            generic_parts.append('<')
                        elif self._check(TokenType.COMPARE_GT):
                            depth -= 1
                            if depth > 0:
                                generic_parts.append('>')
                        elif self._check(TokenType.COMMA):
                            generic_parts.append(',')
                        else:
                            generic_parts.append(str(self._current().value))
                        self._advance()
                    param_info['generic'] = ''.join(generic_parts)

            # Handle custom class types (identifier followed by another identifier = type + name)
            elif self._check(TokenType.IDENTIFIER):
                saved_pos = self.pos
                potential_type = self._advance().value

                # Check for generic type parameter <T> on custom type
                if self._check(TokenType.COMPARE_LT):
                    self._advance()
                    generic_parts = []
                    depth = 1
                    while depth > 0 and not self._is_at_end():
                        if self._check(TokenType.COMPARE_LT):
                            depth += 1
                            generic_parts.append('<')
                        elif self._check(TokenType.COMPARE_GT):
                            depth -= 1
                            if depth > 0:
                                generic_parts.append('>')
                        elif self._check(TokenType.COMMA):
                            generic_parts.append(',')
                        else:
                            generic_parts.append(str(self._current().value))
                        self._advance()
                    param_info['generic'] = ''.join(generic_parts)

                # If followed by identifier, this is "Type name" pattern
                if self._check(TokenType.IDENTIFIER):
                    param_info['type'] = potential_type
                else:
                    # Not a type, restore position - this is just a param name
                    self.pos = saved_pos

            # Handle * prefix for non-null parameters
            if self._match(TokenType.MULTIPLY):
                param_info['non_null'] = True

            # Handle reference operator &
            if self._match(TokenType.AMPERSAND):
                param_info['ref'] = True

            # Get parameter name
            if self._check(TokenType.IDENTIFIER):
                param_name = self._advance().value
                if param_info:
                    params.append({'name': param_name, **param_info})
                else:
                    params.append(param_name)
            elif self._check(TokenType.KEYWORD):
                # Parameter name could be a keyword like 'Params'
                param_name = self._advance().value
                if param_info:
                    params.append({'name': param_name, **param_info})
                else:
                    params.append(param_name)

            self._match(TokenType.COMMA)

        self._expect(TokenType.PAREN_END)

        # Phase 4: Check for extends/overwrites and append mode
        extends_func = None
        extends_is_python = False
        extends_class_ref = None
        extends_method_ref = None
        overwrites_func = None
        overwrites_is_python = False
        overwrites_class_ref = None
        overwrites_method_ref = None
        append_mode = False
        append_ref_class = None
        append_ref_member = None

        # Check for &ClassName::member or &ClassName.member or &function reference
        if self._match(TokenType.AMPERSAND):
            if self._check(TokenType.IDENTIFIER):
                append_ref_class = self._advance().value
            elif self._check(TokenType.AT):
                self._advance()
                if self._check(TokenType.IDENTIFIER):
                    append_ref_class = '@' + self._advance().value
            elif self._check(TokenType.SHARED_REF):
                append_ref_class = f'${self._advance().value}'

            # Check for ::member or .member (support both syntaxes)
            if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.DOT):
                if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                    append_ref_member = self._advance().value

        # Check for ++ append operator
        if self._match(TokenType.PLUS_PLUS):
            append_mode = True

        # Check for : or :: extends/overwrites
        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON):
            while True:
                if self._match_keyword('extends'):
                    # Parse target: @ModuleName, $PythonObject, Parent::method, Parent.method
                    if self._check(TokenType.AT):
                        self._advance()
                        extends_func = '@' + self._advance().value
                    elif self._check(TokenType.SHARED_REF):
                        extends_is_python = True
                        extends_func = self._advance().value
                    elif self._check(TokenType.IDENTIFIER):
                        first_part = self._advance().value
                        # Support both :: and . for class method access
                        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.DOT):
                            extends_class_ref = first_part
                            extends_method_ref = self._advance().value
                        else:
                            extends_func = first_part
                    # Skip optional ()
                    if self._match(TokenType.PAREN_START):
                        self._expect(TokenType.PAREN_END)
                elif self._match_keyword('overwrites'):
                    if self._check(TokenType.AT):
                        self._advance()
                        overwrites_func = '@' + self._advance().value
                    elif self._check(TokenType.SHARED_REF):
                        overwrites_is_python = True
                        overwrites_func = self._advance().value
                    elif self._check(TokenType.IDENTIFIER):
                        first_part = self._advance().value
                        # Support both :: and . for class method access
                        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.DOT):
                            overwrites_class_ref = first_part
                            overwrites_method_ref = self._advance().value
                        else:
                            overwrites_func = first_part
                    if self._match(TokenType.PAREN_START):
                        self._expect(TokenType.PAREN_END)
                else:
                    break
                if not (self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON)):
                    break

        # Phase 5: Parse function body
        node = ASTNode('function', value={
            'name': name,
            'is_global': is_global,
            'is_const': is_const,
            'params': params,
            'return_type': return_type,
            'generic_type': generic_type,
            'modifiers': modifiers,
            'non_null': non_null,
            'exclude_type': exclude_type,
            'extends': extends_func,
            'extends_is_python': extends_is_python,
            'extends_class': extends_class_ref,
            'extends_method': extends_method_ref,
            'overwrites': overwrites_func,
            'overwrites_is_python': overwrites_is_python,
            'overwrites_class': overwrites_class_ref,
            'overwrites_method': overwrites_method_ref,
            'append_mode': append_mode,
            'append_ref_class': append_ref_class,
            'append_ref_member': append_ref_member,
            'enforce_return_type': return_type is not None and 'meta' not in modifiers
        }, children=[])

        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _looks_like_namespace_call(self) -> bool:
        """Check if current position looks like a namespace function call.

        Pattern: keyword::identifier(...) like json::write(), string::cut()
        This allows type keywords to be used as namespace prefixes for function calls.
        """
        if not self._check(TokenType.KEYWORD):
            return False

        # Save position
        saved_pos = self.pos

        self._advance()  # Skip keyword

        # Must be followed by ::
        result = self._check(TokenType.DOUBLE_COLON)

        # Restore position
        self.pos = saved_pos
        return result

    def _looks_like_typed_variable(self) -> bool:
        """Check if current position looks like a typed variable declaration:
        type_name varName; or type_name<T> varName; or type_name varName = value;
        """
        # Save position
        saved_pos = self.pos

        # Must start with a type keyword (int, string, stack, vector, etc.)
        if not self._check(TokenType.KEYWORD):
            return False

        type_name = self._current().value

        # Skip known type keywords
        type_keywords = {'int', 'string', 'float', 'bool', 'dynamic', 'void',
                        'stack', 'vector', 'datastruct', 'dataspace', 'shuffled',
                        'iterator', 'combo', 'array', 'openquote', 'json',
                        'list', 'dictionary', 'dict', 'instance', 'map'}
        if type_name not in type_keywords:
            return False

        self._advance()

        # Check for optional generic <T>
        if self._match(TokenType.COMPARE_LT):
            # Skip until >
            depth = 1
            while depth > 0 and not self._is_at_end():
                if self._check(TokenType.COMPARE_LT):
                    depth += 1
                elif self._check(TokenType.COMPARE_GT):
                    depth -= 1
                self._advance()

        # Next should be an identifier (variable name), not '(' (function) or ';'
        result = self._check(TokenType.IDENTIFIER)

        # Restore position
        self.pos = saved_pos
        return result

    def _parse_typed_variable(self) -> Optional[ASTNode]:
        """Parse a typed variable declaration: type varName; or type<T> *varName = value;

        The * prefix indicates a non-nullable variable (can never be None/null).
        Example: vector<dynamic> *MyVector - can never contain None values.
        """
        # Get type name
        type_name = self._advance().value  # Consume type keyword

        # Check for generic type <T> or instance<"name">
        element_type = None
        if self._match(TokenType.COMPARE_LT):
            # For instance<"name">, element_type can be a string literal
            if type_name == 'instance' and self._check(TokenType.STRING):
                element_type = self._advance().value
            elif self._check(TokenType.KEYWORD) or self._check(TokenType.IDENTIFIER):
                element_type = self._advance().value
            self._expect(TokenType.COMPARE_GT)

        # Check for * prefix (non-nullable indicator)
        non_null = False
        if self._match(TokenType.MULTIPLY):
            non_null = True

        # Get variable name
        if not self._check(TokenType.IDENTIFIER):
            return None
        var_name = self._advance().value

        # Check for assignment or just declaration
        value = None
        if self._match(TokenType.EQUALS):
            value = self._parse_expression()

        self._match(TokenType.SEMICOLON)

        # For instance<"name">, create a special node type
        if type_name == 'instance':
            return ASTNode('instance_declaration', value={
                'instance_name': element_type,
                'name': var_name,
                'value': value,
                'non_null': non_null
            })

        return ASTNode('typed_declaration', value={
            'type': type_name,
            'element_type': element_type,
            'name': var_name,
            'value': value,
            'non_null': non_null
        })

    def parse_program(self) -> ASTNode:
        """Parse a standalone program (no service wrapper)"""
        root = ASTNode('program', children=[])

        while not self._is_at_end():
            if self._match_keyword('struct'):
                root.children.append(self._parse_struct())
            elif self._match_keyword('class'):
                root.children.append(self._parse_class())
            elif self._match_keyword('define'):
                root.children.append(self._parse_define())
            # Check for C-style typed function declarations
            elif self._looks_like_function_declaration():
                root.children.append(self._parse_typed_function())
            # Check for typed variable declarations (int x;, stack<string> s;)
            elif self._looks_like_typed_variable():
                decl = self._parse_typed_variable()
                if decl:
                    root.children.append(decl)
            # Handle service blocks
            elif self._match_keyword('service-init'):
                root.children.append(self._parse_service_init())
            elif self._match_keyword('service-include'):
                root.children.append(self._parse_service_include())
            elif self._match_keyword('service-run'):
                root.children.append(self._parse_service_run())
            elif self._match_keyword('package'):
                root.children.append(self._parse_package())
            elif self._match_keyword('package-includes'):
                root.children.append(self._parse_package_includes())
            # Handle global declarations
            elif self._match_keyword('global'):
                # Check if followed by class or define (global class/function)
                if self._match_keyword('class'):
                    root.children.append(self._parse_class(is_global=True))
                elif self._match_keyword('define'):
                    root.children.append(self._parse_define(is_global=True))
                elif self._looks_like_function_declaration():
                    # global void MyFunc() { } or global int MyFunc() { }
                    root.children.append(self._parse_typed_function(is_global=True))
                else:
                    stmt = self._parse_expression_statement()
                    if stmt:
                        # Wrap in global_assignment to mark as global variable
                        global_stmt = ASTNode('global_assignment', value=stmt)
                        root.children.append(global_stmt)
            elif self._check(TokenType.GLOBAL_REF):
                stmt = self._parse_expression_statement()
                if stmt:
                    # Wrap in global_assignment to mark as global variable (same as 'global' keyword)
                    global_stmt = ASTNode('global_assignment', value=stmt)
                    root.children.append(global_stmt)
            # Control flow keywords must be checked BEFORE generic KEYWORD handling
            elif self._match_keyword('if'):
                root.children.append(self._parse_if())
            elif self._match_keyword('while'):
                root.children.append(self._parse_while())
            elif self._match_keyword('for'):
                root.children.append(self._parse_for())
            elif self._match_keyword('foreach'):
                root.children.append(self._parse_foreach())
            # Handle statements - keywords like 'instance', 'list', 'map' can be variable names
            elif (self._check(TokenType.IDENTIFIER) or self._check(TokenType.AT) or
                  self._check(TokenType.SELF_REF) or self._check(TokenType.SHARED_REF) or
                  self._check(TokenType.KEYWORD)):
                stmt = self._parse_expression_statement()
                if stmt:
                    root.children.append(stmt)
            # Skip comments and newlines
            elif self._check(TokenType.COMMENT) or self._check(TokenType.NEWLINE):
                self._advance()
            else:
                self._advance()

        return root

    def _current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, '', 0, 0)

    def _peek(self, offset=0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return Token(TokenType.EOF, '', 0, 0)

    def _advance(self) -> Token:
        token = self._current()
        self.pos += 1
        return token

    def _is_at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        return self._current().type == token_type

    def _match(self, token_type: TokenType) -> bool:
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _match_keyword(self, keyword: str) -> bool:
        if self._current().type == TokenType.KEYWORD and self._current().value == keyword:
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, message: str = None):
        if not self._match(token_type):
            msg = message or f"Expected {token_type.name}, got {self._current().type.name}"
            self.error(msg)
        return self.tokens[self.pos - 1]

    def _parse_service_init(self) -> ASTNode:
        node = ASTNode('service-init', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                key = self._advance().value
                self._expect(TokenType.COLON)
                value = self._parse_value()
                node.children.append(ASTNode('property', value={'key': key, 'value': value}))
                self._match(TokenType.SEMICOLON)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_service_include(self) -> ASTNode:
        """Parse service-include block for importing modules and files

        Syntax:
        service-include {
            @KernelClient <== get(include(cso_root('/root32/etc/tasks/kernel.cssl')));
            @Time <== get('time');
            @Secrets <== get('secrets');
        }
        """
        node = ASTNode('service-include', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            # Parse module injection statements like @ModuleName <== get(...);
            if self._check(TokenType.AT):
                stmt = self._parse_expression_statement()
                if stmt:
                    node.children.append(stmt)
            elif self._check(TokenType.IDENTIFIER):
                # Also support identifier-based assignments: moduleName <== get(...);
                stmt = self._parse_expression_statement()
                if stmt:
                    node.children.append(stmt)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_service_run(self) -> ASTNode:
        node = ASTNode('service-run', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._match_keyword('struct'):
                node.children.append(self._parse_struct())
            elif self._match_keyword('define'):
                node.children.append(self._parse_define())
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_package(self) -> ASTNode:
        """Parse package {} block for service metadata - NEW

        Syntax:
        package {
            service = "ServiceName";
            exec = @Start();
            version = "1.0.0";
            description = "Beschreibung";
        }
        """
        node = ASTNode('package', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                key = self._advance().value
                self._expect(TokenType.EQUALS)
                value = self._parse_expression()
                node.children.append(ASTNode('package_property', value={'key': key, 'value': value}))
                self._match(TokenType.SEMICOLON)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_package_includes(self) -> ASTNode:
        """Parse package-includes {} block for imports - NEW

        Syntax:
        package-includes {
            @Lists = get('list');
            @OS = get('os');
            @Time = get('time');
            @VSRam = get('vsramsdk');
        }
        """
        node = ASTNode('package-includes', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            # Parse module injection statements like @ModuleName = get(...);
            if self._check(TokenType.AT):
                stmt = self._parse_expression_statement()
                if stmt:
                    node.children.append(stmt)
            elif self._check(TokenType.IDENTIFIER):
                # Also support identifier-based assignments
                stmt = self._parse_expression_statement()
                if stmt:
                    node.children.append(stmt)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_struct(self) -> ASTNode:
        name = self._advance().value
        is_global = False

        # Check for (@) decorator: struct Name(@) { ... }
        if self._match(TokenType.PAREN_START):
            if self._check(TokenType.AT):
                self._advance()  # skip @
                is_global = True
            self._expect(TokenType.PAREN_END)

        node = ASTNode('struct', value={'name': name, 'global': is_global}, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._match_keyword('define'):
                node.children.append(self._parse_define())
            elif self._check(TokenType.IDENTIFIER):
                # Look ahead to determine what kind of statement this is
                saved_pos = self.pos
                var_name = self._advance().value

                if self._match(TokenType.INJECT_LEFT):
                    # Injection: var <== expr
                    value = self._parse_expression()
                    node.children.append(ASTNode('injection', value={'name': var_name, 'source': value}))
                    self._match(TokenType.SEMICOLON)
                elif self._match(TokenType.EQUALS):
                    # Assignment: var = expr
                    value = self._parse_expression()
                    node.children.append(ASTNode('assignment', value={'name': var_name, 'value': value}))
                    self._match(TokenType.SEMICOLON)
                elif self._check(TokenType.PAREN_START):
                    # Function call: func(args)
                    self.pos = saved_pos  # Go back to parse full expression
                    stmt = self._parse_expression_statement()
                    if stmt:
                        node.children.append(stmt)
                elif self._match(TokenType.DOT):
                    # Method call: obj.method(args)
                    self.pos = saved_pos  # Go back to parse full expression
                    stmt = self._parse_expression_statement()
                    if stmt:
                        node.children.append(stmt)
                else:
                    self._match(TokenType.SEMICOLON)
            elif self._check(TokenType.AT):
                # Module reference statement
                stmt = self._parse_expression_statement()
                if stmt:
                    node.children.append(stmt)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_class(self, is_global: bool = False) -> ASTNode:
        """Parse class declaration with members and methods.

        Syntax:
            class ClassName { ... }           // Local class
            global class ClassName { ... }    // Global class
            class @ClassName { ... }          // Global class (alternative)
            class *ClassName { ... }          // Non-null class

        Non-null class (all methods return non-null):
            class *MyClass { ... }
        """
        # Check for * prefix (non-null class - all methods return non-null)
        non_null = False
        if self._match(TokenType.MULTIPLY):
            non_null = True

        # Check for @ prefix (global class): class @ClassName
        if self._check(TokenType.AT):
            self._advance()  # consume @
            is_global = True

        class_name = self._advance().value

        # Check for class-level constructor parameters: class MyClass (int x, string y) { ... }
        class_params = []
        if self._match(TokenType.PAREN_START):
            class_params = self._parse_parameter_list()
            self._expect(TokenType.PAREN_END)

        # Check for inheritance and overwrites:
        # class Child : extends Parent { ... }
        # class Child : extends $PythonObject { ... }
        # class Child : extends Parent : overwrites Parent { ... }
        # class Child : extends Parent (param1, param2) { ... }  <- constructor args for parent
        extends_class = None
        extends_is_python = False
        extends_lang_ref = None  # v4.1.0: Cross-language inheritance (cpp$ClassName)
        extends_args = []
        overwrites_class = None
        overwrites_is_python = False
        supports_language = None  # v4.1.0: Multi-language syntax support

        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON):
            # Parse extends and/or overwrites (can be chained with : or ::)
            while True:
                if self._match_keyword('extends'):
                    # v4.1.0: Check for cross-language inheritance: extends cpp$ClassName
                    if self._check(TokenType.LANG_INSTANCE_REF):
                        ref = self._advance().value
                        extends_lang_ref = ref  # {'lang': 'cpp', 'instance': 'ClassName'}
                        extends_class = ref['instance']
                    elif self._check(TokenType.IDENTIFIER):
                        extends_class = self._advance().value
                    elif self._check(TokenType.SHARED_REF):
                        extends_class = self._advance().value
                        extends_is_python = True
                    else:
                        raise CSSLSyntaxError("Expected parent class name after 'extends'")
                    # Check for constructor arguments: extends Parent (arg1, arg2)
                    if self._match(TokenType.PAREN_START):
                        while not self._check(TokenType.PAREN_END):
                            arg = self._parse_expression()
                            extends_args.append(arg)
                            self._match(TokenType.COMMA)
                        self._expect(TokenType.PAREN_END)
                elif self._match_keyword('overwrites'):
                    if self._check(TokenType.IDENTIFIER):
                        overwrites_class = self._advance().value
                    elif self._check(TokenType.SHARED_REF):
                        overwrites_class = self._advance().value
                        overwrites_is_python = True
                    else:
                        raise CSSLSyntaxError("Expected class name after 'overwrites'")
                    # Skip optional () after class name
                    if self._match(TokenType.PAREN_START):
                        self._expect(TokenType.PAREN_END)
                # v4.1.0: Parse 'supports' keyword for multi-language syntax
                elif self._match_keyword('supports'):
                    if self._check(TokenType.AT):
                        self._advance()  # consume @
                        if self._check(TokenType.IDENTIFIER):
                            supports_language = '@' + self._advance().value
                        else:
                            raise CSSLSyntaxError("Expected language identifier after '@' in 'supports'")
                    elif self._check(TokenType.IDENTIFIER):
                        supports_language = self._advance().value
                    else:
                        raise CSSLSyntaxError("Expected language identifier after 'supports'")
                else:
                    raise CSSLSyntaxError("Expected 'extends', 'overwrites', or 'supports' after ':' or '::' in class declaration")
                # Check for another : or :: for chaining
                if not (self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON)):
                    break

        node = ASTNode('class', value={
            'name': class_name,
            'is_global': is_global,
            'non_null': non_null,
            'class_params': class_params,
            'extends': extends_class,
            'extends_is_python': extends_is_python,
            'extends_lang_ref': extends_lang_ref,  # v4.1.0
            'extends_args': extends_args,
            'overwrites': overwrites_class,
            'overwrites_is_python': overwrites_is_python,
            'supports_language': supports_language  # v4.1.0
        }, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            # Check for typed function (method) declaration
            if self._looks_like_function_declaration():
                method = self._parse_typed_function()
                method_info = method.value
                method_name = method_info.get('name')

                # Mark constructor (same name as class or __init__)
                if method_name == class_name or method_name == '__init__':
                    method.value['is_constructor'] = True

                node.children.append(method)

            # Check for typed member variable declaration
            elif self._looks_like_typed_variable():
                member = self._parse_typed_variable()
                if member:
                    # Mark as class member
                    member.value['is_member'] = True
                    node.children.append(member)

            # Check for define-style method
            elif self._match_keyword('define'):
                method = self._parse_define()
                node.children.append(method)

            # Check for constr keyword (constructor declaration)
            # Syntax: constr ConstructorName() { ... }
            # or: constr ConstructorName() : extends Parent::ConstructorName { ... }
            elif self._match_keyword('constr'):
                constructor = self._parse_constructor(class_name)
                node.children.append(constructor)

            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_constructor(self, class_name: str) -> ASTNode:
        """Parse constructor declaration inside a class.

        Syntax:
            constr ConstructorName() { ... }
            constr ConstructorName() ++ { ... }  // Append: keeps parent constructor + adds new code
            constr ConstructorName() &ParentClass::constructors ++ { ... }  // Append specific parent constructor
            constr ConstructorName() : extends ParentClass::ConstructorName { ... }
            constr ConstructorName() : extends ParentClass::ConstructorName : overwrites ParentClass::ConstructorName { ... }

        The ++ operator means: execute parent's version first, then execute this code (append mode).
        The &ClassName::member syntax references a specific member from the overwritten class.
        """
        # Get constructor name
        if not self._check(TokenType.IDENTIFIER):
            raise CSSLSyntaxError("Expected constructor name after 'constr'")
        constr_name = self._advance().value

        # Parse method-level extends/overwrites with :: syntax
        extends_target = None
        extends_class_ref = None
        extends_method_ref = None
        overwrites_target = None
        overwrites_class_ref = None
        overwrites_method_ref = None

        # New: Append mode and reference tracking
        append_mode = False  # ++ operator: keep parent code + add new
        append_ref_class = None  # &ClassName part
        append_ref_member = None  # ::member part (constructors, functionName, etc.)

        # Parse parameters
        params = []
        if self._match(TokenType.PAREN_START):
            params = self._parse_parameter_list()
            self._expect(TokenType.PAREN_END)

        # Check for &ClassName::member reference (for targeting specific parent member)
        # Syntax: constr Name() &ParentClass::constructors ++ { ... }
        if self._match(TokenType.AMPERSAND):
            # Parse the class reference
            if self._check(TokenType.IDENTIFIER):
                append_ref_class = self._advance().value
            elif self._check(TokenType.SHARED_REF):
                append_ref_class = f'${self._advance().value}'
            else:
                raise CSSLSyntaxError("Expected class name after '&' in constructor reference")

            # Check for ::member
            if self._match(TokenType.DOUBLE_COLON):
                if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                    append_ref_member = self._advance().value
                else:
                    raise CSSLSyntaxError("Expected member name after '::' in constructor reference")

        # Check for ++ append operator
        if self._match(TokenType.PLUS_PLUS):
            append_mode = True

        # Check for method-level extends/overwrites with :: or :
        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON):
            while True:
                if self._match_keyword('extends'):
                    # Parse Parent::method or just method
                    extends_target = self._parse_qualified_method_ref()
                    if '::' in extends_target:
                        parts = extends_target.split('::')
                        extends_class_ref = parts[0]
                        extends_method_ref = parts[1]
                    else:
                        extends_method_ref = extends_target
                elif self._match_keyword('overwrites'):
                    # Parse Parent::method or just method
                    overwrites_target = self._parse_qualified_method_ref()
                    if '::' in overwrites_target:
                        parts = overwrites_target.split('::')
                        overwrites_class_ref = parts[0]
                        overwrites_method_ref = parts[1]
                    else:
                        overwrites_method_ref = overwrites_target
                else:
                    break
                # Check for another :: or : for chaining
                if not (self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON)):
                    break

        # Parse constructor body
        self._expect(TokenType.BLOCK_START)
        body = []
        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        self._expect(TokenType.BLOCK_END)

        return ASTNode('constructor', value={
            'name': constr_name,
            'class_name': class_name,
            'params': params,
            'is_constructor': True,
            'extends_target': extends_target,
            'extends_class': extends_class_ref,
            'extends_method': extends_method_ref,
            'overwrites_target': overwrites_target,
            'overwrites_class': overwrites_class_ref,
            'overwrites_method': overwrites_method_ref,
            # New append mode fields
            'append_mode': append_mode,
            'append_ref_class': append_ref_class,
            'append_ref_member': append_ref_member
        }, children=body)

    def _parse_qualified_method_ref(self) -> str:
        """Parse a qualified method reference like 'ParentClass::methodName' or just 'methodName'.

        Returns the qualified name as a string (e.g., 'Parent::init' or just 'init').
        """
        # Check for $PythonObject
        if self._check(TokenType.SHARED_REF):
            class_ref = self._advance().value  # Gets the name without $
            class_ref = f'${class_ref}'
        elif self._check(TokenType.IDENTIFIER):
            class_ref = self._advance().value
        else:
            raise CSSLSyntaxError("Expected class or method name in extends/overwrites")

        # Check for :: to get method part
        if self._match(TokenType.DOUBLE_COLON):
            if self._check(TokenType.IDENTIFIER):
                method_ref = self._advance().value
                return f'{class_ref}::{method_ref}'
            else:
                raise CSSLSyntaxError("Expected method name after '::'")

        # Just method name, no class qualifier
        return class_ref

    def _parse_parameter_list(self) -> list:
        """Parse a list of parameters (without the surrounding parentheses).

        Returns a list of parameter definitions, each can be:
        - Simple string name: "paramName"
        - Dict with type info: {'name': 'paramName', 'type': 'string', 'ref': True, ...}
        """
        params = []
        while not self._check(TokenType.PAREN_END) and not self._is_at_end():
            param_info = {}

            # Handle 'open' keyword for open parameters
            if self._match_keyword('open'):
                param_info['open'] = True

            # Handle type annotations (e.g., string, int, dynamic, etc.)
            if self._check(TokenType.KEYWORD):
                param_info['type'] = self._advance().value

            # Handle reference operator &
            if self._match(TokenType.AMPERSAND):
                param_info['ref'] = True

            # Handle * prefix for non-null parameters
            if self._match(TokenType.MULTIPLY):
                param_info['non_null'] = True

            # Get parameter name
            if self._check(TokenType.IDENTIFIER):
                param_name = self._advance().value
                if param_info:
                    params.append({'name': param_name, **param_info})
                else:
                    params.append(param_name)
                self._match(TokenType.COMMA)
            elif self._check(TokenType.KEYWORD):
                # Parameter name could be a keyword like 'Params'
                param_name = self._advance().value
                if param_info:
                    params.append({'name': param_name, **param_info})
                else:
                    params.append(param_name)
                self._match(TokenType.COMMA)
            else:
                break

        return params

    def _parse_define(self, is_global: bool = False) -> ASTNode:
        """Parse define function declaration.

        Syntax:
            define MyFunc(args) { }           // Local function
            global define MyFunc(args) { }    // Global function
            define @MyFunc(args) { }          // Global function (alternative)
            define *MyFunc(args) { }          // Non-null: must never return None
            define MyFunc : extends OtherFunc() { }  // Inherit local vars
            define MyFunc : overwrites OtherFunc() { }  // Replace OtherFunc
            define MyFunc :: extends Parent::Method :: overwrites Parent::Method() { }  // Method-level inheritance
        """
        # Check for * prefix (non-null function - must return non-null)
        # Also *[type] for type exclusion (must NOT return that type)
        non_null = False
        exclude_type = None
        if self._match(TokenType.MULTIPLY):
            # Check for type exclusion filter: *[string], *[int], etc.
            if self._check(TokenType.BRACKET_START):
                self._advance()  # consume [
                exclude_type = self._advance().value  # get type name
                self._expect(TokenType.BRACKET_END)
            else:
                non_null = True

        # Check for @ prefix (global function): define @FuncName
        if self._check(TokenType.AT):
            self._advance()  # consume @
            is_global = True

        name = self._advance().value

        # Check for extends/overwrites: define func : extends/overwrites target() { }
        # Also supports method-level :: syntax: define func :: extends Parent::method
        extends_func = None
        overwrites_func = None
        extends_is_python = False
        overwrites_is_python = False
        extends_class_ref = None
        extends_method_ref = None
        overwrites_class_ref = None
        overwrites_method_ref = None
        supports_language = None  # v4.1.0: Multi-language syntax support

        if self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON):
            # Parse extends and/or overwrites (supports :: method-level syntax)
            while True:
                if self._match_keyword('extends'):
                    # Check for qualified reference: Parent::method
                    if self._check(TokenType.SHARED_REF):
                        extends_is_python = True
                        extends_func = self._advance().value
                        # Check for ::method
                        if self._match(TokenType.DOUBLE_COLON):
                            extends_class_ref = f'${extends_func}'
                            if self._check(TokenType.IDENTIFIER):
                                extends_method_ref = self._advance().value
                            else:
                                raise CSSLSyntaxError("Expected method name after '::'")
                    elif self._check(TokenType.IDENTIFIER):
                        first_part = self._advance().value
                        # Check for ::method (qualified reference)
                        if self._match(TokenType.DOUBLE_COLON):
                            extends_class_ref = first_part
                            if self._check(TokenType.IDENTIFIER):
                                extends_method_ref = self._advance().value
                            else:
                                raise CSSLSyntaxError("Expected method name after '::'")
                        else:
                            extends_func = first_part
                    else:
                        raise CSSLSyntaxError("Expected function name after 'extends'")
                    # Skip optional () after function/method name
                    if self._match(TokenType.PAREN_START):
                        self._expect(TokenType.PAREN_END)
                elif self._match_keyword('overwrites'):
                    # Check for qualified reference: Parent::method
                    if self._check(TokenType.SHARED_REF):
                        overwrites_is_python = True
                        overwrites_func = self._advance().value
                        # Check for ::method
                        if self._match(TokenType.DOUBLE_COLON):
                            overwrites_class_ref = f'${overwrites_func}'
                            if self._check(TokenType.IDENTIFIER):
                                overwrites_method_ref = self._advance().value
                            else:
                                raise CSSLSyntaxError("Expected method name after '::'")
                    elif self._check(TokenType.IDENTIFIER):
                        first_part = self._advance().value
                        # Check for ::method (qualified reference)
                        if self._match(TokenType.DOUBLE_COLON):
                            overwrites_class_ref = first_part
                            if self._check(TokenType.IDENTIFIER):
                                overwrites_method_ref = self._advance().value
                            else:
                                raise CSSLSyntaxError("Expected method name after '::'")
                        else:
                            overwrites_func = first_part
                    else:
                        raise CSSLSyntaxError("Expected function name after 'overwrites'")
                    # Skip optional () after function/method name
                    if self._match(TokenType.PAREN_START):
                        self._expect(TokenType.PAREN_END)
                # v4.1.0: Parse 'supports' keyword for multi-language syntax
                elif self._match_keyword('supports'):
                    if self._check(TokenType.AT):
                        self._advance()  # consume @
                        if self._check(TokenType.IDENTIFIER):
                            supports_language = '@' + self._advance().value
                        else:
                            raise CSSLSyntaxError("Expected language identifier after '@' in 'supports'")
                    elif self._check(TokenType.IDENTIFIER):
                        supports_language = self._advance().value
                    else:
                        raise CSSLSyntaxError("Expected language identifier after 'supports'")
                else:
                    break
                # Check for another :: or : for chaining extends/overwrites
                if not (self._match(TokenType.DOUBLE_COLON) or self._match(TokenType.COLON)):
                    break

        params = []

        if self._match(TokenType.PAREN_START):
            while not self._check(TokenType.PAREN_END):
                param_info = {}
                # Handle 'open' keyword for open parameters
                if self._match_keyword('open'):
                    param_info['open'] = True
                # Handle type annotations (e.g., string, int, dynamic, etc.)
                if self._check(TokenType.KEYWORD):
                    param_info['type'] = self._advance().value
                # Handle reference operator &
                if self._match(TokenType.AMPERSAND):
                    param_info['ref'] = True
                # Handle * prefix for non-null parameters
                if self._match(TokenType.MULTIPLY):
                    param_info['non_null'] = True
                # Get parameter name
                if self._check(TokenType.IDENTIFIER):
                    param_name = self._advance().value
                    if param_info:
                        params.append({'name': param_name, **param_info})
                    else:
                        params.append(param_name)
                    self._match(TokenType.COMMA)
                elif self._check(TokenType.KEYWORD):
                    # Parameter name could be a keyword like 'Params'
                    param_name = self._advance().value
                    if param_info:
                        params.append({'name': param_name, **param_info})
                    else:
                        params.append(param_name)
                    self._match(TokenType.COMMA)
                else:
                    break
            self._expect(TokenType.PAREN_END)

        # New: Append mode and reference tracking for functions
        # Syntax: define XYZ(int zahl) &overwrittenclass::functionyouwanttokeep ++ { ... }
        append_mode = False
        append_ref_class = None
        append_ref_member = None

        # Check for &ClassName::member reference
        if self._match(TokenType.AMPERSAND):
            if self._check(TokenType.IDENTIFIER):
                append_ref_class = self._advance().value
            elif self._check(TokenType.SHARED_REF):
                append_ref_class = f'${self._advance().value}'
            else:
                raise CSSLSyntaxError("Expected class name after '&' in function reference")

            # Check for ::member
            if self._match(TokenType.DOUBLE_COLON):
                if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                    append_ref_member = self._advance().value
                else:
                    raise CSSLSyntaxError("Expected member name after '::' in function reference")

        # Check for ++ append operator
        if self._match(TokenType.PLUS_PLUS):
            append_mode = True

        node = ASTNode('function', value={
            'name': name,
            'is_global': is_global,
            'params': params,
            'non_null': non_null,
            'exclude_type': exclude_type,  # *[type] - must NOT return this type
            'extends': extends_func,
            'extends_is_python': extends_is_python,
            'overwrites': overwrites_func,
            'overwrites_is_python': overwrites_is_python,
            # Method-level inheritance (Parent::method syntax)
            'extends_class': extends_class_ref,
            'extends_method': extends_method_ref,
            'overwrites_class': overwrites_class_ref,
            'overwrites_method': overwrites_method_ref,
            # New append mode fields
            'append_mode': append_mode,
            'append_ref_class': append_ref_class,
            'append_ref_member': append_ref_member,
            # v4.1.0: Multi-language support
            'supports_language': supports_language
        }, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_statement(self) -> Optional[ASTNode]:
        if self._match_keyword('if'):
            return self._parse_if()
        elif self._match_keyword('while'):
            return self._parse_while()
        elif self._match_keyword('for'):
            return self._parse_for()
        elif self._match_keyword('foreach'):
            return self._parse_foreach()
        elif self._match_keyword('switch'):
            return self._parse_switch()
        elif self._match_keyword('return'):
            return self._parse_return()
        elif self._match_keyword('break'):
            self._match(TokenType.SEMICOLON)
            return ASTNode('break')
        elif self._match_keyword('continue'):
            self._match(TokenType.SEMICOLON)
            return ASTNode('continue')
        elif self._match_keyword('try'):
            return self._parse_try()
        elif self._match_keyword('await'):
            return self._parse_await()
        elif self._match_keyword('define'):
            # Nested define function
            return self._parse_define()
        elif self._looks_like_typed_variable():
            # Typed variable declaration (e.g., stack<string> myStack;)
            return self._parse_typed_variable()
        elif self._looks_like_function_declaration():
            # Nested typed function (e.g., void Level2() { ... })
            return self._parse_typed_function()
        elif self._check(TokenType.SUPER_FUNC):
            # Super-function for .cssl-pl payload files
            return self._parse_super_function()
        elif (self._check(TokenType.KEYWORD) and self._current().value == 'super' and
              (self._peek(1).type == TokenType.PAREN_START or
               self._peek(1).type == TokenType.DOUBLE_COLON)):
            # super() or super::method() call - calls parent constructor/method
            return self._parse_super_call()
        elif (self._check(TokenType.IDENTIFIER) or self._check(TokenType.AT) or
              self._check(TokenType.CAPTURED_REF) or self._check(TokenType.SHARED_REF) or
              self._check(TokenType.GLOBAL_REF) or self._check(TokenType.SELF_REF) or
              (self._check(TokenType.KEYWORD) and self._current().value in ('this', 'new')) or
              self._looks_like_namespace_call()):
            return self._parse_expression_statement()
        else:
            self._advance()
            return None

    def _parse_super_call(self) -> ASTNode:
        """Parse super() call to invoke parent constructor or method.

        Syntax:
            super()              - Call parent constructor with no args
            super(arg1, arg2)    - Call parent constructor with args
            super::method()      - Call specific parent method
            super::method(args)  - Call specific parent method with args

        Used inside constructors (constr) and methods to call parent implementations.
        """
        # Consume 'super' keyword
        self._advance()

        # Check for ::method syntax
        target_method = None
        if self._match(TokenType.DOUBLE_COLON):
            if not self._check(TokenType.IDENTIFIER):
                raise CSSLSyntaxError("Expected method name after 'super::'")
            target_method = self._advance().value

        # Parse arguments
        args = []
        self._expect(TokenType.PAREN_START)
        while not self._check(TokenType.PAREN_END):
            arg = self._parse_expression()
            args.append(arg)
            if not self._match(TokenType.COMMA):
                break
        self._expect(TokenType.PAREN_END)
        self._match(TokenType.SEMICOLON)

        return ASTNode('super_call', value={
            'method': target_method,  # None for constructor, method name for specific method
            'args': args
        })

    def _parse_if(self) -> ASTNode:
        """Parse if statement with support for else if AND elif syntax."""
        self._expect(TokenType.PAREN_START)
        condition = self._parse_expression()
        self._expect(TokenType.PAREN_END)

        node = ASTNode('if', value={'condition': condition}, children=[])

        self._expect(TokenType.BLOCK_START)
        then_block = ASTNode('then', children=[])
        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                then_block.children.append(stmt)
        self._expect(TokenType.BLOCK_END)
        node.children.append(then_block)

        # Support both 'else if' AND 'elif' syntax
        if self._match_keyword('elif'):
            # elif is shorthand for else if
            else_block = ASTNode('else', children=[])
            else_block.children.append(self._parse_if())
            node.children.append(else_block)
        elif self._match_keyword('else'):
            else_block = ASTNode('else', children=[])
            if self._match_keyword('if'):
                else_block.children.append(self._parse_if())
            else:
                self._expect(TokenType.BLOCK_START)
                while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
                    stmt = self._parse_statement()
                    if stmt:
                        else_block.children.append(stmt)
                self._expect(TokenType.BLOCK_END)
            node.children.append(else_block)

        return node

    def _parse_while(self) -> ASTNode:
        self._expect(TokenType.PAREN_START)
        condition = self._parse_expression()
        self._expect(TokenType.PAREN_END)

        node = ASTNode('while', value={'condition': condition}, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_for(self) -> ASTNode:
        """Parse for loop - supports both syntaxes:

        Python-style: for (i in range(0, n)) { }
        C-style: for (int i = 0; i < n; i = i + 1) { }
                 for (i = 0; i < n; i++) { }
        """
        self._expect(TokenType.PAREN_START)

        # Detect C-style by checking for semicolons in the for header
        # Look ahead without consuming tokens
        is_c_style = self._detect_c_style_for()

        if is_c_style:
            # C-style: for (init; condition; update) { }
            return self._parse_c_style_for()
        else:
            # Python-style: for (var in range(start, end)) { }
            return self._parse_python_style_for()

    def _detect_c_style_for(self) -> bool:
        """Detect if this is a C-style for loop by looking for semicolons."""
        # Scan the tokens list directly without modifying self.pos
        pos = self.pos
        paren_depth = 1

        while pos < len(self.tokens) and paren_depth > 0:
            token = self.tokens[pos]
            if token.type == TokenType.PAREN_START:
                paren_depth += 1
            elif token.type == TokenType.PAREN_END:
                paren_depth -= 1
            elif token.type == TokenType.SEMICOLON and paren_depth == 1:
                # Found semicolon at top level - C-style
                return True
            elif token.type == TokenType.KEYWORD and token.value == 'in':
                # Found 'in' keyword - Python-style
                return False
            pos += 1

        return False  # Default to Python-style

    def _parse_c_style_for(self) -> ASTNode:
        """Parse C-style for loop: for (init; condition; update) { }"""
        # Parse init statement
        init = None
        if not self._check(TokenType.SEMICOLON):
            # Check if it's a typed declaration: int i = 0
            if self._check(TokenType.KEYWORD) and self._peek().value in ('int', 'float', 'string', 'bool', 'dynamic'):
                type_name = self._advance().value
                var_name = self._advance().value
                self._expect(TokenType.EQUALS)
                value = self._parse_expression()
                init = ASTNode('c_for_init', value={
                    'type': type_name,
                    'var': var_name,
                    'value': value
                })
            else:
                # Simple assignment: i = 0
                var_name = self._advance().value
                self._expect(TokenType.EQUALS)
                value = self._parse_expression()
                init = ASTNode('c_for_init', value={
                    'type': None,
                    'var': var_name,
                    'value': value
                })

        self._expect(TokenType.SEMICOLON)

        # Parse condition
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()

        self._expect(TokenType.SEMICOLON)

        # Parse update statement
        update = None
        if not self._check(TokenType.PAREN_END):
            # Could be: i = i + 1, i++, ++i, i += 1
            update = self._parse_c_for_update()

        self._expect(TokenType.PAREN_END)

        node = ASTNode('c_for', value={
            'init': init,
            'condition': condition,
            'update': update
        }, children=[])

        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_c_for_update(self) -> ASTNode:
        """Parse the update part of a C-style for loop.

        Supports: i = i + 1, i++, ++i, i += 1, i -= 1
        """
        # Check for prefix increment/decrement: ++i or --i (as single PLUS_PLUS/MINUS_MINUS token)
        if self._check(TokenType.PLUS_PLUS):
            self._advance()
            var_name = self._advance().value
            return ASTNode('c_for_update', value={'var': var_name, 'op': 'increment'})
        elif self._check(TokenType.MINUS_MINUS):
            self._advance()
            var_name = self._advance().value
            return ASTNode('c_for_update', value={'var': var_name, 'op': 'decrement'})

        # Regular variable assignment or postfix
        var_name = self._advance().value

        # Check for postfix increment/decrement: i++ or i-- (as single PLUS_PLUS/MINUS_MINUS token)
        if self._check(TokenType.PLUS_PLUS):
            self._advance()
            return ASTNode('c_for_update', value={'var': var_name, 'op': 'increment'})
        elif self._check(TokenType.MINUS_MINUS):
            self._advance()
            return ASTNode('c_for_update', value={'var': var_name, 'op': 'decrement'})
        # i += value
        elif self._check(TokenType.PLUS):
            self._advance()
            if self._check(TokenType.EQUALS):
                self._advance()
                value = self._parse_expression()
                return ASTNode('c_for_update', value={'var': var_name, 'op': 'add', 'value': value})
        # i -= value
        elif self._check(TokenType.MINUS):
            self._advance()
            if self._check(TokenType.EQUALS):
                self._advance()
                value = self._parse_expression()
                return ASTNode('c_for_update', value={'var': var_name, 'op': 'subtract', 'value': value})

        # Regular assignment: i = expression
        if self._check(TokenType.EQUALS):
            self._advance()
            value = self._parse_expression()
            return ASTNode('c_for_update', value={'var': var_name, 'op': 'assign', 'value': value})

        # Just the variable (shouldn't happen but handle it)
        return ASTNode('c_for_update', value={'var': var_name, 'op': 'none'})

    def _parse_python_style_for(self) -> ASTNode:
        """Parse Python-style for loop: for (i in range(...)) { } or for (item in collection) { }

        Supports:
            for (i in range(n)) { }           - 0 to n-1
            for (i in range(start, end)) { }  - start to end-1
            for (i in range(start, end, step)) { }
            for (item in collection) { }      - iterate over list/vector
            for (item in @global_collection) { } - iterate over global
        """
        var_name = self._advance().value
        self._expect(TokenType.KEYWORD)  # 'in'

        # Check if this is range() or collection iteration
        is_range = False
        if self._check(TokenType.KEYWORD) and self._peek().value == 'range':
            self._advance()  # consume 'range' keyword
            is_range = True
        elif self._check(TokenType.IDENTIFIER) and self._peek().value == 'range':
            self._advance()  # consume 'range' identifier
            is_range = True

        # If not range, parse as collection iteration
        if not is_range:
            iterable = self._parse_expression()
            self._expect(TokenType.PAREN_END)

            node = ASTNode('foreach', value={'var': var_name, 'iterable': iterable}, children=[])
            self._expect(TokenType.BLOCK_START)

            while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
                stmt = self._parse_statement()
                if stmt:
                    node.children.append(stmt)

            self._expect(TokenType.BLOCK_END)
            return node

        self._expect(TokenType.PAREN_START)
        first_arg = self._parse_expression()

        # Check if there are more arguments
        start = None
        end = None
        step = None

        if self._check(TokenType.COMMA):
            # range(start, end) or range(start, end, step)
            self._advance()  # consume comma
            start = first_arg
            end = self._parse_expression()

            # Optional step parameter
            if self._check(TokenType.COMMA):
                self._advance()  # consume comma
                step = self._parse_expression()
        else:
            # range(n) - single argument means 0 to n-1
            start = ASTNode('literal', value={'type': 'int', 'value': 0})
            end = first_arg

        self._expect(TokenType.PAREN_END)
        self._expect(TokenType.PAREN_END)

        node = ASTNode('for', value={'var': var_name, 'start': start, 'end': end, 'step': step}, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_foreach(self) -> ASTNode:
        """Parse foreach loop - supports both syntaxes:

        Traditional: foreach (var in iterable) { }
        New 'as' syntax: foreach iterable as var { }
        """
        # Check if this is the new 'as' syntax or traditional syntax
        if self._check(TokenType.PAREN_START):
            # Traditional syntax: foreach (var in iterable) { }
            self._expect(TokenType.PAREN_START)
            var_name = self._advance().value
            self._match_keyword('in')
            iterable = self._parse_expression()
            self._expect(TokenType.PAREN_END)
        else:
            # NEW: 'as' syntax: foreach iterable as var { }
            iterable = self._parse_expression()
            if self._check(TokenType.AS):
                self._advance()  # consume 'as'
            else:
                self._match_keyword('as')  # try keyword match as fallback
            var_name = self._advance().value

        node = ASTNode('foreach', value={'var': var_name, 'iterable': iterable}, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_switch(self) -> ASTNode:
        self._expect(TokenType.PAREN_START)
        value = self._parse_expression()
        self._expect(TokenType.PAREN_END)

        node = ASTNode('switch', value={'value': value}, children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._match_keyword('case'):
                case_value = self._parse_expression()
                self._expect(TokenType.COLON)
                case_node = ASTNode('case', value={'value': case_value}, children=[])

                while not self._check_keyword('case') and not self._check_keyword('default') and not self._check(TokenType.BLOCK_END):
                    stmt = self._parse_statement()
                    if stmt:
                        case_node.children.append(stmt)
                    if self._check_keyword('break'):
                        break

                node.children.append(case_node)
            elif self._match_keyword('default'):
                self._expect(TokenType.COLON)
                default_node = ASTNode('default', children=[])

                while not self._check(TokenType.BLOCK_END):
                    stmt = self._parse_statement()
                    if stmt:
                        default_node.children.append(stmt)

                node.children.append(default_node)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_return(self) -> ASTNode:
        """Parse return statement, supporting multiple values for shuffled functions.

        Syntax:
            return;                    // Return None
            return value;              // Return single value
            return a, b, c;            // Return multiple values (for shuffled)
        """
        values = []
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.BLOCK_END):
            values.append(self._parse_expression())

            # Check for comma-separated return values (shuffled return)
            while self._check(TokenType.COMMA):
                self._advance()  # consume comma
                values.append(self._parse_expression())

        self._match(TokenType.SEMICOLON)

        if len(values) == 0:
            return ASTNode('return', value=None)
        elif len(values) == 1:
            return ASTNode('return', value=values[0])
        else:
            # Multiple return values - create tuple return
            return ASTNode('return', value={'multiple': True, 'values': values})

    def _parse_super_function(self) -> ASTNode:
        """Parse super-function for .cssl-pl payload files.

        Syntax:
            #$run(initFunction);           // Call function at load time
            #$exec(setup());               // Execute expression at load time
            #$printl("Payload loaded");    // Print at load time

        These are pre-execution hooks that run when payload() loads the file.
        """
        token = self._advance()  # Get the SUPER_FUNC token
        super_name = token.value  # e.g., "#$run", "#$exec", "#$printl"

        # Parse the arguments
        self._expect(TokenType.PAREN_START)
        args = []
        if not self._check(TokenType.PAREN_END):
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())
        self._expect(TokenType.PAREN_END)
        self._match(TokenType.SEMICOLON)

        return ASTNode('super_func', value={'name': super_name, 'args': args})

    def _parse_try(self) -> ASTNode:
        node = ASTNode('try', children=[])

        try_block = ASTNode('try-block', children=[])
        self._expect(TokenType.BLOCK_START)
        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                try_block.children.append(stmt)
        self._expect(TokenType.BLOCK_END)
        node.children.append(try_block)

        if self._match_keyword('catch'):
            error_var = None
            if self._match(TokenType.PAREN_START):
                error_var = self._advance().value
                self._expect(TokenType.PAREN_END)

            catch_block = ASTNode('catch-block', value={'error_var': error_var}, children=[])
            self._expect(TokenType.BLOCK_START)
            while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
                stmt = self._parse_statement()
                if stmt:
                    catch_block.children.append(stmt)
            self._expect(TokenType.BLOCK_END)
            node.children.append(catch_block)

        return node

    def _parse_await(self) -> ASTNode:
        """Parse await statement: await expression;"""
        expr = self._parse_expression()
        self._match(TokenType.SEMICOLON)
        return ASTNode('await', value=expr)

    def _parse_action_block(self) -> ASTNode:
        """Parse an action block { ... } containing statements for createcmd"""
        node = ASTNode('action_block', children=[])
        self._expect(TokenType.BLOCK_START)

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            # Check for define statements inside action block
            if self._match_keyword('define'):
                node.children.append(self._parse_define())
            # Check for typed function definitions (nested functions)
            elif self._looks_like_function_declaration():
                node.children.append(self._parse_typed_function())
            else:
                stmt = self._parse_statement()
                if stmt:
                    node.children.append(stmt)

        self._expect(TokenType.BLOCK_END)
        return node

    def _parse_injection_filter(self) -> Optional[list]:
        """Parse injection filter(s): [type::helper=value] or [f1][f2][f3]...

        Returns a list of filter dictionaries to support chained filters.
        """
        if not self._check(TokenType.BRACKET_START):
            return None

        filters = []

        # Parse multiple consecutive filter brackets
        while self._match(TokenType.BRACKET_START):
            filter_info = {}
            # Parse type::helper=value patterns within this bracket
            while not self._check(TokenType.BRACKET_END) and not self._is_at_end():
                if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                    filter_type = self._advance().value
                    if self._match(TokenType.DOUBLE_COLON):
                        helper = self._advance().value
                        if self._match(TokenType.EQUALS):
                            value = self._parse_expression()
                            filter_info[f'{filter_type}::{helper}'] = value
                        else:
                            filter_info[f'{filter_type}::{helper}'] = True
                    else:
                        filter_info['type'] = filter_type
                elif self._check(TokenType.COMMA):
                    self._advance()
                else:
                    break

            self._expect(TokenType.BRACKET_END)
            if filter_info:
                filters.append(filter_info)

        return filters if filters else None

    def _parse_expression_statement(self) -> Optional[ASTNode]:
        expr = self._parse_expression()

        # === TUPLE UNPACKING: a, b, c = shuffled_func() ===
        # Check if we have comma-separated identifiers before =
        if expr.type == 'identifier' and self._check(TokenType.COMMA):
            targets = [expr]
            while self._match(TokenType.COMMA):
                next_expr = self._parse_expression()
                if next_expr.type == 'identifier':
                    targets.append(next_expr)
                else:
                    # Not a simple identifier list, this is something else
                    # Restore and fall through to normal parsing
                    break

            # Check if followed by =
            if self._match(TokenType.EQUALS):
                value = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return ASTNode('tuple_assignment', value={'targets': targets, 'value': value})

        # === BASIC INJECTION: <== (replace target with source) ===
        if self._match(TokenType.INJECT_LEFT):
            # Check if this is a createcmd injection with a code block
            is_createcmd = (
                expr.type == 'call' and
                expr.value.get('callee') and
                expr.value.get('callee').type == 'identifier' and
                expr.value.get('callee').value == 'createcmd'
            )

            if is_createcmd and self._check(TokenType.BLOCK_START):
                action_block = self._parse_action_block()
                self._match(TokenType.SEMICOLON)
                return ASTNode('createcmd_inject', value={'command_call': expr, 'action': action_block})
            else:
                # Check for injection filter [type::helper=value]
                filter_info = self._parse_injection_filter()
                source = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return ASTNode('inject', value={'target': expr, 'source': source, 'mode': 'replace', 'filter': filter_info})

        # === PLUS INJECTION: +<== (copy & add to target) ===
        if self._match(TokenType.INJECT_PLUS_LEFT):
            filter_info = self._parse_injection_filter()
            source = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('inject', value={'target': expr, 'source': source, 'mode': 'add', 'filter': filter_info})

        # === MINUS INJECTION: -<== or -<==[n] (move & remove from source) ===
        if self._match(TokenType.INJECT_MINUS_LEFT):
            # Check for indexed deletion: -<==[n] (only numbers, not filters)
            remove_index = None
            if self._check(TokenType.BRACKET_START):
                # Peek ahead to see if this is an index [n] or a filter [type::helper=...]
                # Only consume if it's a simple number index
                saved_pos = self.pos
                self._advance()  # consume [
                if self._check(TokenType.NUMBER):
                    remove_index = int(self._advance().value)
                    self._expect(TokenType.BRACKET_END)
                else:
                    # Not a number - restore position for filter parsing
                    self.pos = saved_pos

            filter_info = self._parse_injection_filter()
            source = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('inject', value={'target': expr, 'source': source, 'mode': 'move', 'filter': filter_info, 'index': remove_index})

        # === CODE INFUSION: <<== (inject code into function) ===
        if self._match(TokenType.INFUSE_LEFT):
            if self._check(TokenType.BLOCK_START):
                code_block = self._parse_action_block()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'code': code_block, 'mode': 'replace'})
            else:
                source = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'source': source, 'mode': 'replace'})

        # === CODE INFUSION PLUS: +<<== (add code to function) ===
        if self._match(TokenType.INFUSE_PLUS_LEFT):
            if self._check(TokenType.BLOCK_START):
                code_block = self._parse_action_block()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'code': code_block, 'mode': 'add'})
            else:
                source = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'source': source, 'mode': 'add'})

        # === CODE INFUSION MINUS: -<<== or -<<==[n] (remove code from function) ===
        if self._match(TokenType.INFUSE_MINUS_LEFT):
            # Check for indexed deletion: -<<==[n] (only numbers)
            remove_index = None
            if self._check(TokenType.BRACKET_START):
                # Peek ahead to see if this is an index [n] or something else
                saved_pos = self.pos
                self._advance()  # consume [
                if self._check(TokenType.NUMBER):
                    remove_index = int(self._advance().value)
                    self._expect(TokenType.BRACKET_END)
                else:
                    # Not a number - restore position
                    self.pos = saved_pos

            if self._check(TokenType.BLOCK_START):
                code_block = self._parse_action_block()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'code': code_block, 'mode': 'remove', 'index': remove_index})
            else:
                source = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                return ASTNode('infuse', value={'target': expr, 'source': source, 'mode': 'remove', 'index': remove_index})

        # === RIGHT-SIDE OPERATORS ===

        # === BASIC RECEIVE: ==> (move source to target) ===
        if self._match(TokenType.INJECT_RIGHT):
            filter_info = self._parse_injection_filter()
            target = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('receive', value={'source': expr, 'target': target, 'mode': 'replace', 'filter': filter_info})

        # === PLUS RECEIVE: ==>+ (copy source to target) ===
        if self._match(TokenType.INJECT_PLUS_RIGHT):
            filter_info = self._parse_injection_filter()
            target = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('receive', value={'source': expr, 'target': target, 'mode': 'add', 'filter': filter_info})

        # === MINUS RECEIVE: -==> (move & remove from source) ===
        if self._match(TokenType.INJECT_MINUS_RIGHT):
            filter_info = self._parse_injection_filter()
            target = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('receive', value={'source': expr, 'target': target, 'mode': 'move', 'filter': filter_info})

        # === CODE INFUSION RIGHT: ==>> ===
        if self._match(TokenType.INFUSE_RIGHT):
            target = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('infuse_right', value={'source': expr, 'target': target, 'mode': 'replace'})

        # === FLOW OPERATORS ===
        if self._match(TokenType.FLOW_RIGHT):
            target = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('flow', value={'source': expr, 'target': target})

        if self._match(TokenType.FLOW_LEFT):
            source = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('flow', value={'source': source, 'target': expr})

        # === BASIC ASSIGNMENT ===
        if self._match(TokenType.EQUALS):
            value = self._parse_expression()
            self._match(TokenType.SEMICOLON)
            return ASTNode('assignment', value={'target': expr, 'value': value})

        self._match(TokenType.SEMICOLON)
        return ASTNode('expression', value=expr)

    def _parse_expression(self) -> ASTNode:
        return self._parse_or()

    def _parse_or(self) -> ASTNode:
        left = self._parse_and()

        while self._match(TokenType.OR) or self._match_keyword('or'):
            right = self._parse_and()
            left = ASTNode('binary', value={'op': 'or', 'left': left, 'right': right})

        return left

    def _parse_and(self) -> ASTNode:
        left = self._parse_comparison()

        while self._match(TokenType.AND) or self._match_keyword('and'):
            right = self._parse_comparison()
            left = ASTNode('binary', value={'op': 'and', 'left': left, 'right': right})

        return left

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_term()

        while True:
            if self._match(TokenType.COMPARE_EQ):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '==', 'left': left, 'right': right})
            elif self._match(TokenType.COMPARE_NE):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '!=', 'left': left, 'right': right})
            elif self._match(TokenType.COMPARE_LT):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '<', 'left': left, 'right': right})
            elif self._match(TokenType.COMPARE_GT):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '>', 'left': left, 'right': right})
            elif self._match(TokenType.COMPARE_LE):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '<=', 'left': left, 'right': right})
            elif self._match(TokenType.COMPARE_GE):
                right = self._parse_term()
                left = ASTNode('binary', value={'op': '>=', 'left': left, 'right': right})
            elif self._check(TokenType.KEYWORD) and self._peek().value == 'in':
                # 'in' operator for containment: item in list
                self._advance()  # consume 'in'
                right = self._parse_term()
                left = ASTNode('binary', value={'op': 'in', 'left': left, 'right': right})
            else:
                break

        return left

    def _parse_term(self) -> ASTNode:
        left = self._parse_factor()

        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_factor()
                left = ASTNode('binary', value={'op': '+', 'left': left, 'right': right})
            elif self._match(TokenType.MINUS):
                right = self._parse_factor()
                left = ASTNode('binary', value={'op': '-', 'left': left, 'right': right})
            else:
                break

        return left

    def _parse_factor(self) -> ASTNode:
        left = self._parse_unary()

        while True:
            if self._match(TokenType.MULTIPLY):
                right = self._parse_unary()
                left = ASTNode('binary', value={'op': '*', 'left': left, 'right': right})
            elif self._match(TokenType.DIVIDE):
                right = self._parse_unary()
                left = ASTNode('binary', value={'op': '/', 'left': left, 'right': right})
            elif self._match(TokenType.MODULO):
                right = self._parse_unary()
                left = ASTNode('binary', value={'op': '%', 'left': left, 'right': right})
            else:
                break

        return left

    def _parse_unary(self) -> ASTNode:
        if self._match(TokenType.NOT) or self._match_keyword('not'):
            operand = self._parse_unary()
            return ASTNode('unary', value={'op': 'not', 'operand': operand})
        if self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return ASTNode('unary', value={'op': '-', 'operand': operand})
        # Prefix increment: ++i
        if self._match(TokenType.PLUS_PLUS):
            operand = self._parse_unary()
            return ASTNode('increment', value={'op': 'prefix', 'operand': operand})
        # Prefix decrement: --i
        if self._match(TokenType.MINUS_MINUS):
            operand = self._parse_unary()
            return ASTNode('decrement', value={'op': 'prefix', 'operand': operand})
        if self._match(TokenType.AMPERSAND):
            # Reference operator: &variable or &@module
            operand = self._parse_unary()
            return ASTNode('reference', value=operand)

        # Non-null assertion: *$var, *@module, *identifier
        # Also type exclusion filter: *[type]expr - exclude type from return
        if self._check(TokenType.MULTIPLY):
            next_token = self._peek(1)

            # Check for type exclusion filter: *[string], *[int], etc.
            if next_token and next_token.type == TokenType.BRACKET_START:
                self._advance()  # consume *
                self._advance()  # consume [
                exclude_type = self._advance().value  # get type name
                self._expect(TokenType.BRACKET_END)
                operand = self._parse_unary()
                return ASTNode('type_exclude_assert', value={'exclude_type': exclude_type, 'operand': operand})

            # Non-null assertion when followed by $ (shared ref), @ (global), or identifier
            if next_token and next_token.type in (TokenType.SHARED_REF, TokenType.AT, TokenType.IDENTIFIER):
                self._advance()  # consume *
                operand = self._parse_unary()
                return ASTNode('non_null_assert', value={'operand': operand})

        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        # Handle 'this->' member access
        if self._check(TokenType.KEYWORD) and self._current().value == 'this':
            self._advance()  # consume 'this'
            if self._match(TokenType.FLOW_RIGHT):  # ->
                member = self._advance().value
                node = ASTNode('this_access', value={'member': member})
                # Continue to check for calls, member access, indexing
                while True:
                    if self._match(TokenType.PAREN_START):
                        # Method call: this->method()
                        args, kwargs = self._parse_call_arguments()
                        self._expect(TokenType.PAREN_END)
                        node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                    elif self._match(TokenType.DOT):
                        # Chained access: this->obj.method
                        member = self._advance().value
                        node = ASTNode('member_access', value={'object': node, 'member': member})
                    elif self._match(TokenType.BRACKET_START):
                        # Index access: this->arr[0]
                        index = self._parse_expression()
                        self._expect(TokenType.BRACKET_END)
                        node = ASTNode('index_access', value={'object': node, 'index': index})
                    elif self._match(TokenType.FLOW_RIGHT):
                        # Chained this->a->b style access
                        member = self._advance().value
                        node = ASTNode('this_access', value={'member': member, 'object': node})
                    else:
                        break
                return node
            else:
                # Just 'this' keyword alone - return as identifier for now
                return ASTNode('identifier', value='this')

        # Handle 'new ClassName(args)' or 'new @ClassName(args)' instantiation
        if self._check(TokenType.KEYWORD) and self._current().value == 'new':
            self._advance()  # consume 'new'
            # Check for @ prefix (global class reference)
            is_global_ref = False
            if self._check(TokenType.AT):
                self._advance()  # consume @
                is_global_ref = True
            class_name = self._advance().value  # get class name
            args = []
            kwargs = {}
            if self._match(TokenType.PAREN_START):
                args, kwargs = self._parse_call_arguments()
                self._expect(TokenType.PAREN_END)
            node = ASTNode('new', value={'class': class_name, 'args': args, 'kwargs': kwargs, 'is_global_ref': is_global_ref})
            # Continue to check for member access, calls on the new object
            while True:
                if self._match(TokenType.DOT):
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                    if self._match(TokenType.PAREN_START):
                        args, kwargs = self._parse_call_arguments()
                        self._expect(TokenType.PAREN_END)
                        node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.BRACKET_START):
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        if self._match(TokenType.AT):
            # Check for @* (global non-null reference): @*name
            is_non_null = False
            if self._check(TokenType.MULTIPLY):
                self._advance()  # consume *
                is_non_null = True

            node = self._parse_module_reference()

            # Wrap in non_null_assert if @* was used
            if is_non_null:
                node = ASTNode('non_null_assert', value={'operand': node, 'is_global': True})

            # Continue to check for calls, indexing, member access on module refs
            while True:
                if self._match(TokenType.PAREN_START):
                    # Function call on module ref: @Module.method() - with kwargs support
                    args, kwargs = self._parse_call_arguments()
                    self._expect(TokenType.PAREN_END)
                    node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.DOT):
                    # Member access: @Module.property
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                elif self._match(TokenType.BRACKET_START):
                    # Index access: @Module[index]
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        if self._check(TokenType.SELF_REF):
            # s@<name> self-reference to global struct
            token = self._advance()
            node = ASTNode('self_ref', value=token.value, line=token.line, column=token.column)
            # Check for function call: s@Backend.Loop.Start() - with kwargs support
            if self._match(TokenType.PAREN_START):
                args, kwargs = self._parse_call_arguments()
                self._expect(TokenType.PAREN_END)
                node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
            return node

        if self._check(TokenType.GLOBAL_REF):
            # r@<name> global variable reference/declaration
            token = self._advance()
            node = ASTNode('global_ref', value=token.value, line=token.line, column=token.column)
            # Check for member access, calls, indexing - with kwargs support
            while True:
                if self._match(TokenType.PAREN_START):
                    args, kwargs = self._parse_call_arguments()
                    self._expect(TokenType.PAREN_END)
                    node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.DOT):
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                elif self._match(TokenType.BRACKET_START):
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        if self._check(TokenType.SHARED_REF):
            # $<name> shared object reference
            token = self._advance()
            node = ASTNode('shared_ref', value=token.value, line=token.line, column=token.column)
            # Check for member access, calls, indexing - with kwargs support
            while True:
                if self._match(TokenType.PAREN_START):
                    args, kwargs = self._parse_call_arguments()
                    self._expect(TokenType.PAREN_END)
                    node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.DOT):
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                elif self._match(TokenType.BRACKET_START):
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        if self._check(TokenType.CAPTURED_REF):
            # %<name> captured reference (captures value at infusion registration time)
            token = self._advance()
            node = ASTNode('captured_ref', value=token.value, line=token.line, column=token.column)
            # Check for member access, calls, indexing - with kwargs support
            while True:
                if self._match(TokenType.PAREN_START):
                    args, kwargs = self._parse_call_arguments()
                    self._expect(TokenType.PAREN_END)
                    node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.DOT):
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                elif self._match(TokenType.BRACKET_START):
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        # v4.1.0: Cross-language instance reference: cpp$ClassName, py$Object
        if self._check(TokenType.LANG_INSTANCE_REF):
            token = self._advance()
            ref = token.value  # {'lang': 'cpp', 'instance': 'ClassName'}
            node = ASTNode('lang_instance_ref', value=ref, line=token.line, column=token.column)
            # Check for member access, calls, indexing
            while True:
                if self._match(TokenType.PAREN_START):
                    args, kwargs = self._parse_call_arguments()
                    self._expect(TokenType.PAREN_END)
                    node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
                elif self._match(TokenType.DOT):
                    member = self._advance().value
                    node = ASTNode('member_access', value={'object': node, 'member': member})
                elif self._match(TokenType.BRACKET_START):
                    index = self._parse_expression()
                    self._expect(TokenType.BRACKET_END)
                    node = ASTNode('index_access', value={'object': node, 'index': index})
                else:
                    break
            return node

        if self._check(TokenType.NUMBER):
            return ASTNode('literal', value=self._advance().value)

        if self._check(TokenType.STRING):
            return ASTNode('literal', value=self._advance().value)

        if self._check(TokenType.BOOLEAN):
            return ASTNode('literal', value=self._advance().value)

        if self._check(TokenType.NULL):
            self._advance()
            return ASTNode('literal', value=None)

        # NEW: Type literals (list, dict) - create empty instances
        if self._check(TokenType.TYPE_LITERAL):
            type_name = self._advance().value
            return ASTNode('type_literal', value=type_name)

        if self._match(TokenType.PAREN_START):
            expr = self._parse_expression()
            self._expect(TokenType.PAREN_END)
            return expr

        if self._match(TokenType.BLOCK_START):
            # Distinguish between object literal { key = value } and action block { expr; }
            # Object literal: starts with IDENTIFIER = or STRING =
            # Action block: starts with expression (captured_ref, call, literal, etc.)
            if self._is_object_literal():
                return self._parse_object()
            else:
                return self._parse_action_block_expression()

        if self._match(TokenType.BRACKET_START):
            return self._parse_array()

        if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
            return self._parse_identifier_or_call()

        return ASTNode('literal', value=None)

    def _parse_module_reference(self) -> ASTNode:
        """Parse @name, handling method calls and property access.

        @name alone -> module_ref
        @name.method() -> call with member_access
        @name.property -> member_access
        """
        # Get base name
        name = self._advance().value
        node = ASTNode('module_ref', value=name)

        # Continue to handle member access, calls, and indexing
        while True:
            if self._match(TokenType.DOT):
                member = self._advance().value
                node = ASTNode('member_access', value={'object': node, 'member': member})
            elif self._match(TokenType.PAREN_START):
                # Function call - use _parse_call_arguments for kwargs support
                args, kwargs = self._parse_call_arguments()
                self._expect(TokenType.PAREN_END)
                node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
            elif self._match(TokenType.BRACKET_START):
                # Index access
                index = self._parse_expression()
                self._expect(TokenType.BRACKET_END)
                node = ASTNode('index_access', value={'object': node, 'index': index})
            else:
                break

        return node

    def _parse_call_arguments(self) -> tuple:
        """Parse function call arguments, supporting both positional and named (key=value).

        Returns: (args, kwargs) where:
            args = list of positional argument expressions
            kwargs = dict of {name: expression} for named arguments
        """
        args = []
        kwargs = {}

        while not self._check(TokenType.PAREN_END) and not self._is_at_end():
            # Check for named argument: identifier = expression
            if self._check(TokenType.IDENTIFIER):
                saved_pos = self.pos  # Save token position
                name_token = self._advance()

                if self._check(TokenType.EQUALS):
                    # Named argument: name=value
                    self._advance()  # consume =
                    value = self._parse_expression()
                    kwargs[name_token.value] = value
                else:
                    # Not named, restore and parse as expression
                    self.pos = saved_pos  # Restore token position
                    args.append(self._parse_expression())
            else:
                args.append(self._parse_expression())

            if not self._check(TokenType.PAREN_END):
                self._expect(TokenType.COMMA)

        return args, kwargs

    def _parse_identifier_or_call(self) -> ASTNode:
        name = self._advance().value

        # Check for namespace syntax: json::read, string::cut, etc.
        if self._match(TokenType.DOUBLE_COLON):
            if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
                namespace_member = self._advance().value
                name = f"{name}::{namespace_member}"

        # Check for instance<"name"> syntax - gets/creates shared instance
        if name == 'instance' and self._check(TokenType.COMPARE_LT):
            self._advance()  # consume <
            # Expect string literal for instance name
            if self._check(TokenType.STRING):
                instance_name = self._advance().value
            elif self._check(TokenType.IDENTIFIER):
                instance_name = self._advance().value
            else:
                raise CSSLParserError("Expected instance name (string or identifier)", self._current_line())
            self._expect(TokenType.COMPARE_GT)  # consume >
            return ASTNode('instance_ref', value=instance_name)

        # Check for type generic instantiation: stack<string>, vector<int>, map<string, int>, etc.
        # This creates a new instance of the type with the specified element type
        if name in TYPE_GENERICS and self._check(TokenType.COMPARE_LT):
            self._advance()  # consume <
            element_type = 'dynamic'
            value_type = None  # For map<K, V>

            if self._check(TokenType.KEYWORD) or self._check(TokenType.IDENTIFIER):
                element_type = self._advance().value

            # Check for second type parameter (map<K, V>)
            if name == 'map' and self._check(TokenType.COMMA):
                self._advance()  # consume ,
                if self._check(TokenType.KEYWORD) or self._check(TokenType.IDENTIFIER):
                    value_type = self._advance().value
                else:
                    value_type = 'dynamic'

            self._expect(TokenType.COMPARE_GT)  # consume >

            # Check for inline initialization: map<K,V>{"key": "value", ...}
            init_values = None
            if self._check(TokenType.BLOCK_START):
                self._advance()  # consume {
                init_values = {}

                while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
                    # Parse key
                    if self._check(TokenType.STRING):
                        key = self._advance().value
                    elif self._check(TokenType.IDENTIFIER):
                        key = self._advance().value
                    else:
                        key = str(self._parse_expression().value) if hasattr(self._parse_expression(), 'value') else 'key'

                    # Expect : or =
                    if self._check(TokenType.COLON):
                        self._advance()
                    elif self._check(TokenType.EQUALS):
                        self._advance()

                    # Parse value
                    value = self._parse_expression()
                    init_values[key] = value

                    # Optional comma
                    if self._check(TokenType.COMMA):
                        self._advance()

                self._expect(TokenType.BLOCK_END)  # consume }

            # Check for array-style initialization: vector<int>[1, 2, 3], array<string>["a", "b"]
            elif self._check(TokenType.BRACKET_START):
                self._advance()  # consume [
                init_values = []

                while not self._check(TokenType.BRACKET_END) and not self._is_at_end():
                    init_values.append(self._parse_expression())

                    # Optional comma
                    if self._check(TokenType.COMMA):
                        self._advance()

                self._expect(TokenType.BRACKET_END)  # consume ]

            return ASTNode('type_instantiation', value={
                'type': name,
                'element_type': element_type,
                'value_type': value_type,
                'init_values': init_values
            })

        # Check for type-parameterized function call: OpenFind<string>(0) or OpenFind<dynamic, "name">
        if name in TYPE_PARAM_FUNCTIONS and self._check(TokenType.COMPARE_LT):
            self._advance()  # consume <
            type_param = 'dynamic'
            param_name = None  # Optional: named parameter search

            if self._check(TokenType.KEYWORD) or self._check(TokenType.IDENTIFIER):
                type_param = self._advance().value

            # Check for second parameter: OpenFind<type, "name">
            if self._check(TokenType.COMMA):
                self._advance()  # consume comma
                # Expect a string literal for the parameter name
                if self._check(TokenType.STRING):
                    param_name = self._advance().value
                elif self._check(TokenType.IDENTIFIER):
                    param_name = self._advance().value

            self._expect(TokenType.COMPARE_GT)  # consume >

            # Must be followed by ()
            if self._check(TokenType.PAREN_START):
                self._advance()  # consume (
                args = []
                while not self._check(TokenType.PAREN_END):
                    args.append(self._parse_expression())
                    if not self._check(TokenType.PAREN_END):
                        self._expect(TokenType.COMMA)
                self._expect(TokenType.PAREN_END)

                # Return as typed function call
                return ASTNode('typed_call', value={
                    'name': name,
                    'type_param': type_param,
                    'param_name': param_name,  # Named parameter for OpenFind
                    'args': args
                })

        node = ASTNode('identifier', value=name)

        while True:
            if self._match(TokenType.DOT):
                member = self._advance().value
                node = ASTNode('member_access', value={'object': node, 'member': member})
            elif self._match(TokenType.PAREN_START):
                args, kwargs = self._parse_call_arguments()
                self._expect(TokenType.PAREN_END)
                node = ASTNode('call', value={'callee': node, 'args': args, 'kwargs': kwargs})
            elif self._match(TokenType.BRACKET_START):
                index = self._parse_expression()
                self._expect(TokenType.BRACKET_END)
                node = ASTNode('index_access', value={'object': node, 'index': index})
            # Postfix increment: i++
            elif self._match(TokenType.PLUS_PLUS):
                node = ASTNode('increment', value={'op': 'postfix', 'operand': node})
            # Postfix decrement: i--
            elif self._match(TokenType.MINUS_MINUS):
                node = ASTNode('decrement', value={'op': 'postfix', 'operand': node})
            else:
                break

        return node

    def _is_object_literal(self) -> bool:
        """Check if current position is an object literal { key = value } vs action block { expr; }

        Object literal: { name = value; } or { "key" = value; }
        Action block: { %version; } or { "1.0.0" } or { call(); }
        """
        # Empty block is action block
        if self._check(TokenType.BLOCK_END):
            return False

        # Save position for lookahead
        saved_pos = self.pos

        # Check if it looks like key = value pattern
        is_object = False
        if self._check(TokenType.IDENTIFIER) or self._check(TokenType.STRING):
            self._advance()  # skip key
            if self._check(TokenType.EQUALS):
                # Looks like object literal: { key = ...
                is_object = True

        # Restore position
        self.pos = saved_pos
        return is_object

    def _parse_action_block_expression(self) -> ASTNode:
        """Parse an action block expression: { expr; expr2; } returns last value

        Used for: v <== { %version; } or v <== { "1.0.0" }
        """
        children = []

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            # Parse statement or expression
            if (self._check(TokenType.IDENTIFIER) or self._check(TokenType.AT) or
                self._check(TokenType.CAPTURED_REF) or self._check(TokenType.SHARED_REF) or
                self._check(TokenType.GLOBAL_REF) or self._check(TokenType.SELF_REF) or
                self._check(TokenType.STRING) or self._check(TokenType.NUMBER) or
                self._check(TokenType.BOOLEAN) or self._check(TokenType.NULL) or
                self._check(TokenType.PAREN_START)):
                # Parse as expression and wrap in expression node for _execute_node
                expr = self._parse_expression()
                self._match(TokenType.SEMICOLON)
                children.append(ASTNode('expression', value=expr))
            elif self._check(TokenType.KEYWORD):
                # Parse as statement
                stmt = self._parse_statement()
                if stmt:
                    children.append(stmt)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return ASTNode('action_block', children=children)

    def _parse_object(self) -> ASTNode:
        properties = {}

        while not self._check(TokenType.BLOCK_END) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER) or self._check(TokenType.STRING):
                key = self._advance().value
                self._expect(TokenType.EQUALS)
                value = self._parse_expression()
                properties[key] = value
                self._match(TokenType.SEMICOLON)
                self._match(TokenType.COMMA)
            else:
                self._advance()

        self._expect(TokenType.BLOCK_END)
        return ASTNode('object', value=properties)

    def _parse_array(self) -> ASTNode:
        elements = []

        while not self._check(TokenType.BRACKET_END) and not self._is_at_end():
            elements.append(self._parse_expression())
            if not self._check(TokenType.BRACKET_END):
                self._expect(TokenType.COMMA)

        self._expect(TokenType.BRACKET_END)
        return ASTNode('array', value=elements)

    def _parse_value(self) -> Any:
        if self._check(TokenType.STRING):
            return self._advance().value
        if self._check(TokenType.NUMBER):
            return self._advance().value
        if self._check(TokenType.BOOLEAN):
            return self._advance().value
        if self._check(TokenType.NULL):
            self._advance()
            return None
        if self._check(TokenType.IDENTIFIER) or self._check(TokenType.KEYWORD):
            return self._advance().value
        return None

    def _check_keyword(self, keyword: str) -> bool:
        return self._current().type == TokenType.KEYWORD and self._current().value == keyword


def parse_cssl(source: str) -> ASTNode:
    """Parse CSSL source code into an AST - auto-detects service vs program format"""
    lexer = CSSLLexer(source)
    tokens = lexer.tokenize()
    parser = CSSLParser(tokens, lexer.source_lines)

    # Auto-detect: if first token is '{', it's a service file
    # Otherwise treat as standalone program (whitespace is already filtered by lexer)
    if tokens and tokens[0].type == TokenType.BLOCK_START:
        return parser.parse()  # Service file format
    else:
        return parser.parse_program()  # Standalone program format


def parse_cssl_program(source: str) -> ASTNode:
    """Parse standalone CSSL program (no service wrapper) into an AST"""
    lexer = CSSLLexer(source)
    tokens = lexer.tokenize()
    parser = CSSLParser(tokens, lexer.source_lines)
    return parser.parse_program()


def tokenize_cssl(source: str) -> List[Token]:
    """Tokenize CSSL source code (useful for syntax highlighting)"""
    lexer = CSSLLexer(source)
    return lexer.tokenize()


# Export public API
__all__ = [
    'TokenType', 'Token', 'ASTNode',
    'CSSLLexer', 'CSSLParser', 'CSSLSyntaxError',
    'parse_cssl', 'parse_cssl_program', 'tokenize_cssl',
    'KEYWORDS', 'TYPE_LITERALS'
]
