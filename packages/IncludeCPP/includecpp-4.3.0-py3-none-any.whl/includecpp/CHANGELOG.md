# IncludeCPP Changelog

## v4.3.0 (2026-01-08)

### New Features
- Payload namespace support: `payload("mylib", "libname")` loads definitions into `libname::`
- Auto-extension for payloads: `payload("engine")` finds `engine.cssl-pl`
- Namespaced class instantiation: `new Engine::GameEngine()`

### Bug Fixes
- Fixed try/catch parsing (catch was interpreted as function call)
- Added finally block support for try/catch
- Division by zero now throws error instead of returning 0
- Modulo by zero now throws error
- List index out of bounds now throws error with helpful message
- Dict key not found now throws error
- try/catch now catches Python exceptions
- Fixed `embedded &$PyObject::method` replacement (this-> now works)

---

## v4.2.5 (2026-01-08)

### New Features
- Added `embedded` keyword for immediate function/class replacement
- Added `switch` for open parameters with pattern matching

### Bug Fixes
- Fixed `OpenFind<type, "name">` returning function reference instead of value

---

## v4.2.4 (2026-01-08)

### Bug Fixes
- Fixed `%name` priority for `&function` overrides

---

## v4.2.3 (2026-01-08)

### Bug Fixes
- Removed pagination from CLI documentation
- Fixed `&builtin` function override

---

## v4.2.2 (2026-01-08)

### Bug Fixes
- Fixed bidirectional `lang$Instance` mutations

---

## v4.2.1 (2026-01-08)

### CLI Improvements
- `--doc` and `--changelog` now load from local files
- Added `--changelog --N` and `--changelog --all` options

---

## v4.2.0 (2026-01-08)

### New Features
- Multi-language support with `libinclude()` and `supports` keyword
- Cross-language instance sharing with `lang$InstanceName` syntax
- Language transformers for Python, JavaScript, Java, C#, C++
- SDK packages for C++, Java, C#, JavaScript
- Default parameter values in CSSL functions

### CLI
- Added `includecpp cssl sdk <lang>` command
- Added `--doc "searchterm"` for documentation search

---

## v4.1.0 (2024-12-15)

### New Features
- CodeInfusion system with `<<==` and `+<<==` operators
- Class `overwrites` keyword
- `super()` and `super::method()` calls
- New containers: `combo<T>`, `iterator<T>`, `datastruct<T>`
- `python::pythonize()` for returning CSSL classes to Python

---

## v4.0.3 (2024-11-20)

### New Features
- Universal instances with `instance<"name">`
- Python API: `getInstance()`, `createInstance()`, `deleteInstance()`
- Method injection with `+<<==`

---

## v4.0.2 (2024-11-01)

### New Features
- Simplified API: `CSSL.run()`, `CSSL.module()`, `CSSL.script()`
- Shared objects with `cssl.share(obj, "name")` and `$name` syntax

---

## v4.0.0 (2024-10-15)

### Major Release
- Complete rewrite of CSSL parser and runtime
- Generic container types: `stack<T>`, `vector<T>`, `map<K,V>`
- Class system with constructors and inheritance
- BruteInjection operators: `<==`, `+<==`, `-<==`
- Global variables with `@name`, captured variables with `%name`

---

## v3.2.0 (2024-09-01)

### New Features
- CPPY code conversion (`includecpp cppy convert`)
- AI-assisted conversion with `--ai` flag
- Fast incremental builds with `--fast` flag

---

## v3.1.0 (2024-08-01)

### New Features
- `includecpp auto` and `includecpp fix` commands
- `DEPENDS()` for module dependencies
- `TEMPLATE_FUNC()` for template instantiation

---

## v3.0.0 (2024-07-01)

### Initial Release
- C++ to Python binding generation
- CSSL scripting language
- Plugin file format (.cp)
- CMake-based build system
- Cross-platform support (Windows, Linux, Mac)
