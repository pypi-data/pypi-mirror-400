# IncludeCPP Changelog

## v4.2.1 (2025-01-08)

### CLI Improvements
- `--doc` and `--doc "term"` now load from local DOCUMENTATION.md
- `--changelog` now loads from local CHANGELOG.md
- Added `--changelog --N` (e.g., `--changelog --5`) for showing N releases
- Added `--changelog --all` for showing all releases

### Documentation
- Added comprehensive DOCUMENTATION.md for CLI reference
- Added CHANGELOG.md for version history

---

## v4.2.0 (2025-01-08)

### Multi-Language Support
- Added `libinclude("language")` for loading language support modules
- Added `supports <lang>` keyword for writing in other language syntax
- Added cross-language instance sharing with `lang$InstanceName` syntax
- Added language transformers for Python, JavaScript, Java, C#, C++
- Added default parameter values in CSSL functions

### SDK Packages
- Added C++ SDK (`sdk/cpp/includecpp.h`)
- Added Java SDK (`sdk/java/src/com/includecpp/CSSL.java`)
- Added C# SDK (`sdk/csharp/IncludeCPP.cs`)
- Added JavaScript SDK (`sdk/javascript/includecpp.js`)
- Added `includecpp cssl sdk <lang>` command to generate SDKs

### CLI Improvements
- Added `--doc "searchterm"` for documentation search
- Added `--changelog --all`, `--changelog --N` for changelog viewing
- Improved error messages with line context

### Bug Fixes
- Fixed compound assignment operators in Python transformer (-=, +=, *=, /=)
- Fixed type annotation stripping in `supports python` blocks
- Fixed self parameter handling in Python method transformation

---

## v4.1.0 (2024-12-15)

### CodeInfusion System
- Added `<<==` operator for code injection into functions
- Added `+<<==` for appending code without replacing
- Added method appending with `&Class::method` syntax
- Added `++` append mode for function definitions

### Class Improvements
- Added `overwrites` keyword for method replacement
- Added `extends Parent::method` for method-level inheritance
- Added `super()` and `super::method()` calls
- Added shuffled returns with `shuffled<T>` type

### New Containers
- Added `combo<T>` for filter/search operations
- Added `iterator<T>` for programmable iterators
- Added `datastruct<T>` universal container

### Python Interop
- Added `python::pythonize()` for returning CSSL classes to Python
- Added `python::wrap()` and `python::export()` aliases
- Added universal instances with `instance<"name">`

---

## v4.0.3 (2024-11-20)

### Universal Instances
- Added `instance<"name">` for cross-runtime shared containers
- Added `cssl.getInstance("name")` Python API
- Added `cssl.createInstance("name")` Python API
- Added `cssl.deleteInstance("name")` Python API
- Added method injection into instances with `+<<==`

### Module System
- Added `CSSL.makemodule()` for creating callable modules
- Added `CSSL.makepayload()` for payload file registration
- Added payload binding with `bind=` parameter

---

## v4.0.2 (2024-11-01)

### Simplified API
- Added `CSSL.run()` as main entry point
- Added `CSSL.module()` for creating modules from strings
- Added `CSSL.script()` for inline payload registration
- Improved parameter handling with `parameter.get()` and `parameter.return()`

### Shared Objects
- Added `cssl.share(obj, "name")` for Python object sharing
- Added `$name` syntax for accessing shared objects
- Changes in CSSL reflect back to Python objects

---

## v4.0.0 (2024-10-15)

### Major Release
- Complete rewrite of CSSL parser and runtime
- Added generic container types (`stack<T>`, `vector<T>`, `map<K,V>`)
- Added class system with constructors and inheritance
- Added BruteInjection operators (`<==`, `+<==`, `-<==`)
- Added global variables with `@name` syntax
- Added captured variables with `%name` syntax

### AI Integration
- Added `includecpp ai` command group
- Added AI-assisted code analysis
- Added AI-powered optimization
- Added `includecpp ai ask` for project questions

---

## v3.2.0 (2024-09-01)

### CPPY Conversion
- Added `includecpp cppy convert` command
- Added Python to C++ conversion
- Added C++ to Python conversion
- Added AI-assisted conversion with `--ai` flag
- Added type mapping tables

### Build Improvements
- Added `--fast` flag for incremental builds
- Added object file caching
- Added SHA256 hash checking for unchanged modules
- Reduced rebuild time to ~0.4s when unchanged

---

## v3.1.0 (2024-08-01)

### CLI Enhancements
- Added `includecpp auto` command
- Added `includecpp fix` for code analysis
- Added `--verbose` flag for detailed output
- Added `-j` flag for parallel jobs

### Plugin Format
- Added `DEPENDS()` for module dependencies
- Added `TEMPLATE_FUNC()` for template instantiation
- Added `METHOD_CONST()` for overloaded methods

---

## v3.0.0 (2024-07-01)

### Initial CSSL
- Added CSSL scripting language
- Added basic data types and control flow
- Added functions and basic classes
- Added Python interop with shared objects

### Core Features
- C++ to Python binding generation
- Plugin file format (.cp)
- CMake-based build system
- Cross-platform support (Windows, Linux, Mac)
