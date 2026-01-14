# IncludeCPP

Use C++ code in Python. Write your C++ functions and classes, IncludeCPP generates the Python bindings automatically.

```bash
pip install IncludeCPP
```

## Quick Start

### 1. Create a Project

```bash
mkdir myproject && cd myproject
includecpp init
```

This creates:
- `cpp.proj` - your project settings
- `include/` - put your C++ files here
- `plugins/` - binding files go here (auto-generated)

### 2. Write Some C++

Create `include/math.cpp`:

```cpp
namespace includecpp {

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

}
```

Your code must be inside `namespace includecpp`. Everything outside is ignored.

### 3. Generate Bindings

```bash
includecpp plugin math include/math.cpp
```

This scans your C++ and creates `plugins/math.cp` with the binding instructions.

### 4. Build

```bash
includecpp rebuild
```

Compiles your C++ into a Python module.

### 5. Use in Python

```python
from includecpp import math

print(math.add(2, 3))       # 5
print(math.multiply(4, 5))  # 20
```

Done. Your C++ code works in Python.

---

## Classes

C++ classes work the same way:

```cpp
// include/calculator.cpp
#include <vector>

namespace includecpp {

class Calculator {
public:
    Calculator() : result(0) {}

    void add(int x) { result += x; }
    void subtract(int x) { result -= x; }
    int getResult() { return result; }
    void reset() { result = 0; }

private:
    int result;
};

}
```

Generate and build:

```bash
includecpp plugin calculator include/calculator.cpp
includecpp rebuild
```

Use in Python:

```python
from includecpp import calculator

calc = calculator.Calculator()
calc.add(10)
calc.add(5)
calc.subtract(3)
print(calc.getResult())  # 12
```

---

## Development Workflow

When you're actively working on your C++:

```bash
# Regenerate bindings AND rebuild in one command
includecpp auto math

# Fast rebuild (skips unchanged files, ~0.4s when nothing changed)
includecpp rebuild --fast

# Rebuild everything from scratch
includecpp rebuild --clean
```

---

## CLI Commands

| Command | What it does |
|---------|-------------|
| `init` | Create project structure |
| `plugin <name> <file.cpp>` | Generate bindings from C++ |
| `auto <name>` | Regenerate bindings + rebuild |
| `rebuild` | Compile all modules |
| `rebuild --fast` | Fast incremental build |
| `rebuild --clean` | Full clean rebuild |
| `get <name>` | Show module's API |

---

## Project Configuration

The `cpp.proj` file controls your build:

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

---

## Plugin Files (.cp)

The `.cp` files tell IncludeCPP what to expose. They're auto-generated, but you can edit them:

```
SOURCE(calculator.cpp) calculator

PUBLIC(
    calculator CLASS(Calculator) {
        CONSTRUCTOR()
        METHOD(add)
        METHOD(subtract)
        METHOD(getResult)
        METHOD(reset)
    }
)
```

Common directives:
- `CLASS(Name)` - expose a class
- `METHOD(name)` - expose a method
- `FUNC(name)` - expose a function
- `FIELD(name)` - expose a member variable
- `CONSTRUCTOR()` or `CONSTRUCTOR(int, string)` - expose constructor

---

## Requirements

- Python 3.9+
- C++ compiler (g++, clang++, or MSVC)
- CMake

pybind11 is installed automatically.

---

## More Help

```bash
includecpp --doc           # Full documentation
includecpp --changelog     # Version history
includecpp <command> --help
```

---

## Experimental Features

IncludeCPP also includes experimental features that are still in development:

- **CSSL** - A scripting language for runtime code manipulation
- **AI Commands** - OpenAI-powered code analysis (`includecpp ai`)
- **CPPY** - Python to C++ conversion (`includecpp cppy`)

These are hidden by default. To enable them:

```bash
includecpp settings
```

Check "Enable Experimental Features" and save.

Warning: Experimental features may have bugs or breaking changes between versions.

---

## Issues

Report bugs at: https://github.com/liliassg/IncludeCPP/issues

```bash
includecpp bug    # Quick bug report
includecpp update # Update to latest version
```
