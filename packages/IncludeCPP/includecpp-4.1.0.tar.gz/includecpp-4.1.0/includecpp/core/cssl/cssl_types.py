"""
CSSL Data Types - Advanced container types for CSSL

Types:
- datastruct<T>: Universal container (lazy declarator) - can hold any type
- shuffled<T>: Unorganized fast storage for multiple returns
- iterator<T>: Advanced iterator with programmable tasks
- combo<T>: Filter/search spaces for open parameter matching
- dataspace<T>: SQL/data storage container
- openquote<T>: SQL openquote container
"""

from typing import Any, Dict, List, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass, field
import copy


T = TypeVar('T')


class DataStruct(list):
    """Universal container - lazy declarator that can hold any type.

    Like a vector but more flexible. Can hold strings, ints, floats,
    objects, etc. at the cost of performance.

    Usage:
        datastruct<dynamic> myData;
        myData +<== someValue;
        myData.content()  # Returns all elements
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type
        self._metadata: Dict[str, Any] = {}

    def content(self) -> list:
        """Return all elements as a list"""
        return list(self)

    def add(self, item: Any) -> 'DataStruct':
        """Add an item to the datastruct"""
        self.append(item)
        return self

    def remove_where(self, predicate: Callable[[Any], bool]) -> 'DataStruct':
        """Remove items matching predicate"""
        to_remove = [item for item in self if predicate(item)]
        for item in to_remove:
            self.remove(item)
        return self

    def find_where(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """Find first item matching predicate"""
        for item in self:
            if predicate(item):
                return item
        return None

    def convert(self, target_type: type) -> Any:
        """Convert first element to target type"""
        if len(self) > 0:
            return target_type(self[0])
        return None

    def length(self) -> int:
        """Return datastruct length"""
        return len(self)

    def size(self) -> int:
        """Return datastruct size (alias for length)"""
        return len(self)

    def push(self, item: Any) -> 'DataStruct':
        """Push item to datastruct (alias for add)"""
        self.append(item)
        return self

    def isEmpty(self) -> bool:
        """Check if datastruct is empty"""
        return len(self) == 0

    def contains(self, item: Any) -> bool:
        """Check if datastruct contains item"""
        return item in self

    def at(self, index: int) -> Any:
        """Get item at index (safe access)"""
        if 0 <= index < len(self):
            return self[index]
        return None

    def begin(self) -> int:
        """Return iterator to beginning (C++ style)"""
        return 0

    def end(self) -> int:
        """Return iterator to end (C++ style)"""
        return len(self)


class Stack(list):
    """Stack data structure (LIFO).

    Standard stack with push/pop operations.

    Usage:
        stack<string> myStack;
        myStack.push("Item1");
        myStack.push("Item2");
        item = myStack.pop();  # Returns "Item2"
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type

    def push(self, item: Any) -> 'Stack':
        """Push item onto stack"""
        self.append(item)
        return self

    def push_back(self, item: Any) -> 'Stack':
        """Push item onto stack (alias for push)"""
        self.append(item)
        return self

    def pop(self) -> Any:
        """Pop and return top element from stack"""
        if len(self) == 0:
            return None
        return super().pop()

    def pop_back(self) -> Any:
        """Pop and return top element (alias for pop)"""
        return self.pop()

    def peek(self) -> Any:
        """View top item without removing"""
        return self[-1] if self else None

    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return len(self) == 0

    def isEmpty(self) -> bool:
        """Check if stack is empty (camelCase alias)"""
        return len(self) == 0

    def size(self) -> int:
        """Return stack size"""
        return len(self)

    def length(self) -> int:
        """Return stack length (alias for size)"""
        return len(self)

    def contains(self, item: Any) -> bool:
        """Check if stack contains item"""
        return item in self

    def indexOf(self, item: Any) -> int:
        """Find index of item (-1 if not found)"""
        try:
            return self.index(item)
        except ValueError:
            return -1

    def toArray(self) -> list:
        """Convert stack to array"""
        return list(self)

    def swap(self) -> 'Stack':
        """Swap top two elements"""
        if len(self) >= 2:
            self[-1], self[-2] = self[-2], self[-1]
        return self

    def dup(self) -> 'Stack':
        """Duplicate top element"""
        if self:
            self.append(self[-1])
        return self

    def begin(self) -> int:
        """Return iterator to beginning (C++ style)"""
        return 0

    def end(self) -> int:
        """Return iterator to end (C++ style)"""
        return len(self)


class Vector(list):
    """Dynamic array (vector) data structure.

    Resizable array with efficient random access.

    Usage:
        vector<int> myVector;
        myVector.push(1);
        myVector.push(2);
        myVector.at(0);  # Returns 1
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type

    def push(self, item: Any) -> 'Vector':
        """Add item to end"""
        self.append(item)
        return self

    def push_back(self, item: Any) -> 'Vector':
        """Add item to end (alias for push)"""
        self.append(item)
        return self

    def push_front(self, item: Any) -> 'Vector':
        """Add item to front"""
        self.insert(0, item)
        return self

    def pop_back(self) -> Any:
        """Remove and return last element"""
        return self.pop() if self else None

    def pop_front(self) -> Any:
        """Remove and return first element"""
        return self.pop(0) if self else None

    def at(self, index: int) -> Any:
        """Get item at index"""
        if 0 <= index < len(self):
            return self[index]
        return None

    def set(self, index: int, value: Any) -> 'Vector':
        """Set item at index"""
        if 0 <= index < len(self):
            self[index] = value
        return self

    def size(self) -> int:
        """Return vector size"""
        return len(self)

    def length(self) -> int:
        """Return vector length (alias for size)"""
        return len(self)

    def empty(self) -> bool:
        """Check if vector is empty"""
        return len(self) == 0

    def isEmpty(self) -> bool:
        """Check if vector is empty (camelCase alias)"""
        return len(self) == 0

    def front(self) -> Any:
        """Get first element"""
        return self[0] if self else None

    def back(self) -> Any:
        """Get last element"""
        return self[-1] if self else None

    def contains(self, item: Any) -> bool:
        """Check if vector contains item"""
        return item in self

    def indexOf(self, item: Any) -> int:
        """Find index of item (-1 if not found)"""
        try:
            return self.index(item)
        except ValueError:
            return -1

    def lastIndexOf(self, item: Any) -> int:
        """Find last index of item (-1 if not found)"""
        for i in range(len(self) - 1, -1, -1):
            if self[i] == item:
                return i
        return -1

    def find(self, predicate: Callable[[Any], bool]) -> Any:
        """Find first item matching predicate"""
        for item in self:
            if callable(predicate) and predicate(item):
                return item
            elif item == predicate:
                return item
        return None

    def findIndex(self, predicate: Callable[[Any], bool]) -> int:
        """Find index of first item matching predicate"""
        for i, item in enumerate(self):
            if callable(predicate) and predicate(item):
                return i
            elif item == predicate:
                return i
        return -1

    def slice(self, start: int, end: int = None) -> 'Vector':
        """Return slice of vector"""
        if end is None:
            result = Vector(self._element_type)
            result.extend(self[start:])
        else:
            result = Vector(self._element_type)
            result.extend(self[start:end])
        return result

    def join(self, separator: str = ',') -> str:
        """Join elements into string"""
        return separator.join(str(item) for item in self)

    def map(self, func: Callable[[Any], Any]) -> 'Vector':
        """Apply function to all elements"""
        result = Vector(self._element_type)
        result.extend(func(item) for item in self)
        return result

    def filter(self, predicate: Callable[[Any], bool]) -> 'Vector':
        """Filter elements by predicate"""
        result = Vector(self._element_type)
        result.extend(item for item in self if predicate(item))
        return result

    def forEach(self, func: Callable[[Any], None]) -> 'Vector':
        """Execute function for each element"""
        for item in self:
            func(item)
        return self

    def toArray(self) -> list:
        """Convert to plain list"""
        return list(self)

    def fill(self, value: Any, start: int = 0, end: int = None) -> 'Vector':
        """Fill range with value"""
        if end is None:
            end = len(self)
        for i in range(start, min(end, len(self))):
            self[i] = value
        return self

    def every(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if all elements match predicate"""
        return all(predicate(item) for item in self)

    def some(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if any element matches predicate"""
        return any(predicate(item) for item in self)

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = None) -> Any:
        """Reduce vector to single value"""
        from functools import reduce as py_reduce
        if initial is None:
            return py_reduce(func, self)
        return py_reduce(func, self, initial)

    def begin(self) -> int:
        """Return iterator to beginning (C++ style)"""
        return 0

    def end(self) -> int:
        """Return iterator to end (C++ style)"""
        return len(self)


class Array(list):
    """Array data structure with CSSL methods.

    Standard array with push/pop/length operations.

    Usage:
        array<string> arr;
        arr.push("Item");
        arr.length();  # Returns 1
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type

    def push(self, item: Any) -> 'Array':
        """Add item to end"""
        self.append(item)
        return self

    def push_back(self, item: Any) -> 'Array':
        """Add item to end (alias for push)"""
        self.append(item)
        return self

    def push_front(self, item: Any) -> 'Array':
        """Add item to front"""
        self.insert(0, item)
        return self

    def pop_back(self) -> Any:
        """Remove and return last element"""
        return self.pop() if self else None

    def pop_front(self) -> Any:
        """Remove and return first element"""
        return self.pop(0) if self else None

    def at(self, index: int) -> Any:
        """Get item at index"""
        if 0 <= index < len(self):
            return self[index]
        return None

    def set(self, index: int, value: Any) -> 'Array':
        """Set item at index"""
        if 0 <= index < len(self):
            self[index] = value
        return self

    def size(self) -> int:
        """Return array size"""
        return len(self)

    def length(self) -> int:
        """Return array length"""
        return len(self)

    def empty(self) -> bool:
        """Check if array is empty"""
        return len(self) == 0

    def isEmpty(self) -> bool:
        """Check if array is empty (camelCase alias)"""
        return len(self) == 0

    def first(self) -> Any:
        """Get first element"""
        return self[0] if self else None

    def last(self) -> Any:
        """Get last element"""
        return self[-1] if self else None

    def contains(self, item: Any) -> bool:
        """Check if array contains item"""
        return item in self

    def indexOf(self, item: Any) -> int:
        """Find index of item (-1 if not found)"""
        try:
            return self.index(item)
        except ValueError:
            return -1

    def lastIndexOf(self, item: Any) -> int:
        """Find last index of item (-1 if not found)"""
        for i in range(len(self) - 1, -1, -1):
            if self[i] == item:
                return i
        return -1

    def find(self, predicate: Callable[[Any], bool]) -> Any:
        """Find first item matching predicate"""
        for item in self:
            if callable(predicate) and predicate(item):
                return item
            elif item == predicate:
                return item
        return None

    def findIndex(self, predicate: Callable[[Any], bool]) -> int:
        """Find index of first item matching predicate"""
        for i, item in enumerate(self):
            if callable(predicate) and predicate(item):
                return i
            elif item == predicate:
                return i
        return -1

    def slice(self, start: int, end: int = None) -> 'Array':
        """Return slice of array"""
        if end is None:
            result = Array(self._element_type)
            result.extend(self[start:])
        else:
            result = Array(self._element_type)
            result.extend(self[start:end])
        return result

    def join(self, separator: str = ',') -> str:
        """Join elements into string"""
        return separator.join(str(item) for item in self)

    def map(self, func: Callable[[Any], Any]) -> 'Array':
        """Apply function to all elements"""
        result = Array(self._element_type)
        result.extend(func(item) for item in self)
        return result

    def filter(self, predicate: Callable[[Any], bool]) -> 'Array':
        """Filter elements by predicate"""
        result = Array(self._element_type)
        result.extend(item for item in self if predicate(item))
        return result

    def forEach(self, func: Callable[[Any], None]) -> 'Array':
        """Execute function for each element"""
        for item in self:
            func(item)
        return self

    def toArray(self) -> list:
        """Convert to plain list"""
        return list(self)

    def fill(self, value: Any, start: int = 0, end: int = None) -> 'Array':
        """Fill range with value"""
        if end is None:
            end = len(self)
        for i in range(start, min(end, len(self))):
            self[i] = value
        return self

    def every(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if all elements match predicate"""
        return all(predicate(item) for item in self)

    def some(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if any element matches predicate"""
        return any(predicate(item) for item in self)

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = None) -> Any:
        """Reduce array to single value"""
        from functools import reduce as py_reduce
        if initial is None:
            return py_reduce(func, self)
        return py_reduce(func, self, initial)

    def concat(self, *arrays) -> 'Array':
        """Concatenate with other arrays"""
        result = Array(self._element_type)
        result.extend(self)
        for arr in arrays:
            result.extend(arr)
        return result

    def flat(self, depth: int = 1) -> 'Array':
        """Flatten nested arrays"""
        result = Array(self._element_type)
        for item in self:
            if isinstance(item, (list, Array)) and depth > 0:
                if depth == 1:
                    result.extend(item)
                else:
                    nested = Array(self._element_type)
                    nested.extend(item)
                    result.extend(nested.flat(depth - 1))
            else:
                result.append(item)
        return result

    def unique(self) -> 'Array':
        """Return array with unique elements"""
        result = Array(self._element_type)
        seen = set()
        for item in self:
            key = item if isinstance(item, (int, str, float, bool)) else id(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def begin(self) -> int:
        """Return iterator to beginning (C++ style)"""
        return 0

    def end(self) -> int:
        """Return iterator to end (C++ style)"""
        return len(self)


class List(list):
    """Python-like list with all standard operations.

    Works exactly like Python lists with additional CSSL methods.

    Usage:
        list myList;
        myList.append("item");
        myList.insert(0, "first");
        myList.pop();
        myList.find("item");  # Returns index or -1
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type

    def length(self) -> int:
        """Return list length"""
        return len(self)

    def size(self) -> int:
        """Return list size (alias for length)"""
        return len(self)

    def isEmpty(self) -> bool:
        """Check if list is empty"""
        return len(self) == 0

    def first(self) -> Any:
        """Get first element"""
        return self[0] if self else None

    def last(self) -> Any:
        """Get last element"""
        return self[-1] if self else None

    def at(self, index: int) -> Any:
        """Get item at index (safe access)"""
        if 0 <= index < len(self):
            return self[index]
        return None

    def set(self, index: int, value: Any) -> 'List':
        """Set item at index"""
        if 0 <= index < len(self):
            self[index] = value
        return self

    def add(self, item: Any) -> 'List':
        """Add item to end (alias for append)"""
        self.append(item)
        return self

    def push(self, item: Any) -> 'List':
        """Push item to end (alias for append)"""
        self.append(item)
        return self

    def find(self, item: Any) -> int:
        """Find index of item (-1 if not found)"""
        try:
            return self.index(item)
        except ValueError:
            return -1

    def contains(self, item: Any) -> bool:
        """Check if list contains item"""
        return item in self

    def indexOf(self, item: Any) -> int:
        """Find index of item (-1 if not found)"""
        return self.find(item)

    def lastIndexOf(self, item: Any) -> int:
        """Find last index of item (-1 if not found)"""
        for i in range(len(self) - 1, -1, -1):
            if self[i] == item:
                return i
        return -1

    def removeAt(self, index: int) -> Any:
        """Remove and return item at index"""
        if 0 <= index < len(self):
            return self.pop(index)
        return None

    def removeValue(self, value: Any) -> bool:
        """Remove first occurrence of value"""
        try:
            self.remove(value)
            return True
        except ValueError:
            return False

    def removeAll(self, value: Any) -> int:
        """Remove all occurrences of value, return count"""
        count = 0
        while value in self:
            self.remove(value)
            count += 1
        return count

    def slice(self, start: int, end: int = None) -> 'List':
        """Return slice of list"""
        result = List(self._element_type)
        if end is None:
            result.extend(self[start:])
        else:
            result.extend(self[start:end])
        return result

    def join(self, separator: str = ',') -> str:
        """Join elements into string"""
        return separator.join(str(item) for item in self)

    def unique(self) -> 'List':
        """Return list with unique elements"""
        result = List(self._element_type)
        seen = set()
        for item in self:
            key = item if isinstance(item, (int, str, float, bool)) else id(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def sorted(self, reverse: bool = False) -> 'List':
        """Return sorted copy"""
        result = List(self._element_type)
        result.extend(sorted(self, reverse=reverse))
        return result

    def reversed(self) -> 'List':
        """Return reversed copy"""
        result = List(self._element_type)
        result.extend(reversed(self))
        return result

    def shuffle(self) -> 'List':
        """Shuffle list in place"""
        import random
        random.shuffle(self)
        return self

    def fill(self, value: Any, count: int = None) -> 'List':
        """Fill list with value"""
        if count is None:
            for i in range(len(self)):
                self[i] = value
        else:
            self.clear()
            self.extend([value] * count)
        return self

    def map(self, func: Callable[[Any], Any]) -> 'List':
        """Apply function to all elements"""
        result = List(self._element_type)
        result.extend(func(item) for item in self)
        return result

    def filter(self, predicate: Callable[[Any], bool]) -> 'List':
        """Filter elements by predicate"""
        result = List(self._element_type)
        result.extend(item for item in self if predicate(item))
        return result

    def forEach(self, func: Callable[[Any], None]) -> 'List':
        """Execute function for each element"""
        for item in self:
            func(item)
        return self

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = None) -> Any:
        """Reduce list to single value"""
        from functools import reduce as py_reduce
        if initial is None:
            return py_reduce(func, self)
        return py_reduce(func, self, initial)

    def every(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if all elements match predicate"""
        return all(predicate(item) for item in self)

    def some(self, predicate: Callable[[Any], bool]) -> bool:
        """Check if any element matches predicate"""
        return any(predicate(item) for item in self)

    def begin(self) -> int:
        """Return iterator to beginning"""
        return 0

    def end(self) -> int:
        """Return iterator to end"""
        return len(self)


class Dictionary(dict):
    """Python-like dictionary with all standard operations.

    Works exactly like Python dicts with additional CSSL methods.

    Usage:
        dictionary myDict;
        myDict.set("key", "value");
        myDict.get("key");
        myDict.keys();
        myDict.values();
    """

    def __init__(self, key_type: str = 'dynamic', value_type: str = 'dynamic'):
        super().__init__()
        self._key_type = key_type
        self._value_type = value_type

    def length(self) -> int:
        """Return dictionary size"""
        return len(self)

    def size(self) -> int:
        """Return dictionary size (alias for length)"""
        return len(self)

    def isEmpty(self) -> bool:
        """Check if dictionary is empty"""
        return len(self) == 0

    def set(self, key: Any, value: Any) -> 'Dictionary':
        """Set key-value pair"""
        self[key] = value
        return self

    def hasKey(self, key: Any) -> bool:
        """Check if key exists"""
        return key in self

    def hasValue(self, value: Any) -> bool:
        """Check if value exists"""
        return value in self.values()

    def remove(self, key: Any) -> Any:
        """Remove and return value for key"""
        return self.pop(key, None)

    def getOrDefault(self, key: Any, default: Any = None) -> Any:
        """Get value or default if not found"""
        return self.get(key, default)

    def setDefault(self, key: Any, default: Any) -> Any:
        """Set default if key doesn't exist, return value"""
        if key not in self:
            self[key] = default
        return self[key]

    def merge(self, other: dict) -> 'Dictionary':
        """Merge another dictionary into this one"""
        self.update(other)
        return self

    def keysList(self) -> list:
        """Return keys as list"""
        return list(self.keys())

    def valuesList(self) -> list:
        """Return values as list"""
        return list(self.values())

    def itemsList(self) -> list:
        """Return items as list of tuples"""
        return list(self.items())

    def filter(self, predicate: Callable[[Any, Any], bool]) -> 'Dictionary':
        """Filter dictionary by predicate(key, value)"""
        result = Dictionary(self._key_type, self._value_type)
        for k, v in self.items():
            if predicate(k, v):
                result[k] = v
        return result

    def map(self, func: Callable[[Any, Any], Any]) -> 'Dictionary':
        """Apply function to all values"""
        result = Dictionary(self._key_type, self._value_type)
        for k, v in self.items():
            result[k] = func(k, v)
        return result

    def forEach(self, func: Callable[[Any, Any], None]) -> 'Dictionary':
        """Execute function for each key-value pair"""
        for k, v in self.items():
            func(k, v)
        return self

    def invert(self) -> 'Dictionary':
        """Swap keys and values"""
        result = Dictionary(self._value_type, self._key_type)
        for k, v in self.items():
            result[v] = k
        return result

    def find(self, value: Any) -> Optional[Any]:
        """Find first key with given value"""
        for k, v in self.items():
            if v == value:
                return k
        return None

    def findAll(self, value: Any) -> list:
        """Find all keys with given value"""
        return [k for k, v in self.items() if v == value]


class Shuffled(list):
    """Unorganized fast storage for multiple returns.

    Stores data unorganized for fast and efficient access.
    Supports receiving multiple return values from functions.
    Can be used as a function modifier to allow multiple returns.

    Usage:
        shuffled<string> results;
        results +<== someFunc();  # Catches all returns
        results.read()  # Returns all content as list

        # As return modifier:
        shuffled string getData() {
            return "name", "address";  # Returns multiple values
        }
    """

    def __init__(self, element_type: str = 'dynamic'):
        super().__init__()
        self._element_type = element_type

    def read(self) -> list:
        """Return all content as a list"""
        return list(self)

    def collect(self, func: Callable, *args) -> 'Shuffled':
        """Collect all returns from a function"""
        result = func(*args)
        if isinstance(result, (list, tuple)):
            self.extend(result)
        else:
            self.append(result)
        return self

    def add(self, *items) -> 'Shuffled':
        """Add one or more items"""
        for item in items:
            if isinstance(item, (list, tuple)):
                self.extend(item)
            else:
                self.append(item)
        return self

    def first(self) -> Any:
        """Get first element"""
        return self[0] if self else None

    def last(self) -> Any:
        """Get last element"""
        return self[-1] if self else None

    def length(self) -> int:
        """Return shuffled length"""
        return len(self)

    def isEmpty(self) -> bool:
        """Check if empty"""
        return len(self) == 0

    def contains(self, item: Any) -> bool:
        """Check if contains item"""
        return item in self

    def at(self, index: int) -> Any:
        """Get item at index"""
        if 0 <= index < len(self):
            return self[index]
        return None

    def toList(self) -> list:
        """Convert to plain list"""
        return list(self)

    def toTuple(self) -> tuple:
        """Convert to tuple"""
        return tuple(self)


class Iterator:
    """Advanced iterator with programmable tasks.

    Provides iterator positions within a data container with
    the ability to attach tasks (functions) to iterators.

    Usage:
        iterator<int, 16> Map;  # Create 16-element iterator space
        Map::iterator::set(0, 5);  # Set iterator 0 to position 5
        Map::iterator::task(0, myFunc);  # Attach task to iterator
    """

    def __init__(self, element_type: str = 'int', size: int = 16):
        self._element_type = element_type
        self._size = size
        self._data: List[Any] = [None] * size
        self._iterators: Dict[int, int] = {0: 0, 1: 1}  # Default: 2 iterators at positions 0 and 1
        self._tasks: Dict[int, Callable] = {}

    def insert(self, index: int, value: Any) -> 'Iterator':
        """Insert value at index"""
        if 0 <= index < self._size:
            self._data[index] = value
        return self

    def fill(self, value: Any) -> 'Iterator':
        """Fill all positions with value"""
        self._data = [value] * self._size
        return self

    def at(self, index: int) -> Any:
        """Get value at index"""
        if 0 <= index < self._size:
            return self._data[index]
        return None

    def is_all(self, check_value: bool) -> bool:
        """Check if all values are 1 (True) or 0 (False)"""
        expected = 1 if check_value else 0
        return all(v == expected for v in self._data if v is not None)

    def end(self) -> int:
        """Return last index"""
        return self._size - 1

    class IteratorControl:
        """Static methods for iterator control"""

        @staticmethod
        def set(iterator_obj: 'Iterator', iterator_id: int, position: int):
            """Set iterator position"""
            iterator_obj._iterators[iterator_id] = position

        @staticmethod
        def move(iterator_obj: 'Iterator', iterator_id: int, steps: int):
            """Move iterator by steps"""
            if iterator_id in iterator_obj._iterators:
                iterator_obj._iterators[iterator_id] += steps

        @staticmethod
        def insert(iterator_obj: 'Iterator', iterator_id: int, value: Any):
            """Insert value at current iterator position"""
            if iterator_id in iterator_obj._iterators:
                pos = iterator_obj._iterators[iterator_id]
                if 0 <= pos < iterator_obj._size:
                    iterator_obj._data[pos] = value

        @staticmethod
        def pop(iterator_obj: 'Iterator', iterator_id: int):
            """Delete value at current iterator position"""
            if iterator_id in iterator_obj._iterators:
                pos = iterator_obj._iterators[iterator_id]
                if 0 <= pos < iterator_obj._size:
                    iterator_obj._data[pos] = None

        @staticmethod
        def task(iterator_obj: 'Iterator', iterator_id: int, func: Callable):
            """Attach a task function to iterator"""
            iterator_obj._tasks[iterator_id] = func

        @staticmethod
        def dtask(iterator_obj: 'Iterator', iterator_id: int):
            """Clear task from iterator"""
            if iterator_id in iterator_obj._tasks:
                del iterator_obj._tasks[iterator_id]

        @staticmethod
        def run_task(iterator_obj: 'Iterator', iterator_id: int):
            """Run the task at current iterator position"""
            if iterator_id in iterator_obj._tasks and iterator_id in iterator_obj._iterators:
                pos = iterator_obj._iterators[iterator_id]
                task = iterator_obj._tasks[iterator_id]
                # Create a position wrapper
                class IteratorPos:
                    def __init__(self, data, idx):
                        self._data = data
                        self._idx = idx
                    def read(self):
                        return self._data[self._idx]
                    def write(self, value):
                        self._data[self._idx] = value

                task(IteratorPos(iterator_obj._data, pos))


class Combo:
    """Filter/search space for open parameter matching.

    Creates a search/filter space that can match parameters
    based on filter databases and similarity.

    Usage:
        combo<open&string> nameSpace;
        nameSpace +<== [combo::filterdb] filterDB;
        special_name = OpenFind(&nameSpace);
    """

    def __init__(self, element_type: str = 'dynamic'):
        self._element_type = element_type
        self._filterdb: List[Any] = []
        self._blocked: List[Any] = []
        self._data: List[Any] = []
        self._like_pattern: Optional[str] = None

    @property
    def filterdb(self) -> List[Any]:
        return self._filterdb

    @filterdb.setter
    def filterdb(self, value: List[Any]):
        self._filterdb = value

    @property
    def blocked(self) -> List[Any]:
        return self._blocked

    @blocked.setter
    def blocked(self, value: List[Any]):
        self._blocked = value

    def like(self, pattern: str) -> 'Combo':
        """Set similarity pattern (94-100% match)"""
        self._like_pattern = pattern
        return self

    def matches(self, value: Any) -> bool:
        """Check if value matches combo criteria"""
        # Check if blocked
        if value in self._blocked:
            return False

        # Check filterdb if present
        if self._filterdb:
            if value not in self._filterdb:
                return False

        # Check like pattern if present
        if self._like_pattern and isinstance(value, str):
            similarity = self._calculate_similarity(value, self._like_pattern)
            if similarity < 0.94:
                return False

        return True

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (simple Levenshtein-based)"""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        # Simple character-based similarity
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        matching = sum(c1 == c2 for c1, c2 in zip(s1_lower, s2_lower))
        return matching / max(len(s1), len(s2))

    def find_match(self, items: List[Any]) -> Optional[Any]:
        """Find first matching item from list"""
        for item in items:
            if self.matches(item):
                return item
        return None


class DataSpace(dict):
    """SQL/data storage container for structured data.

    Used for SQL table definitions and structured data storage.

    Usage:
        dataspace<sql::table> table = { ... };
        @Sql.Structured(&table);
    """

    def __init__(self, space_type: str = 'dynamic'):
        super().__init__()
        self._space_type = space_type
        self._sections: Dict[str, Any] = {}

    def content(self) -> dict:
        """Return all content"""
        return dict(self)

    def section(self, name: str, *types) -> 'DataSpace':
        """Create a section with specified types"""
        self._sections[name] = {
            'types': types,
            'data': []
        }
        return self


class OpenQuote:
    """SQL openquote container for organized data handling.

    Creates a datastruct together with sql::db.oqt() for easy
    data organization and retrieval.

    Usage:
        openquote<datastruct<dynamic>&@sql::db.oqt(@db)> Queue;
        Queue.save("Section", "data1", "data2", 123);
        Queue.where(Section="value", KEY="match");
    """

    def __init__(self, db_reference: Any = None):
        self._data: List[Dict[str, Any]] = []
        self._db_ref = db_reference

    def save(self, section: str, *values) -> 'OpenQuote':
        """Save data to a section"""
        self._data.append({
            'section': section,
            'values': list(values)
        })
        return self

    def where(self, **kwargs) -> Optional[Any]:
        """Find data matching criteria"""
        for entry in self._data:
            if all(entry.get(k) == v or (k == 'Section' and entry.get('section') == v)
                   for k, v in kwargs.items()):
                return entry
        return None

    def all(self) -> List[Dict[str, Any]]:
        """Return all data"""
        return self._data


class Parameter:
    """Parameter accessor for CSSL exec() arguments.

    Provides access to arguments passed to CSSL.exec() via parameter.get(index).

    Usage in CSSL:
        parameter.get(0)  # Get first argument
        parameter.get(1)  # Get second argument
        parameter.count() # Get total argument count
        parameter.all()   # Get all arguments as list
        parameter.return(value)  # Yield a return value (generator-like)
        parameter.returns()  # Get all yielded return values
    """

    def __init__(self, args: List[Any] = None):
        self._args = args if args is not None else []
        self._returns: List[Any] = []

    def get(self, index: int, default: Any = None) -> Any:
        """Get argument at index, returns default if not found"""
        if 0 <= index < len(self._args):
            return self._args[index]
        return default

    def count(self) -> int:
        """Return total number of arguments"""
        return len(self._args)

    def all(self) -> List[Any]:
        """Return all arguments as a list"""
        return list(self._args)

    def has(self, index: int) -> bool:
        """Check if argument exists at index"""
        return 0 <= index < len(self._args)

    # Using 'return_' to avoid Python keyword conflict
    def return_(self, value: Any) -> None:
        """Yield a return value (generator-like behavior).

        Multiple calls accumulate values that can be retrieved via returns().
        The CSSL runtime will collect these as the exec() return value.
        """
        self._returns.append(value)

    def returns(self) -> List[Any]:
        """Get all yielded return values"""
        return list(self._returns)

    def clear_returns(self) -> None:
        """Clear all yielded return values"""
        self._returns.clear()

    def has_returns(self) -> bool:
        """Check if any values have been returned"""
        return len(self._returns) > 0

    def __iter__(self):
        return iter(self._args)

    def __len__(self):
        return len(self._args)

    def __getitem__(self, index: int) -> Any:
        return self.get(index)


def OpenFind(combo_or_type: Union[Combo, type], index: int = 0) -> Optional[Any]:
    """Find open parameter by type or combo space.

    Usage:
        string name = OpenFind<string>(0);  # Find string at index 0
        string special = OpenFind(&@comboSpace);  # Find by combo
    """
    if isinstance(combo_or_type, Combo):
        # Find by combo space
        return combo_or_type.find_match([])  # Would need open params context
    elif isinstance(combo_or_type, type):
        # Find by type at index - needs open params context
        pass
    return None


# Type factory functions for CSSL
def create_datastruct(element_type: str = 'dynamic') -> DataStruct:
    return DataStruct(element_type)

def create_shuffled(element_type: str = 'dynamic') -> Shuffled:
    return Shuffled(element_type)

def create_iterator(element_type: str = 'int', size: int = 16) -> Iterator:
    return Iterator(element_type, size)

def create_combo(element_type: str = 'dynamic') -> Combo:
    return Combo(element_type)

def create_dataspace(space_type: str = 'dynamic') -> DataSpace:
    return DataSpace(space_type)

def create_openquote(db_ref: Any = None) -> OpenQuote:
    return OpenQuote(db_ref)

def create_stack(element_type: str = 'dynamic') -> Stack:
    return Stack(element_type)

def create_vector(element_type: str = 'dynamic') -> Vector:
    return Vector(element_type)

def create_parameter(args: List[Any] = None) -> Parameter:
    """Create a Parameter object for accessing exec arguments"""
    return Parameter(args)

def create_array(element_type: str = 'dynamic') -> Array:
    """Create an Array object"""
    return Array(element_type)


def create_list(element_type: str = 'dynamic') -> List:
    """Create a List object"""
    return List(element_type)


def create_dictionary(key_type: str = 'dynamic', value_type: str = 'dynamic') -> Dictionary:
    """Create a Dictionary object"""
    return Dictionary(key_type, value_type)


class Map(dict):
    """C++ style map container with ordered key-value pairs.

    Similar to Dictionary but with C++ map semantics.
    Keys are maintained in sorted order.

    Usage:
        map<string, int> ages;
        ages.insert("Alice", 30);
        ages.find("Alice");
        ages.erase("Alice");
    """

    def __init__(self, key_type: str = 'dynamic', value_type: str = 'dynamic'):
        super().__init__()
        self._key_type = key_type
        self._value_type = value_type

    def insert(self, key: Any, value: Any) -> 'Map':
        """Insert key-value pair (C++ style)"""
        self[key] = value
        return self

    def find(self, key: Any) -> Optional[Any]:
        """Find value by key, returns None if not found (C++ style)"""
        return self.get(key, None)

    def erase(self, key: Any) -> bool:
        """Erase key-value pair, returns True if existed"""
        if key in self:
            del self[key]
            return True
        return False

    def contains(self, key: Any) -> bool:
        """Check if key exists (C++20 style)"""
        return key in self

    def count(self, key: Any) -> int:
        """Return 1 if key exists, 0 otherwise (C++ style)"""
        return 1 if key in self else 0

    def size(self) -> int:
        """Return map size"""
        return len(self)

    def empty(self) -> bool:
        """Check if map is empty"""
        return len(self) == 0

    def at(self, key: Any) -> Any:
        """Get value at key, raises error if not found (C++ style)"""
        if key not in self:
            raise KeyError(f"Key '{key}' not found in map")
        return self[key]

    def begin(self) -> Optional[tuple]:
        """Return first key-value pair"""
        if len(self) == 0:
            return None
        first_key = next(iter(self))
        return (first_key, self[first_key])

    def end(self) -> Optional[tuple]:
        """Return last key-value pair"""
        if len(self) == 0:
            return None
        last_key = list(self.keys())[-1]
        return (last_key, self[last_key])

    def lower_bound(self, key: Any) -> Optional[Any]:
        """Find first key >= given key (for sorted keys)"""
        sorted_keys = sorted(self.keys())
        for k in sorted_keys:
            if k >= key:
                return k
        return None

    def upper_bound(self, key: Any) -> Optional[Any]:
        """Find first key > given key (for sorted keys)"""
        sorted_keys = sorted(self.keys())
        for k in sorted_keys:
            if k > key:
                return k
        return None


def create_map(key_type: str = 'dynamic', value_type: str = 'dynamic') -> Map:
    """Create a Map object"""
    return Map(key_type, value_type)


class CSSLClass:
    """Represents a CSSL class definition.

    Stores class name, member variables, methods, and constructor.
    Used by the runtime to instantiate CSSLInstance objects.
    Supports inheritance via the 'parent' attribute.
    """

    def __init__(self, name: str, members: Dict[str, Any] = None,
                 methods: Dict[str, Any] = None, constructor: Any = None,
                 parent: Any = None):
        self.name = name
        self.members = members or {}  # Default member values/types
        self.methods = methods or {}  # Method AST nodes
        self.constructor = constructor  # Constructor AST node
        self.parent = parent  # Parent class (CSSLClass or CSSLizedPythonObject)

    def get_all_members(self) -> Dict[str, Any]:
        """Get all members including inherited ones."""
        all_members = {}
        # First add parent members (can be overridden)
        if self.parent:
            if hasattr(self.parent, 'get_all_members'):
                all_members.update(self.parent.get_all_members())
            elif hasattr(self.parent, 'members'):
                all_members.update(self.parent.members)
            elif hasattr(self.parent, '_python_obj'):
                # CSSLizedPythonObject - get attributes from Python object
                py_obj = self.parent._python_obj
                if hasattr(py_obj, '__dict__'):
                    for key, val in py_obj.__dict__.items():
                        if not key.startswith('_'):
                            all_members[key] = {'type': 'dynamic', 'default': val}
        # Then add own members (override parent)
        all_members.update(self.members)
        return all_members

    def get_all_methods(self) -> Dict[str, Any]:
        """Get all methods including inherited ones."""
        all_methods = {}
        # First add parent methods (can be overridden)
        if self.parent:
            if hasattr(self.parent, 'get_all_methods'):
                all_methods.update(self.parent.get_all_methods())
            elif hasattr(self.parent, 'methods'):
                all_methods.update(self.parent.methods)
            elif hasattr(self.parent, '_python_obj'):
                # CSSLizedPythonObject - get methods from Python object
                py_obj = self.parent._python_obj
                for name in dir(py_obj):
                    if not name.startswith('_'):
                        attr = getattr(py_obj, name, None)
                        if callable(attr):
                            all_methods[name] = ('python_method', attr)
        # Then add own methods (override parent)
        all_methods.update(self.methods)
        return all_methods

    def __repr__(self):
        parent_info = f" extends {self.parent.name}" if self.parent and hasattr(self.parent, 'name') else ""
        return f"<CSSLClass '{self.name}'{parent_info} with {len(self.methods)} methods>"


class CSSLInstance:
    """Represents an instance of a CSSL class.

    Holds instance member values and provides access to class methods.
    Supports this-> member access pattern.
    """

    def __init__(self, class_def: CSSLClass):
        self._class = class_def
        self._members: Dict[str, Any] = {}
        # Initialize members with defaults from class definition (including inherited)
        all_members = class_def.get_all_members() if hasattr(class_def, 'get_all_members') else class_def.members
        for name, default in all_members.items():
            if isinstance(default, dict):
                # Type declaration with optional default
                member_type = default.get('type')
                member_default = default.get('default')

                if member_default is not None:
                    self._members[name] = member_default
                elif member_type:
                    # Create instance of container types
                    self._members[name] = self._create_default_for_type(member_type)
                else:
                    self._members[name] = None
            else:
                self._members[name] = default

    def _create_default_for_type(self, type_name: str) -> Any:
        """Create a default value for a given type name."""
        # Container types
        if type_name == 'map':
            return Map()
        elif type_name in ('stack',):
            return Stack()
        elif type_name in ('vector',):
            return Vector()
        elif type_name in ('array',):
            return Array()
        elif type_name in ('list',):
            return List()
        elif type_name in ('dictionary', 'dict'):
            return Dictionary()
        elif type_name == 'datastruct':
            return DataStruct()
        elif type_name == 'dataspace':
            return DataSpace()
        elif type_name == 'shuffled':
            return Shuffled()
        elif type_name == 'iterator':
            return Iterator()
        elif type_name == 'combo':
            return Combo()
        # Primitive types
        elif type_name == 'int':
            return 0
        elif type_name == 'float':
            return 0.0
        elif type_name == 'string':
            return ""
        elif type_name == 'bool':
            return False
        elif type_name == 'json':
            return {}
        return None

    def get_member(self, name: str) -> Any:
        """Get member value by name"""
        if name in self._members:
            return self._members[name]
        raise AttributeError(f"'{self._class.name}' has no member '{name}'")

    def set_member(self, name: str, value: Any) -> None:
        """Set member value by name"""
        self._members[name] = value

    def has_member(self, name: str) -> bool:
        """Check if member exists"""
        return name in self._members

    def get_method(self, name: str) -> Any:
        """Get method AST node by name (including inherited methods)"""
        # Use get_all_methods to include inherited methods
        all_methods = self._class.get_all_methods() if hasattr(self._class, 'get_all_methods') else self._class.methods
        if name in all_methods:
            return all_methods[name]
        raise AttributeError(f"'{self._class.name}' has no method '{name}'")

    def has_method(self, name: str) -> bool:
        """Check if method exists (including inherited methods)"""
        all_methods = self._class.get_all_methods() if hasattr(self._class, 'get_all_methods') else self._class.methods
        return name in all_methods

    def __getattr__(self, name: str) -> Any:
        """Allow direct attribute access for members"""
        if name.startswith('_'):
            raise AttributeError(name)
        if name in self._members:
            return self._members[name]
        raise AttributeError(f"'{self._class.name}' has no member '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow direct attribute setting for members"""
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            if hasattr(self, '_members'):
                self._members[name] = value
            else:
                object.__setattr__(self, name, value)

    def __repr__(self):
        return f"<{self._class.name} instance at 0x{id(self):x}>"

    def __str__(self):
        return f"<{self._class.name} instance at 0x{id(self):x}>"


class UniversalInstance:
    """Universal shared container accessible from CSSL, Python, and C++.

    Created via instance<"name"> syntax in CSSL or getInstance("name") in Python.
    Supports dynamic member/method injection via +<<== operator.

    Example CSSL:
        instance<"myContainer"> container;
        container +<<== { void sayHello() { printl("Hello!"); } }
        container.sayHello();

    Example Python:
        container = cssl.getInstance("myContainer")
        container.sayHello()
    """

    # Global registry for all universal instances
    _registry: Dict[str, 'UniversalInstance'] = {}

    def __init__(self, name: str):
        self._name = name
        self._members: Dict[str, Any] = {}
        self._methods: Dict[str, Any] = {}  # Method name -> AST node or callable
        self._injections: List[Any] = []  # Code blocks injected via +<<==
        self._runtime = None  # Weak reference to CSSL runtime for method calls
        # Register globally
        UniversalInstance._registry[name] = self

    @classmethod
    def get_or_create(cls, name: str) -> 'UniversalInstance':
        """Get existing instance or create new one."""
        if name in cls._registry:
            return cls._registry[name]
        return cls(name)

    @classmethod
    def get(cls, name: str) -> Optional['UniversalInstance']:
        """Get existing instance by name, returns None if not found."""
        return cls._registry.get(name)

    @classmethod
    def exists(cls, name: str) -> bool:
        """Check if instance exists."""
        return name in cls._registry

    @classmethod
    def delete(cls, name: str) -> bool:
        """Delete instance from registry."""
        if name in cls._registry:
            del cls._registry[name]
            return True
        return False

    @classmethod
    def clear_all(cls) -> int:
        """Clear all instances. Returns count of cleared instances."""
        count = len(cls._registry)
        cls._registry.clear()
        return count

    @classmethod
    def list_all(cls) -> List[str]:
        """List all instance names."""
        return list(cls._registry.keys())

    @property
    def name(self) -> str:
        """Get instance name."""
        return self._name

    def set_member(self, name: str, value: Any) -> None:
        """Set a member value."""
        self._members[name] = value

    def get_member(self, name: str) -> Any:
        """Get a member value."""
        if name in self._members:
            return self._members[name]
        raise AttributeError(f"Instance '{self._name}' has no member '{name}'")

    def has_member(self, name: str) -> bool:
        """Check if member exists."""
        return name in self._members

    def set_runtime(self, runtime: Any) -> None:
        """Set the runtime reference for method calls from Python."""
        import weakref
        self._runtime = weakref.ref(runtime)

    def set_method(self, name: str, method: Any, runtime: Any = None) -> None:
        """Set a method (AST node or callable)."""
        self._methods[name] = method
        if runtime is not None and self._runtime is None:
            self.set_runtime(runtime)

    def get_method(self, name: str) -> Any:
        """Get a method by name."""
        if name in self._methods:
            return self._methods[name]
        raise AttributeError(f"Instance '{self._name}' has no method '{name}'")

    def has_method(self, name: str) -> bool:
        """Check if method exists."""
        return name in self._methods

    def add_injection(self, code_block: Any) -> None:
        """Add a code injection (from +<<== operator)."""
        self._injections.append(code_block)

    def get_injections(self) -> List[Any]:
        """Get all injected code blocks."""
        return self._injections

    def get_all_members(self) -> Dict[str, Any]:
        """Get all members."""
        return dict(self._members)

    def get_all_methods(self) -> Dict[str, Any]:
        """Get all methods."""
        return dict(self._methods)

    def __getattr__(self, name: str) -> Any:
        """Allow direct attribute access for members and methods."""
        if name.startswith('_'):
            raise AttributeError(name)
        if name in object.__getattribute__(self, '_members'):
            return object.__getattribute__(self, '_members')[name]
        if name in object.__getattribute__(self, '_methods'):
            method = object.__getattribute__(self, '_methods')[name]
            runtime_ref = object.__getattribute__(self, '_runtime')

            # If method is an AST node and we have a runtime, create a callable wrapper
            if hasattr(method, 'type') and method.type == 'function' and runtime_ref is not None:
                runtime = runtime_ref()  # Dereference weakref
                if runtime is not None:
                    instance = self
                    def method_caller(*args, **kwargs):
                        # Set 'this' context and call the method
                        old_this = runtime.scope.get('this')
                        runtime.scope.set('this', instance)
                        try:
                            return runtime._call_function(method, list(args))
                        finally:
                            if old_this is not None:
                                runtime.scope.set('this', old_this)
                            elif hasattr(runtime.scope, 'remove'):
                                runtime.scope.remove('this')
                    return method_caller
            # Return method directly if already callable or no runtime
            return method
        raise AttributeError(f"Instance '{object.__getattribute__(self, '_name')}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow direct attribute setting for members."""
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            if hasattr(self, '_members'):
                self._members[name] = value
            else:
                object.__setattr__(self, name, value)

    def __repr__(self):
        members = len(self._members)
        methods = len(self._methods)
        return f"<UniversalInstance '{self._name}' ({members} members, {methods} methods)>"

    def __str__(self):
        return f"<UniversalInstance '{self._name}'>"


__all__ = [
    'DataStruct', 'Shuffled', 'Iterator', 'Combo', 'DataSpace', 'OpenQuote',
    'OpenFind', 'Parameter', 'Stack', 'Vector', 'Array', 'List', 'Dictionary', 'Map',
    'CSSLClass', 'CSSLInstance', 'UniversalInstance',
    'create_datastruct', 'create_shuffled', 'create_iterator',
    'create_combo', 'create_dataspace', 'create_openquote', 'create_parameter',
    'create_stack', 'create_vector', 'create_array', 'create_list', 'create_dictionary', 'create_map'
]
