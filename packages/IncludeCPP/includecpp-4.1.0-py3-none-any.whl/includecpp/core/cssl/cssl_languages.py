"""
CSSL Multi-Language Support Module

Provides language definitions, syntax transformers, and cross-language instance access
for Python, Java, C#, C++, and JavaScript.

Usage:
    @py = libinclude("python")
    cpp = libinclude("c++")

    define my_func() : supports @py {
        # Python syntax here
        for i in range(10):
            print(i)
    }

    class MyClass : extends cpp$BaseClass {
        // C++ style
    }
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class SupportedLanguage(Enum):
    """Enumeration of supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    CSHARP = "c#"
    CPP = "c++"
    JAVASCRIPT = "javascript"


@dataclass
class LanguageSyntax:
    """Defines syntax rules for a programming language"""
    name: str
    statement_terminator: str      # ";" or "\n"
    uses_braces: bool              # True for {}, False for indentation (Python)
    boolean_true: str              # "True", "true"
    boolean_false: str             # "False", "false"
    null_keyword: str              # "None", "null", "nullptr"
    variable_keywords: List[str]   # ["let", "const", "var"] for JS
    function_keywords: List[str]   # ["def"] for Python, ["function"] for JS
    class_keywords: List[str]      # ["class"]
    constructor_name: str          # "__init__" for Python, "constructor" for JS
    print_function: str            # "print", "console.log", "System.out.println"
    comment_single: str            # "#" or "//"
    comment_multi_start: str       # "/*" or '"""'
    comment_multi_end: str         # "*/" or '"""'


@dataclass
class LanguageSupport:
    """
    Language support object returned by libinclude().

    Provides syntax transformation and cross-language instance sharing.
    """
    language: SupportedLanguage
    syntax: LanguageSyntax
    name: str
    _instances: Dict[str, Any] = field(default_factory=dict)
    _transformer: Optional['LanguageTransformer'] = field(default=None, repr=False)

    def share(self, name: str, instance: Any) -> None:
        """
        Share an instance for cross-language access.

        Usage in CSSL:
            cpp.share("Engine", myEngine)

        Then accessible via:
            cpp$Engine
        """
        self._instances[name] = instance

    def get_instance(self, name: str) -> Any:
        """
        Get a shared instance by name.

        Usage in CSSL:
            engine = cpp.get("Engine")
        """
        return self._instances.get(name)

    def has_instance(self, name: str) -> bool:
        """Check if an instance is shared"""
        return name in self._instances

    def list_instances(self) -> List[str]:
        """List all shared instance names"""
        return list(self._instances.keys())

    def remove_instance(self, name: str) -> bool:
        """Remove a shared instance"""
        if name in self._instances:
            del self._instances[name]
            return True
        return False

    def get_transformer(self) -> 'LanguageTransformer':
        """Get the syntax transformer for this language"""
        if self._transformer is None:
            self._transformer = create_transformer(self)
        return self._transformer

    def __getattr__(self, name: str) -> Any:
        """Allow method-like access for convenience"""
        if name == 'get':
            return self.get_instance
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


class LanguageTransformer:
    """
    Base class for transforming language-specific syntax to CSSL.

    Each language has a specific transformer that handles its unique syntax.
    """

    def __init__(self, lang_support: LanguageSupport):
        self.lang = lang_support
        self.syntax = lang_support.syntax

    def transform_source(self, source: str) -> str:
        """Transform source code from target language to CSSL"""
        raise NotImplementedError("Subclasses must implement transform_source")

    def _common_replacements(self, stmt: str) -> str:
        """Apply common replacements across all languages"""
        return stmt


class PythonTransformer(LanguageTransformer):
    """
    Transforms Python syntax to CSSL.

    Handles:
    - Indentation-based blocks -> brace-based blocks
    - def -> define
    - print() -> printl()
    - self. -> this->
    - None -> null
    - Python-style for loops -> CSSL for loops
    """

    def transform_source(self, source: str) -> str:
        lines = source.split('\n')
        result = []
        indent_stack = [0]  # Stack of indentation levels

        for i, line in enumerate(lines):
            stripped = line.lstrip()

            # Handle empty lines and comments
            if not stripped:
                continue
            if stripped.startswith('#'):
                # Convert Python comment to CSSL comment
                result.append('// ' + stripped[1:].lstrip())
                continue

            current_indent = len(line) - len(stripped)

            # Handle dedent - close blocks
            while len(indent_stack) > 1 and current_indent < indent_stack[-1]:
                indent_stack.pop()
                result.append(' ' * indent_stack[-1] + '}')

            # Transform the statement
            transformed = self._transform_statement(stripped)

            # Check if line opens a new block (ends with :)
            if stripped.rstrip().endswith(':'):
                # Remove trailing colon, add opening brace
                transformed = transformed.rstrip(':').rstrip() + ' {'
                # Get next line's indentation
                next_indent = self._get_next_indent(lines, i)
                if next_indent > current_indent:
                    indent_stack.append(next_indent)
            elif not transformed.endswith(('{', '}', ';')):
                # Add semicolon if not a block statement
                transformed += ';'

            result.append(' ' * current_indent + transformed)

        # Close remaining open blocks
        while len(indent_stack) > 1:
            indent_stack.pop()
            result.append(' ' * indent_stack[-1] + '}')

        return '\n'.join(result)

    def _transform_statement(self, stmt: str) -> str:
        """Transform a single Python statement to CSSL"""

        # def func(args): -> define func(args)
        if stmt.startswith('def '):
            match = re.match(r'def\s+(\w+)\s*\((.*?)\)\s*:', stmt)
            if match:
                func_name = match.group(1)
                params = match.group(2)
                return f"define {func_name}({params})"

        # class ClassName(Parent): -> class ClassName : extends Parent
        if stmt.startswith('class '):
            match = re.match(r'class\s+(\w+)(?:\s*\((.*?)\))?\s*:', stmt)
            if match:
                class_name = match.group(1)
                parent = match.group(2)
                if parent and parent.strip():
                    return f"class {class_name} : extends {parent}"
                return f"class {class_name}"

        # if condition: -> if (condition)
        if stmt.startswith('if '):
            match = re.match(r'if\s+(.+?):', stmt)
            if match:
                condition = match.group(1)
                return f"if ({condition})"

        # elif condition: -> elif (condition)
        if stmt.startswith('elif '):
            match = re.match(r'elif\s+(.+?):', stmt)
            if match:
                condition = match.group(1)
                return f"elif ({condition})"

        # else: -> else
        if stmt.strip() == 'else:':
            return 'else'

        # while condition: -> while (condition)
        if stmt.startswith('while '):
            match = re.match(r'while\s+(.+?):', stmt)
            if match:
                condition = match.group(1)
                return f"while ({condition})"

        # for i in range(n): -> for (i in range(0, n))
        # for i in iterable: -> for (i in iterable)
        if stmt.startswith('for '):
            match = re.match(r'for\s+(\w+)\s+in\s+(.+?):', stmt)
            if match:
                var = match.group(1)
                iterable = match.group(2)
                # Handle range with single argument
                range_match = re.match(r'range\s*\(\s*(\d+)\s*\)', iterable)
                if range_match:
                    return f"for ({var} in range(0, {range_match.group(1)}))"
                return f"for ({var} in {iterable})"

        # try: -> try
        if stmt.strip() == 'try:':
            return 'try'

        # except Exception as e: -> catch (e)
        if stmt.startswith('except'):
            match = re.match(r'except\s*(?:\w+\s+)?(?:as\s+(\w+))?\s*:', stmt)
            if match:
                var = match.group(1) or 'e'
                return f"catch ({var})"

        # finally: -> finally
        if stmt.strip() == 'finally:':
            return 'finally'

        # return value -> return value
        # (no change needed, just ensure semicolon is added)

        # Common replacements
        stmt = self._apply_replacements(stmt)

        return stmt

    def _apply_replacements(self, stmt: str) -> str:
        """Apply common Python to CSSL replacements"""
        # print() -> printl()
        stmt = re.sub(r'\bprint\s*\(', 'printl(', stmt)

        # self. -> this->
        stmt = stmt.replace('self.', 'this->')

        # None -> null
        stmt = re.sub(r'\bNone\b', 'null', stmt)

        # True/False stay the same (CSSL supports both cases)

        # __init__ -> constructor handling would be done at class level

        return stmt

    def _get_next_indent(self, lines: List[str], current_idx: int) -> int:
        """Get indentation of next non-empty, non-comment line"""
        for i in range(current_idx + 1, len(lines)):
            line = lines[i]
            stripped = line.lstrip()
            if stripped and not stripped.startswith('#'):
                return len(line) - len(stripped)
        return 0


class JavaScriptTransformer(LanguageTransformer):
    """
    Transforms JavaScript syntax to CSSL.

    Handles:
    - let/const/var -> dynamic
    - function name() -> define name()
    - console.log() -> printl()
    - null/undefined -> null
    - Arrow functions (basic support)
    """

    def transform_source(self, source: str) -> str:
        lines = source.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Convert comments
            if stripped.startswith('//'):
                result.append(stripped)
                continue

            # Transform the line
            transformed = self._transform_line(stripped)
            result.append(transformed)

        return '\n'.join(result)

    def _transform_line(self, line: str) -> str:
        """Transform a single JavaScript line to CSSL"""

        # function name(args) { -> define name(args) {
        match = re.match(r'function\s+(\w+)\s*\((.*?)\)\s*\{?', line)
        if match:
            func_name = match.group(1)
            params = match.group(2)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            return f"define {func_name}({params}){suffix}"

        # const/let/var name = value; -> dynamic name = value;
        match = re.match(r'(const|let|var)\s+(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(2)
            value = match.group(3)
            return f"dynamic {var_name} = {value}"

        # const/let/var name; -> dynamic name;
        match = re.match(r'(const|let|var)\s+(\w+)\s*;', line)
        if match:
            var_name = match.group(2)
            return f"dynamic {var_name};"

        # class Name { or class Name extends Parent {
        match = re.match(r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{?', line)
        if match:
            class_name = match.group(1)
            parent = match.group(2)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            if parent:
                return f"class {class_name} : extends {parent}{suffix}"
            return f"class {class_name}{suffix}"

        # constructor(args) { -> constr ClassName(args) {
        if line.strip().startswith('constructor'):
            match = re.match(r'constructor\s*\((.*?)\)\s*\{?', line)
            if match:
                params = match.group(1)
                suffix = ' {' if line.rstrip().endswith('{') else ''
                return f"constr __init__({params}){suffix}"

        # Common replacements
        line = self._apply_replacements(line)

        return line

    def _apply_replacements(self, line: str) -> str:
        """Apply common JavaScript to CSSL replacements"""
        # console.log() -> printl()
        line = re.sub(r'console\.log\s*\(', 'printl(', line)

        # console.error() -> error()
        line = re.sub(r'console\.error\s*\(', 'error(', line)

        # console.warn() -> warn()
        line = re.sub(r'console\.warn\s*\(', 'warn(', line)

        # true/false -> True/False
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bfalse\b', 'False', line)

        # undefined -> null
        line = re.sub(r'\bundefined\b', 'null', line)

        # this. stays as this. (CSSL uses this-> but also supports this.)

        return line


class JavaTransformer(LanguageTransformer):
    """
    Transforms Java syntax to CSSL.

    Handles:
    - System.out.println() -> printl()
    - true/false -> True/False
    - String -> string (optional lowercase)
    """

    def transform_source(self, source: str) -> str:
        lines = source.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('//'):
                result.append(stripped)
                continue

            transformed = self._transform_line(stripped)
            result.append(transformed)

        return '\n'.join(result)

    def _transform_line(self, line: str) -> str:
        """Transform a single Java line to CSSL"""

        # public/private/protected static void main(String[] args)
        # -> define main(args)
        match = re.match(r'(?:public|private|protected)?\s*(?:static)?\s*(?:void|int|String|boolean|float|double)\s+(\w+)\s*\((.*?)\)\s*\{?', line)
        if match:
            func_name = match.group(1)
            params = match.group(2)
            # Simplify Java params: String[] args -> args
            params = re.sub(r'\w+(?:\[\])?\s+(\w+)', r'\1', params)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            return f"define {func_name}({params}){suffix}"

        # class Name extends Parent implements Interface {
        match = re.match(r'(?:public\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+\w+(?:,\s*\w+)*)?\s*\{?', line)
        if match:
            class_name = match.group(1)
            parent = match.group(2)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            if parent:
                return f"class {class_name} : extends {parent}{suffix}"
            return f"class {class_name}{suffix}"

        # Common replacements
        line = self._apply_replacements(line)

        return line

    def _apply_replacements(self, line: str) -> str:
        """Apply common Java to CSSL replacements"""
        # System.out.println() -> printl()
        line = re.sub(r'System\.out\.println\s*\(', 'printl(', line)
        line = re.sub(r'System\.out\.print\s*\(', 'print(', line)

        # true/false -> True/False
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bfalse\b', 'False', line)

        # String -> string (CSSL convention)
        line = re.sub(r'\bString\b', 'string', line)

        return line


class CSharpTransformer(LanguageTransformer):
    """
    Transforms C# syntax to CSSL.

    Handles:
    - Console.WriteLine() -> printl()
    - true/false -> True/False
    - var -> dynamic
    """

    def transform_source(self, source: str) -> str:
        lines = source.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('//'):
                result.append(stripped)
                continue

            transformed = self._transform_line(stripped)
            result.append(transformed)

        return '\n'.join(result)

    def _transform_line(self, line: str) -> str:
        """Transform a single C# line to CSSL"""

        # public/private void MethodName(params) {
        match = re.match(r'(?:public|private|protected|internal)?\s*(?:static)?\s*(?:async)?\s*(?:void|int|string|bool|float|double|var|dynamic|\w+)\s+(\w+)\s*\((.*?)\)\s*\{?', line)
        if match and not line.strip().startswith('class'):
            func_name = match.group(1)
            params = match.group(2)
            # Simplify C# params: string name -> name
            params = re.sub(r'\w+\s+(\w+)', r'\1', params)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            return f"define {func_name}({params}){suffix}"

        # class Name : Parent {
        match = re.match(r'(?:public\s+)?(?:partial\s+)?class\s+(\w+)(?:\s*:\s*(\w+))?\s*\{?', line)
        if match:
            class_name = match.group(1)
            parent = match.group(2)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            if parent:
                return f"class {class_name} : extends {parent}{suffix}"
            return f"class {class_name}{suffix}"

        # var name = value; -> dynamic name = value;
        match = re.match(r'var\s+(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(1)
            value = match.group(2)
            return f"dynamic {var_name} = {value}"

        # Common replacements
        line = self._apply_replacements(line)

        return line

    def _apply_replacements(self, line: str) -> str:
        """Apply common C# to CSSL replacements"""
        # Console.WriteLine() -> printl()
        line = re.sub(r'Console\.WriteLine\s*\(', 'printl(', line)
        line = re.sub(r'Console\.Write\s*\(', 'print(', line)

        # true/false -> True/False
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bfalse\b', 'False', line)

        return line


class CppTransformer(LanguageTransformer):
    """
    Transforms C++ syntax to CSSL.

    Handles:
    - std::cout << x << std::endl; -> printl(x);
    - nullptr -> null
    - auto -> dynamic
    - true/false -> True/False
    """

    def transform_source(self, source: str) -> str:
        lines = source.split('\n')
        result = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('//'):
                result.append(stripped)
                continue

            transformed = self._transform_line(stripped)
            result.append(transformed)

        return '\n'.join(result)

    def _transform_line(self, line: str) -> str:
        """Transform a single C++ line to CSSL"""

        # void/int/etc functionName(params) {
        match = re.match(r'(?:virtual\s+)?(?:static\s+)?(?:inline\s+)?(?:void|int|string|bool|float|double|auto|\w+)\s+(\w+)\s*\((.*?)\)\s*(?:const)?\s*(?:override)?\s*\{?', line)
        if match and not any(kw in line for kw in ['class ', 'struct ', 'namespace ']):
            func_name = match.group(1)
            params = match.group(2)
            # Simplify C++ params: const std::string& name -> name
            params = re.sub(r'(?:const\s+)?(?:std::)?(?:\w+)(?:&|\*)?\s+(\w+)', r'\1', params)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            return f"define {func_name}({params}){suffix}"

        # class Name : public Parent {
        match = re.match(r'class\s+(\w+)(?:\s*:\s*(?:public|protected|private)\s+(\w+))?\s*\{?', line)
        if match:
            class_name = match.group(1)
            parent = match.group(2)
            suffix = ' {' if line.rstrip().endswith('{') else ''
            if parent:
                return f"class {class_name} : extends {parent}{suffix}"
            return f"class {class_name}{suffix}"

        # auto name = value; -> dynamic name = value;
        match = re.match(r'auto\s+(\w+)\s*=\s*(.+)', line)
        if match:
            var_name = match.group(1)
            value = match.group(2)
            return f"dynamic {var_name} = {value}"

        # Common replacements
        line = self._apply_replacements(line)

        return line

    def _apply_replacements(self, line: str) -> str:
        """Apply common C++ to CSSL replacements"""
        # std::cout << x << std::endl; -> printl(x);
        match = re.match(r'std::cout\s*<<\s*(.*?)\s*<<\s*std::endl\s*;', line)
        if match:
            content = match.group(1)
            return f'printl({content});'

        match = re.match(r'std::cout\s*<<\s*(.*?)\s*;', line)
        if match:
            content = match.group(1)
            return f'print({content});'

        # true/false -> True/False
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bfalse\b', 'False', line)

        # nullptr -> null
        line = re.sub(r'\bnullptr\b', 'null', line)

        # auto -> dynamic (for standalone declarations)
        line = re.sub(r'\bauto\b', 'dynamic', line)

        return line


# Language Registry
LANGUAGE_DEFINITIONS: Dict[str, LanguageSupport] = {}


def register_language(lang_id: str, lang_support: LanguageSupport) -> None:
    """Register a language definition"""
    LANGUAGE_DEFINITIONS[lang_id.lower()] = lang_support


def get_language(lang_id: str) -> Optional[LanguageSupport]:
    """Get a language definition by ID"""
    return LANGUAGE_DEFINITIONS.get(lang_id.lower())


def list_languages() -> List[str]:
    """List all registered language IDs"""
    return list(LANGUAGE_DEFINITIONS.keys())


def create_transformer(lang_support: LanguageSupport) -> LanguageTransformer:
    """Create the appropriate transformer for a language"""
    if lang_support.language == SupportedLanguage.PYTHON:
        return PythonTransformer(lang_support)
    elif lang_support.language == SupportedLanguage.JAVASCRIPT:
        return JavaScriptTransformer(lang_support)
    elif lang_support.language == SupportedLanguage.JAVA:
        return JavaTransformer(lang_support)
    elif lang_support.language == SupportedLanguage.CSHARP:
        return CSharpTransformer(lang_support)
    elif lang_support.language == SupportedLanguage.CPP:
        return CppTransformer(lang_support)
    else:
        return LanguageTransformer(lang_support)


def _init_languages() -> None:
    """Initialize all built-in language definitions"""

    # Python
    python_syntax = LanguageSyntax(
        name="Python",
        statement_terminator="\n",
        uses_braces=False,
        boolean_true="True",
        boolean_false="False",
        null_keyword="None",
        variable_keywords=[],
        function_keywords=["def"],
        class_keywords=["class"],
        constructor_name="__init__",
        print_function="print",
        comment_single="#",
        comment_multi_start='"""',
        comment_multi_end='"""'
    )
    python_support = LanguageSupport(
        language=SupportedLanguage.PYTHON,
        syntax=python_syntax,
        name="Python"
    )
    register_language("python", python_support)
    register_language("py", python_support)

    # Java
    java_syntax = LanguageSyntax(
        name="Java",
        statement_terminator=";",
        uses_braces=True,
        boolean_true="true",
        boolean_false="false",
        null_keyword="null",
        variable_keywords=["int", "String", "boolean", "float", "double", "var"],
        function_keywords=["public", "private", "protected", "static", "void"],
        class_keywords=["class", "interface", "enum"],
        constructor_name="<classname>",
        print_function="System.out.println",
        comment_single="//",
        comment_multi_start="/*",
        comment_multi_end="*/"
    )
    java_support = LanguageSupport(
        language=SupportedLanguage.JAVA,
        syntax=java_syntax,
        name="Java"
    )
    register_language("java", java_support)

    # C#
    csharp_syntax = LanguageSyntax(
        name="C#",
        statement_terminator=";",
        uses_braces=True,
        boolean_true="true",
        boolean_false="false",
        null_keyword="null",
        variable_keywords=["int", "string", "bool", "float", "double", "var", "dynamic"],
        function_keywords=["public", "private", "protected", "static", "void", "async"],
        class_keywords=["class", "interface", "struct", "enum"],
        constructor_name="<classname>",
        print_function="Console.WriteLine",
        comment_single="//",
        comment_multi_start="/*",
        comment_multi_end="*/"
    )
    csharp_support = LanguageSupport(
        language=SupportedLanguage.CSHARP,
        syntax=csharp_syntax,
        name="C#"
    )
    register_language("c#", csharp_support)
    register_language("csharp", csharp_support)

    # C++
    cpp_syntax = LanguageSyntax(
        name="C++",
        statement_terminator=";",
        uses_braces=True,
        boolean_true="true",
        boolean_false="false",
        null_keyword="nullptr",
        variable_keywords=["int", "string", "bool", "float", "double", "auto", "const"],
        function_keywords=["void", "int", "string", "bool", "float", "double", "auto"],
        class_keywords=["class", "struct"],
        constructor_name="<classname>",
        print_function="std::cout",
        comment_single="//",
        comment_multi_start="/*",
        comment_multi_end="*/"
    )
    cpp_support = LanguageSupport(
        language=SupportedLanguage.CPP,
        syntax=cpp_syntax,
        name="C++"
    )
    register_language("c++", cpp_support)
    register_language("cpp", cpp_support)

    # JavaScript
    js_syntax = LanguageSyntax(
        name="JavaScript",
        statement_terminator=";",
        uses_braces=True,
        boolean_true="true",
        boolean_false="false",
        null_keyword="null",
        variable_keywords=["let", "const", "var"],
        function_keywords=["function", "async"],
        class_keywords=["class"],
        constructor_name="constructor",
        print_function="console.log",
        comment_single="//",
        comment_multi_start="/*",
        comment_multi_end="*/"
    )
    js_support = LanguageSupport(
        language=SupportedLanguage.JAVASCRIPT,
        syntax=js_syntax,
        name="JavaScript"
    )
    register_language("javascript", js_support)
    register_language("js", js_support)


# Initialize languages on module load
_init_languages()


# Export public API
__all__ = [
    'SupportedLanguage',
    'LanguageSyntax',
    'LanguageSupport',
    'LanguageTransformer',
    'PythonTransformer',
    'JavaScriptTransformer',
    'JavaTransformer',
    'CSharpTransformer',
    'CppTransformer',
    'register_language',
    'get_language',
    'list_languages',
    'create_transformer',
    'LANGUAGE_DEFINITIONS',
]
