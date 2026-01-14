# CSSL - C-Style Scripting Language

> Version 3.9.0 | A modern scripting language with C++-style syntax and unique features like CodeInfusion, BruteInjection, and Python Interop.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Syntax Basics](#syntax-basics)
3. [Data Types](#data-types)
4. [Variables & Globals](#variables--globals)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Classes & OOP](#classes--oop)
9. [Container Types](#container-types)
10. [Built-in Functions](#built-in-functions)
11. [CodeInfusion](#codeinfusion)
12. [BruteInjection](#bruteinjection)
13. [Value Capture](#value-capture)
14. [Module System](#module-system)
15. [Error Handling](#error-handling)
16. [Quick Reference](#quick-reference)

---

## Quick Start

### Installation

```bash
pip install includecpp
```

### Python Usage

```python
from includecpp import CSSL

# Execute CSSL code
CSSL.run('''
    printl("Hello CSSL!");
''')

# With parameters and return value
result = CSSL.run('''
    string name = parameter.get(0);
    printl("Hello " + name);
    parameter.return(true);
''', "World")

print(result)  # True
```

### CLI Execution

```bash
# Execute CSSL file
python -m includecpp cssl exec myfile.cssl

# Create module from Python file
python -m includecpp cssl makemodule mylib.py -o mylib.cssl-mod
```

### First Script

```cssl
// Variables
string name = "CSSL";
int version = 3;

// Output
printl("Welcome to " + name);

// Function
void greet(string msg) {
    printl(msg);
}

greet("Hello World!");
```

---

## Syntax Basics

### Comments

```cssl
// Single-line comment (C-style)
# Single-line comment (Python-style)
```

### Semicolons

Semicolons are optional but recommended for clarity.

```cssl
printl("Hello")    // Works
printl("Hello");   // Also works (recommended)
```

### Output Functions

```cssl
printl("Text");              // Print with newline
print("No newline");         // Print without newline
debug("Debug info");         // Print with [DEBUG] prefix
error("Error message");      // Print with [ERROR] prefix
warn("Warning");             // Print with [WARN] prefix
log("INFO", "Message");      // Print with custom prefix
```

---

## Data Types

### Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer | `int x = 42;` |
| `float` | Floating point | `float f = 3.14;` |
| `string` | Text string | `string s = "Hello";` |
| `bool` | Boolean | `bool b = true;` |
| `dynamic` | Any type (flexible) | `dynamic x = "text";` |
| `void` | No return value | `void func() { }` |
| `null` | Absence of value | `dynamic x = null;` |

### Generic Container Types

| Type | Description | Example |
|------|-------------|---------|
| `stack<T>` | LIFO stack | `stack<string> names;` |
| `vector<T>` | Dynamic array | `vector<int> nums;` |
| `array<T>` | Standard array | `array<float> values;` |
| `map<K,V>` | Ordered key-value | `map<string, int> ages;` |
| `list` | Python-like list | `list items = [1, 2, 3];` |
| `dict` | Dictionary | `dict data = {"a": 1};` |
| `datastruct<T>` | Universal container | `datastruct<string> data;` |
| `iterator<T>` | Programmable iterator | `iterator<int> it;` |
| `shuffled<T>` | Multi-value returns | `shuffled<string> results;` |
| `combo<T>` | Filter/search space | `combo<string> search;` |

### Type Conversion

```cssl
int("42");        // String to int: 42
float("3.14");    // String to float: 3.14
str(42);          // Int to string: "42"
bool(1);          // Int to bool: true
int("ff", 16);    // Hex to int: 255
```

### Type Checking

```cssl
typeof(42);           // "int"
typeof("hello");      // "str"
isinstance(42, "int"); // true
isint(42);            // true
isstr("hello");       // true
isnull(null);         // true
```

---

## Variables & Globals

### Local Variables

```cssl
string name = "Alice";
int count = 10;
float price = 19.99;
bool active = true;
```

### Global Variables

```cssl
// Declaration with 'global' keyword
global myGlobal = "visible everywhere";

// Access with '@' prefix
printl(@myGlobal);

// Alternative: r@ syntax
r@anotherGlobal = "also global";
printl(@anotherGlobal);
```

### Shared Objects ($)

Access Python objects shared via `CSSL.share()`:

```cssl
// Access shared Python object
$counter.value = 100;
$counter.increment();

// Delete shared object
delete("counter");
```

### Captured References (%)

Capture value at registration time:

```cssl
string version = "1.0";
savedVersion <<== { %version; }
version = "2.0";
printl(savedVersion);  // Still "1.0"
```

---

## Operators

### Arithmetic

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition / Concatenation | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `%` | Modulo | `a % b` |

### Comparison

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal | `a == b` |
| `!=` | Not equal | `a != b` |
| `<` | Less than | `a < b` |
| `>` | Greater than | `a > b` |
| `<=` | Less or equal | `a <= b` |
| `>=` | Greater or equal | `a >= b` |

### Logical

| Operator | Description | Example |
|----------|-------------|---------|
| `&&` | AND | `a && b` |
| `\|\|` | OR | `a \|\| b` |
| `!` | NOT | `!a` |
| `and` | AND (keyword) | `a and b` |
| `or` | OR (keyword) | `a or b` |
| `not` | NOT (keyword) | `not a` |

### Increment/Decrement (in for-loops)

| Operator | Description | Example |
|----------|-------------|---------|
| `++` | Increment | `i++` |
| `--` | Decrement | `i--` |
| `+=` | Add assign | `i += 1` |
| `-=` | Subtract assign | `i -= 1` |

---

## Control Flow

### If / Else If / Else

```cssl
if (x < 5) {
    printl("Small");
} else if (x < 15) {
    printl("Medium");
} else {
    printl("Large");
}

// elif also works
if (x < 5) {
    printl("Small");
} elif (x < 15) {
    printl("Medium");
}
```

### Switch / Case

```cssl
switch (day) {
    case 1:
        printl("Monday");
        break;
    case 2:
        printl("Tuesday");
        break;
    default:
        printl("Other");
}
```

### While Loop

```cssl
int i = 0;
while (i < 5) {
    printl(i);
    i = i + 1;
}
```

### For Loop (Python-Style)

```cssl
// Range-based
for (i in range(5)) {
    printl(i);  // 0, 1, 2, 3, 4
}

// With start and end
for (i in range(10, 15)) {
    printl(i);  // 10, 11, 12, 13, 14
}

// With step
for (i in range(0, 10, 2)) {
    printl(i);  // 0, 2, 4, 6, 8
}
```

### For Loop (C-Style)

```cssl
for (int i = 0; i < 10; i++) {
    printl(i);
}

for (int i = 10; i > 0; i--) {
    printl(i);
}
```

### Foreach

```cssl
stack<string> names;
names.push("Alice");
names.push("Bob");

// Syntax 1
foreach (name in names) {
    printl(name);
}

// Syntax 2
foreach names as name {
    printl(name);
}
```

### Break & Continue

```cssl
for (i in range(10)) {
    if (i == 5) break;     // Exit loop
    if (i == 3) continue;  // Skip iteration
    printl(i);
}
```

---

## Functions

### Basic Syntax

```cssl
// Without return
void sayHello() {
    printl("Hello!");
}

// With return
string getName() {
    return "CSSL";
}

// With parameters
int add(int a, int b) {
    return a + b;
}
```

### Define Functions

```cssl
// Simple function without type
define greet() {
    printl("Hello!");
}

// With parameters
define greet(string name) {
    printl("Hello " + name);
}
```

### Function Modifiers

| Modifier | Description |
|----------|-------------|
| `undefined` | Silently ignore errors |
| `closed` | Block external CodeInfusion |
| `private` | Block all CodeInfusion |
| `virtual` | Import-cycle safe |
| `meta` | Source function (must return) |
| `super` | Force execution (no exceptions) |
| `open` | Accept any parameters |
| `shuffled` | Return multiple values |

```cssl
// Ignore errors
undefined void mayFail() {
    riskyOperation();
}

// Protected from injection
closed void protected() {
    printl("Protected");
}

// Multiple returns
shuffled string getNames() {
    return "Alice", "Bob", "Charlie";
}

a, b, c = getNames();
```

### Non-Null Functions (*)

Functions that must never return null:

```cssl
// Non-null function
define *alwaysReturns() {
    return "Always a value";
}

// Non-null assertion on value
this->name = *$System.os;  // Error if null
```

### Type Exclusion Filter (*[type])

Functions that must NOT return a specific type:

```cssl
// Must NOT return string
shuffled *[string] getNumbers() {
    return 1, 2, 3;  // OK
    // return "text";  // Error!
}

// Must NOT return null
define *[null] getValue() {
    return 42;  // OK
}
```

### Open Parameters

```cssl
open define flexibleFunc(open Params) {
    string name = OpenFind<string>(0);
    int num = OpenFind<int>(0);
    printl(name + " " + num);
}

flexibleFunc("Hello", 123, true);
```

---

## Classes & OOP

### Class Definition

```cssl
class Person {
    string name;
    int age;

    // Constructor
    void Person(string n, int a) {
        this->name = n;
        this->age = a;
    }

    void greet() {
        printl("Hello, I'm " + this->name);
    }

    string getName() {
        return this->name;
    }
}
```

### Creating Instances

```cssl
Person p = new Person("Alice", 30);
p.greet();
printl(p.name);
```

### Constructor with `constr` Keyword

```cssl
class Vehicle {
    string brand;

    constr Initialize(string b) {
        this->brand = b;
    }

    constr SetupDefaults() {
        printl("Vehicle ready");
    }
}

Vehicle v = new Vehicle("Toyota");
```

### Class Inheritance

```cssl
class Animal {
    string name;

    void Animal(string n) {
        this->name = n;
    }

    void speak() {
        printl("Sound");
    }
}

class Dog : extends Animal {
    void Dog(string n) {
        this->name = n;
    }

    void speak() {
        printl("Woof! I'm " + this->name);
    }
}

Dog d = new Dog("Buddy");
d.speak();  // "Woof! I'm Buddy"
```

### super() and super::method()

```cssl
class Child : extends Parent {
    constr ChildInit(string name) {
        super(name);  // Call parent constructor
    }

    void speak() {
        super::speak();  // Call parent method
        printl("Child speaking");
    }
}
```

### Append Mode (++)

Extend constructors/functions while keeping original code:

```cssl
// Original function
define BaseFunc() {
    printl("Base functionality");
}

// Append to BaseFunc
define ExtendedFunc() &BaseFunc ++ {
    printl("Extended functionality");
}

ExtendedFunc();
// Output:
// Base functionality
// Extended functionality
```

```cssl
class MyClass {
    constr MyClassConstructor() {
        printl("MyClass constructor");
        this->value = 10;
    }
}

class BetterClass :: extends MyClass {
    constr BetterConstructor() &MyClass::MyClassConstructor ++ {
        printl("BetterClass - added code");
        this->extra = 20;
    }
}
```

### Non-Null Class

```cssl
class *MyClass {
    // All methods must return non-null
    string getValue() {
        return "Value";
    }
}
```

---

## Container Types

### stack\<T\> - LIFO Stack

```cssl
stack<string> names;
names.push("Alice");
names.push("Bob");

printl(names.pop());     // "Bob"
printl(names.peek());    // "Alice" (doesn't remove)
printl(names.size());    // 1
printl(names.isEmpty()); // false
```

**Methods:**

| Method | Description |
|--------|-------------|
| `push(value)` | Add to top |
| `pop()` | Remove and return top |
| `peek()` | View top without removing |
| `size()` / `length()` | Element count |
| `isEmpty()` / `is_empty()` | Check if empty |
| `contains(value)` | Check if contains |
| `indexOf(value)` | Find index (-1 if not found) |
| `toArray()` | Convert to list |
| `swap()` | Swap top two elements |
| `dup()` | Duplicate top element |

### vector\<T\> - Dynamic Array

```cssl
vector<int> nums;
nums.push(10);
nums.push(20);

printl(nums.at(0));     // 10
printl(nums.front());   // 10
printl(nums.back());    // 20
```

**Methods:**

| Method | Description |
|--------|-------------|
| `push(value)` / `push_back(value)` | Add to end |
| `push_front(value)` | Add to front |
| `pop_back()` | Remove from end |
| `pop_front()` | Remove from front |
| `at(index)` | Get element |
| `set(index, value)` | Set element |
| `front()` | Get first |
| `back()` | Get last |
| `size()` / `length()` | Element count |
| `empty()` / `isEmpty()` | Check if empty |
| `contains(value)` | Check if contains |
| `indexOf(value)` | Find first index |
| `lastIndexOf(value)` | Find last index |
| `slice(start, end)` | Get sub-vector |
| `join(separator)` | Join to string |
| `map(func)` | Apply function |
| `filter(predicate)` | Filter elements |
| `forEach(func)` | Execute for each |
| `every(predicate)` | Check all match |
| `some(predicate)` | Check any match |
| `reduce(func, initial)` | Reduce to value |
| `toArray()` | Convert to list |

### map\<K,V\> - Ordered Key-Value

```cssl
map<string, int> ages;
ages.insert("Alice", 30);
ages.insert("Bob", 25);

printl(ages.find("Alice"));   // 30
printl(ages.contains("Bob")); // true
ages.erase("Bob");
```

**Methods:**

| Method | Description |
|--------|-------------|
| `insert(key, value)` | Insert/update pair |
| `find(key)` | Get value (null if not found) |
| `at(key)` | Get value (throws if not found) |
| `erase(key)` | Remove key |
| `contains(key)` | Check if key exists |
| `count(key)` | Count (0 or 1) |
| `size()` | Pair count |
| `empty()` | Check if empty |
| `begin()` | First key-value tuple |
| `end()` | Last key-value tuple |
| `lower_bound(key)` | First key >= given |
| `upper_bound(key)` | First key > given |

### datastruct\<T\> - Universal Container

Primary target for BruteInjection operations.

```cssl
datastruct<string> data;
data.add("item1");
data.add("item2");

printl(data.content());  // All elements
```

**Methods:**

| Method | Description |
|--------|-------------|
| `content()` | Get all elements |
| `add(value)` | Add element |
| `remove_where(predicate)` | Remove matching |
| `find_where(predicate)` | Find first matching |
| `convert(type)` | Convert first element |

### shuffled\<T\> - Multiple Returns

```cssl
shuffled string getInfo() {
    return "Alice", "Bob", "Charlie";
}

a, b, c = getInfo();
printl(a);  // "Alice"
```

---

## Built-in Functions

### String Operations

```cssl
string s = "Hello World";

// Case
upper(s);              // "HELLO WORLD"
lower(s);              // "hello world"
capitalize(s);         // "Hello world"
title(s);              // "Hello World"

// Trim
trim("  text  ");      // "text"
ltrim("  text");       // "text"
rtrim("text  ");       // "text"

// Search
contains(s, "World");  // true
startswith(s, "Hello"); // true
endswith(s, "World");  // true
indexof(s, "o");       // 4
lastindexof(s, "o");   // 7

// Manipulation
replace(s, "World", "CSSL");  // "Hello CSSL"
substr(s, 0, 5);              // "Hello"
split(s, " ");                // ["Hello", "World"]
join("-", ["a", "b"]);        // "a-b"
repeat("ab", 3);              // "ababab"
reverse(s);                   // "dlroW olleH"

// Padding
padleft("42", 5, "0");   // "00042"
padright("42", 5, ".");  // "42..."
center("hi", 6, "-");    // "--hi--"
zfill("42", 5);          // "00042"

// Character
len(s);                  // 11
chars("abc");            // ["a", "b", "c"]
ord("A");                // 65
chr(65);                 // "A"

// Checks
isalpha("abc");          // true
isdigit("123");          // true
isalnum("abc123");       // true
isspace("  ");           // true
```

### Array/List Operations

```cssl
stack<int> arr = [1, 2, 3, 4, 5];

// Add/Remove
push(arr, 6);            // Add to end
pop(arr);                // Remove last
shift(arr);              // Remove first
unshift(arr, 0);         // Add to front

// Access
first(arr);              // First element
last(arr);               // Last element
slice(arr, 1, 3);        // [2, 3]

// Transform
sort(arr);               // Sort ascending
rsort(arr);              // Sort descending
reversed(arr);           // Reverse copy
shuffle(arr);            // Random order
unique(arr);             // Remove duplicates
flatten([[1,2],[3,4]]);  // [1, 2, 3, 4]

// Search
find(arr, x => x > 3);   // First matching
findindex(arr, x => x > 3);
every(arr, x => x > 0);  // All match?
some(arr, x => x > 3);   // Any match?
count(arr, 2);           // Count of 2

// Functional
map(arr, x => x * 2);    // [2, 4, 6, 8, 10]
filter(arr, x => x > 2); // [3, 4, 5]
reduce(arr, (a,b) => a+b, 0); // 15

// Utilities
range(5);                // [0, 1, 2, 3, 4]
range(1, 5);             // [1, 2, 3, 4]
range(0, 10, 2);         // [0, 2, 4, 6, 8]
enumerate(arr);          // [(0,1), (1,2), ...]
zip([1,2], ["a","b"]);   // [(1,"a"), (2,"b")]
take(arr, 3);            // First 3 elements
drop(arr, 2);            // Skip first 2
chunk(arr, 2);           // [[1,2], [3,4], [5]]
sample(arr, 2);          // 2 random elements
```

### Dictionary Operations

```cssl
dict d = {"name": "Alice", "age": 30};

keys(d);                 // ["name", "age"]
values(d);               // ["Alice", 30]
items(d);                // [("name","Alice"), ...]
haskey(d, "name");       // true
getkey(d, "name");       // "Alice"
getkey(d, "x", "default"); // "default"
setkey(d, "city", "NYC"); // Add key
delkey(d, "age");        // Remove key
merge(d1, d2);           // Merge dicts
update(d, {"new": 1});   // Update in place
fromkeys(["a","b"], 0);  // {"a": 0, "b": 0}
invert({"a": 1});        // {1: "a"}
pick(d, "name");         // {"name": "Alice"}
omit(d, "age");          // {"name": "Alice"}
```

### Math Functions

```cssl
abs(-5);                 // 5
min(3, 1, 2);            // 1
max(3, 1, 2);            // 3
sum([1, 2, 3]);          // 6
avg([1, 2, 3, 4, 5]);    // 3.0

round(3.14159, 2);       // 3.14
floor(3.9);              // 3
ceil(3.1);               // 4

pow(2, 3);               // 8
sqrt(16);                // 4
mod(7, 3);               // 1

sin(0);                  // 0.0
cos(0);                  // 1.0
tan(0);                  // 0.0
asin(1);                 // 1.5708
acos(0);                 // 1.5708
atan(1);                 // 0.7854
atan2(1, 1);             // 0.7854

log(e());                // 1.0
log10(100);              // 2.0
exp(1);                  // 2.71828

pi();                    // 3.14159...
e();                     // 2.71828...
radians(180);            // 3.14159
degrees(3.14159);        // 180

random();                // 0.0 to 1.0
randint(1, 6);           // 1 to 6
```

### Date/Time Functions

```cssl
now();                   // Unix timestamp (float)
timestamp();             // Unix timestamp (int)
date();                  // "2025-12-30"
date("%d/%m/%Y");        // "30/12/2025"
time();                  // "14:30:45"
datetime();              // "2025-12-30 14:30:45"
strftime("%Y-%m-%d", ts);

sleep(1.5);              // Wait 1.5 seconds
delay(500);              // Wait 500 milliseconds
```

### File I/O Functions

```cssl
// Read
string content = read("file.txt");
string line5 = readline(5, "file.txt");
stack<string> lines = readlines("file.txt");

// Write
write("file.txt", "Hello");
writeline(3, "New line", "file.txt");
appendfile("file.txt", "\nMore");

// Path operations
basename("/path/to/file.txt");  // "file.txt"
dirname("/path/to/file.txt");   // "/path/to"
joinpath("/path", "file.txt");  // "/path/file.txt"
abspath("./file.txt");
normpath("/path/../other");

// Checks
pathexists("file.txt");  // true/false
isfile("file.txt");      // true/false
isdir("folder");         // true/false
filesize("file.txt");    // bytes

// Directory
listdir("./");           // ["file1", "file2"]
makedirs("new/folder");
removefile("file.txt");
removedir("folder");
copyfile("src", "dst");
movefile("old", "new");
```

### JSON Functions (json:: namespace)

```cssl
// File operations
json data = json::read("config.json");
json::write("output.json", data);

// Parse/Stringify
json obj = json::parse('{"name": "Alice"}');
string str = json::stringify(obj);
string pretty = json::pretty(obj);

// Path operations
json::get(data, "user.name");
json::get(data, "user.age", 0);  // with default
json::set(data, "user.name", "Bob");
json::has(data, "user.email");

// Object operations
json::keys(obj);         // ["name"]
json::values(obj);       // ["Alice"]
json::merge(obj1, obj2); // Deep merge
```

### Instance Functions (instance:: namespace)

```cssl
@module = include("lib.cssl-mod");

instance::getMethods(@module);   // Method names
instance::getClasses(@module);   // Class names
instance::getVars(@module);      // Variable names
instance::getAll(@module);       // Categorized dict

instance::call(@module, "methodName", arg1);
instance::has(@module, "attribute");
instance::type(@module);         // Type name

isavailable("sharedName");       // Check if exists
```

### Regex Functions

```cssl
match("\\d+", "abc123");         // Match at start
search("\\d+", "abc123");        // Search anywhere
findall("\\d+", "a1b2c3");       // ["1", "2", "3"]
sub("\\d", "X", "a1b2");         // "aXbX"
sub("\\d", "X", "a1b2", 1);      // "aXb2" (count=1)
```

### Hash Functions

```cssl
md5("hello");            // 32 hex chars
sha1("hello");           // 40 hex chars
sha256("hello");         // 64 hex chars
```

### System Functions

```cssl
exit(0);                 // Exit with code
input("Enter name: ");   // Read user input

env("PATH");             // Get env variable
setenv("MY_VAR", "val"); // Set env variable

copy(obj);               // Shallow copy
deepcopy(obj);           // Deep copy

clear();                 // Clear console

pyimport("os");          // Import Python module
include("lib.cssl-mod"); // Import CSSL module
payload("helper.cssl-pl"); // Load payload

isLinux();               // Platform checks
isWindows();
isMac();
```

### Filter Functions (filter:: namespace)

```cssl
// Register custom filter
filter::register("custom", "handler", callback);
filter::unregister("custom", "handler");
filter::list();          // All registered filters
filter::exists("custom", "handler");
```

---

## CodeInfusion

Modify functions at runtime.

### <<== (Replace)

```cssl
void original() {
    printl("Original");
}

original() <<== {
    printl("Replaced");
}

original();  // "Replaced"
```

### +<<== (Add Before)

```cssl
void base() {
    printl("Base");
}

base() +<<== {
    printl("Added");
}

base();
// Output:
// Added
// Base
```

### -<<== (Remove)

```cssl
void withExtra() {
    printl("Important");
    printl("Unimportant");
}

withExtra() -<<== {
    printl("Unimportant");
}

withExtra();  // Only "Important"
```

### Exit Injection

```cssl
exit() <<== {
    printl("Cleanup...");
}

exit();  // Executes injection
```

---

## BruteInjection

Transfer data between containers.

### +<== (Copy)

```cssl
stack<string> source;
source.push("A");
source.push("B");

datastruct<string> target;
target +<== source;  // Copy A, B (source unchanged)
```

### -<== (Move)

```cssl
stack<string> src;
src.push("Data");

datastruct<string> dst;
dst -<== src;  // src is empty after
```

### ==> (Replace)

```cssl
stack<string> data;
data.push("New");

datastruct<string> container;
container ==> data;  // Replace container content
```

### ==>- (Remove Matching)

```cssl
stack<string> names;
names.push("Alice");
names.push("Bob");
names.push("Alice");

stack<string> toRemove;
toRemove.push("Alice");

names ==>- toRemove;
printl(names);  // ["Bob"]
```

### Filter Syntax

```cssl
target +<== [type::filter=value] source;

// String filters
result +<== [string::where="Apple"] fruits;
result +<== [string::not="Banana"] fruits;
result +<== [string::contains="App"] fruits;
result +<== [string::length=5] fruits;
result +<== [string::cut=3] version;
result +<== [string::cutAfter="."] version;

// Other filters
result +<== [integer::where=42] numbers;
result +<== [json::key="name"] objects;
```

---

## Value Capture

Capture values at registration time with `%`:

```cssl
string version = "1.0.0";
savedVersion <<== { %version; }

version = "2.0.0";
printl(savedVersion);  // "1.0.0" (captured value)
```

### Capturing Functions

```cssl
originalExit <<== { %exit(); }

exit() <<== {
    printl("Custom cleanup");
    originalExit();
}
```

---

## Module System

### Import CSSL Module

```cssl
@Math = include("mathlib.cssl-mod");
int result = @Math.add(5, 3);
```

### Import Python Module

```cssl
@os = pyimport("os");
string cwd = @os.getcwd();

@datetime = pyimport("datetime");
@datetime.datetime.now();
```

### Load Payload

```cssl
payload("helpers.cssl-pl");
```

### Create Module (CLI)

```bash
python -m includecpp cssl makemodule mylib.py -o mylib.cssl-mod
```

---

## Error Handling

### Try / Catch

```cssl
try {
    riskyOperation();
} catch (error) {
    printl("Error: " + error);
}

try {
    operation();
} catch (error) {
    printl("Error");
} finally {
    printl("Always runs");
}
```

### Undefined Functions

```cssl
undefined void safeOperation() {
    dangerousCode();  // Errors ignored
}
```

### Assert

```cssl
assert(x > 0, "x must be positive");
```

---

## Quick Reference

### Keywords

| Keyword | Description |
|---------|-------------|
| `void` | No return value |
| `return` | Return value |
| `global` | Declare global |
| `if` / `else` / `elif` | Conditionals |
| `switch` / `case` / `default` | Switch statement |
| `for` / `foreach` / `while` | Loops |
| `break` / `continue` | Loop control |
| `try` / `catch` / `finally` | Error handling |
| `class` / `new` / `this` | OOP |
| `extends` / `overwrites` | Inheritance |
| `constr` | Constructor |
| `define` | Function definition |
| `undefined` | Ignore errors |
| `closed` / `private` | Injection protection |
| `virtual` | Import-safe |
| `meta` / `super` | Special function types |
| `shuffled` | Multiple returns |
| `open` | Any parameters |
| `include` / `get` | Import modules |

### Injection Operators

| Operator | Type | Description |
|----------|------|-------------|
| `<<==` | CodeInfusion | Replace function |
| `+<<==` | CodeInfusion | Add code before |
| `-<<==` | CodeInfusion | Remove code |
| `<==` | ValueCapture | Capture/assign |
| `+<==` | BruteInjection | Copy data |
| `-<==` | BruteInjection | Move data |
| `==>` | BruteInjection | Replace data |
| `==>-` | BruteInjection | Remove matching |
| `++` | AppendMode | Append to parent |

### Special Syntax

| Syntax | Description |
|--------|-------------|
| `@name` | Global variable |
| `$name` | Shared Python object |
| `%name` | Captured value |
| `this->` | Class member access |
| `super::method()` | Parent method call |
| `json::func()` | Namespace function |
| `&ClassName::member` | Class member reference |
| `&FunctionName ++` | Append to function |
| `*func()` | Non-null function |
| `*[type]func()` | Type exclusion filter |

---

*CSSL v3.9.0 - Developed as part of IncludeCPP*
