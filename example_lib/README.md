# example_lib

Template for creating new Python libraries in the monorepo.

## Structure

```
example_lib/
├── __init__.py           # Package initialization, public API
├── core.py               # Core functionality
├── utils/
│   ├── __init__.py      # Utils subpackage
│   └── helpers.py       # Helper functions
├── test_core.py         # Tests for core module
├── test_utils.py        # Tests for utils module
├── BUILD                # Pants build configuration
└── README.md            # This file
```

## Usage

```python
from example_lib.core import ExampleClass, process_data
from example_lib.utils import validate_input, format_output

# Create an instance
obj = ExampleClass("my-object", value=10)
obj.increment(5)
print(obj)  # ExampleClass(name='my-object', value=15)

# Process data
result = process_data([1, 2, 3])
print(result)  # [2, 4, 6]

# Validate input
is_valid = validate_input("test")
print(is_valid)  # True

# Format output
output = format_output({"key": "value"})
print(output)  # key: value
```

## Testing

```bash
# Run all tests for this library
pants test example_lib::

# Run specific test file
pants test example_lib/test_core.py

# Run specific test function
pants test example_lib/test_core.py::test_example_class_init
```

## Development

```bash
# Format code
pants fmt example_lib::

# Lint code
pants lint example_lib::

# Check dependencies
pants dependencies example_lib::

# Check what depends on this library
pants dependees example_lib::
```

## Adding to Other Projects

To use this library in another package:

```python
# In your BUILD file, Pants will automatically detect the import
# No explicit dependency needed (auto-inferred)

# Or explicitly add dependency:
python_sources(
    dependencies=["//example_lib"],
)
```

## API Documentation

### Core Module (`core.py`)

#### `ExampleClass`
A sample class demonstrating proper structure.

**Attributes:**
- `name` (str): Object name
- `value` (int): Numeric value

**Methods:**
- `increment(amount=1)`: Increment value by amount

#### `process_data(data)`
Process a list of data items.

**Args:**
- `data` (list): Input data

**Returns:**
- list: Processed data

### Utils Module (`utils/`)

#### `validate_input(value)`
Validate string input.

**Args:**
- `value` (str): Value to validate

**Returns:**
- bool: True if valid

#### `format_output(data)`
Format dictionary as string.

**Args:**
- `data` (dict): Data to format

**Returns:**
- str: Formatted output

## Best Practices

This template follows these best practices:

1. **Type Hints**: All functions have type annotations
2. **Docstrings**: Google-style docstrings for all public APIs
3. **Tests**: Comprehensive test coverage
4. **Structure**: Clear separation of concerns
5. **Public API**: Controlled via `__all__` in `__init__.py`
6. **Imports**: Use `from __future__ import annotations` for forward compatibility

## Creating a New Library

To create a new library based on this template:

1. **Copy the structure:**
   ```bash
   cp -r example_lib my_new_lib
   ```

2. **Update files:**
   - `__init__.py`: Update metadata (version, author, etc.)
   - `core.py`: Implement your core functionality
   - `utils/`: Add utility functions as needed
   - `test_*.py`: Write tests for your code
   - `README.md`: Document your library

3. **Generate BUILD file:**
   ```bash
   make tailor
   ```

4. **Test it:**
   ```bash
   pants test my_new_lib::
   ```

5. **Use it:**
   ```python
   from my_new_lib import MyClass
   ```

## License

[Your License Here]
