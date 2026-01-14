# IncludeCPP Documentation

Version 4.2.0 | C++ Performance in Python, Zero Hassle

---

## Overview

IncludeCPP lets you write C++ code and use it directly in Python. It auto-generates pybind11 bindings from your C++ source files.

```bash
pip install IncludeCPP
```

---

## Project Setup

### Initialize Project

```bash
includecpp init
```

Creates:
- `cpp.proj` - project configuration
- `include/` - C++ source files
- `plugins/` - generated binding definitions

### Project Structure

```
myproject/
  cpp.proj           # Configuration
  include/           # Your C++ code
    math.cpp
    utils.cpp
  plugins/           # Auto-generated binding files
    math.cp
    utils.cp
```

---

## Writing C++ Code

All C++ code must be in `namespace includecpp`:

```cpp
// include/math.cpp
#include <vector>

namespace includecpp {

class Calculator {
public:
    int add(int a, int b) { return a + b; }
    int multiply(int a, int b) { return a * b; }
private:
    int memory = 0;
};

int square(int x) { return x * x; }

}  // namespace includecpp
```

The parser only scans code inside `namespace includecpp`. Everything else is ignored.

---

## Generate Bindings

Create a plugin file from C++ source:

```bash
includecpp plugin math include/math.cpp
```

This creates `plugins/math.cp` with binding instructions.

### Plugin File Format

```
SOURCE(math.cpp) math

PUBLIC(
    math CLASS(Calculator) {
        CONSTRUCTOR()
        METHOD(add)
        METHOD(multiply)
    }

    math FUNC(square)
)
```

### Key Directives

| Directive | Description |
|-----------|-------------|
| `SOURCE(file) name` | Link source to module name |
| `CLASS(Name)` | Expose a class |
| `STRUCT(Name)` | Expose a struct |
| `FUNC(name)` | Expose a free function |
| `METHOD(name)` | Expose a class method |
| `METHOD_CONST(name, sig)` | Overloaded method |
| `CONSTRUCTOR(args)` | Expose constructor |
| `FIELD(name)` | Expose member variable |
| `DEPENDS(mod1, mod2)` | Module dependencies |

---

## Build

```bash
includecpp rebuild
```

Compiles C++ into Python extension (`.pyd` on Windows, `.so` on Linux/Mac).

### Build Flags

```bash
includecpp rebuild                  # Standard build
includecpp rebuild --clean          # Full rebuild, clear caches
includecpp rebuild --fast           # Fast incremental (~0.4s if unchanged)
includecpp rebuild --verbose        # Show compiler output
includecpp rebuild -m crypto        # Build specific module only
includecpp rebuild -j 8             # Use 8 parallel jobs
```

### Build Times

| Scenario | Time |
|----------|------|
| No changes (--fast) | ~0.4s |
| Source changed | ~5-10s |
| Full rebuild | ~30s |

---

## Using in Python

### Direct Import

```python
from includecpp import math

calc = math.Calculator()
print(calc.add(2, 3))      # 5
print(math.square(4))      # 16
```

### CppApi

```python
from includecpp import CppApi

api = CppApi()
math = api.include("math")
```

---

## Development Workflow

### Auto Command

For active development:

```bash
includecpp auto math
```

Regenerates `.cp` file from source and rebuilds in one command.

### Rebuild All

```bash
includecpp auto --all
includecpp auto --all -x tests    # All except tests
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `init` | Create project structure |
| `plugin <name> <files>` | Generate .cp from C++ sources |
| `auto <plugin>` | Regenerate .cp and rebuild |
| `rebuild` / `build` | Compile all modules |
| `get <module>` | Show module API |
| `fix <module>` | Analyze C++ code for issues |
| `--doc` | Show this documentation |
| `--doc "term"` | Search documentation |
| `--changelog` | Show latest changes |

---

## Advanced Features

### Overloaded Methods

```
MODULE CLASS(Circle) {
    METHOD_CONST(intersects, const Circle&)
    METHOD_CONST(intersects, const Rect&)
}
```

### Template Instantiation

```
MODULE TEMPLATE_FUNC(maximum) TYPES(int, float, double)
```

Generates: `maximum_int`, `maximum_float`, `maximum_double`

### Module Dependencies

```
DEPENDS(math_utils, geometry)
```

Ensures dependent modules build first.

---

## Configuration

### cpp.proj

```json
{
  "project": "MyProject",
  "include": "/include",
  "plugins": "/plugins",
  "compiler": {
    "standard": "c++17",
    "optimization": "O3"
  }
}
```

### Options

| Option | Description |
|--------|-------------|
| `project` | Project name |
| `include` | C++ source directory |
| `plugins` | Plugin file directory |
| `compiler.standard` | C++ standard (c++11/14/17/20) |
| `compiler.optimization` | Optimization level (O0-O3) |

---

## CSSL Scripting

IncludeCPP includes CSSL (C-Style Scripting Language) for runtime scripting.

### Basic Usage

```python
from includecpp import CSSL

CSSL.run('''
    printl("Hello from CSSL!");

    int x = 10;
    for (i in range(0, 5)) {
        x = x + i;
    }
    printl(x);
''')
```

### Parameters and Return

```python
result = CSSL.run('''
    int a = parameter.get(0);
    int b = parameter.get(1);
    parameter.return(a + b);
''', 5, 3)

print(result)  # 8
```

### Shared Objects

Share Python objects with CSSL:

```python
class Counter:
    def __init__(self):
        self.value = 100

counter = Counter()
cssl = CSSL.CsslLang()
cssl.share(counter, "cnt")

cssl.run('''
    $cnt.value = $cnt.value - 10;
    printl($cnt.value);  // 90
''')

print(counter.value)  # 90 - Changed!
```

### Object Syntax

| Syntax | Description |
|--------|-------------|
| `$name` | Access shared object |
| `@name` | Access global variable |
| `%name` | Access captured variable |
| `this->` | Access instance member |

---

## CSSL Data Types

### Primitives

```cssl
int x = 42;
float pi = 3.14;
string name = "CSSL";
bool active = true;
dynamic any = "flexible";
```

### Collections

```cssl
array<int> arr;
arr.push(1);
arr.push(2);

vector<string> vec;
stack<int> s;
map<string, int> ages;
list items = [1, 2, 3];
dict data = {"a": 1};
```

---

## CSSL Control Flow

```cssl
// If/elif/else
if (x > 10) {
    printl("big");
} elif (x > 5) {
    printl("medium");
} else {
    printl("small");
}

// For loop
for (i in range(0, 10)) {
    printl(i);
}

// Foreach
foreach (item in items) {
    printl(item);
}

// While
while (count < 5) {
    count = count + 1;
}
```

---

## CSSL Functions

```cssl
// Basic function
void greet(string name) {
    printl("Hello, " + name + "!");
}

// Return value
int add(int a, int b) {
    return a + b;
}

// Typed function (C++ style)
int multiply(int a, int b) {
    return a * b;
}
```

---

## CSSL Classes

```cssl
class Person {
    string name;
    int age;

    constr Person(string n, int a) {
        this->name = n;
        this->age = a;
    }

    void greet() {
        printl("I am " + this->name);
    }
}

instance = new Person("Alice", 30);
instance.greet();
```

### Inheritance

```cssl
class Employee : extends Person {
    string role;

    constr Employee(string n, int a, string r) {
        super(n, a);
        this->role = r;
    }
}
```

---

## CSSL Injection Operators

### Data Movement

```cssl
target <== source;     // Move data (replace)
target +<== source;    // Copy & add
target -<== source;    // Move & remove from source
```

### Code Infusion

```cssl
myFunc() <<== {
    printl("Injected!");
};

myFunc() +<<== {
    printl("Added!");
};
```

---

## CSSL Modules

### Create Module

```python
mod = CSSL.module('''
    int add(int a, int b) {
        return a + b;
    }
''')

result = mod.call("add", 2, 3)  # 5
```

### Makemodule

```python
math_mod = CSSL.makemodule('''
    int square(int x) {
        return x * x;
    }
''')

print(math_mod.square(5))  # 25
```

---

## Pythonize CSSL Classes

Return CSSL classes to Python:

```python
greeter = cssl.run('''
    class Greeter {
        string name;

        Greeter(string n) {
            this->name = n;
        }

        string sayHello() {
            return "Hello, " + this->name;
        }
    }

    instance = new Greeter("World");
    pyclass = python::pythonize(instance);
    parameter.return(pyclass);
''')

print(greeter.sayHello())  # "Hello, World"
```

---

## Universal Instances

Shared containers across CSSL and Python:

```python
cssl.run('''
    instance<"myData"> data;
    data.value = 42;
''')

container = cssl.getInstance("myData")
print(container.value)  # 42
```

---

## AI Integration

### Setup

```bash
includecpp ai key sk-your-api-key
includecpp ai enable
```

### Commands

```bash
includecpp ai ask "where is collision detection?"
includecpp ai edit "add logging" --file utils.cpp
includecpp ai optimize mymodule
includecpp fix --ai mymodule
```

---

## CPPY Code Conversion

### Python to C++

```bash
includecpp cppy convert math.py --cpp
```

### C++ to Python

```bash
includecpp cppy convert utils.cpp --py
```

### AI-Assisted

```bash
includecpp cppy convert complex.py --cpp --ai
```

---

## Requirements

- Python 3.8+
- C++ compiler (g++, clang++, MSVC)
- pybind11 (installed automatically)
- CMake

---

## Support

Report issues: https://github.com/liliassg/IncludeCPP/issues

```bash
includecpp bug    # Report an issue
includecpp update # Update IncludeCPP
```
