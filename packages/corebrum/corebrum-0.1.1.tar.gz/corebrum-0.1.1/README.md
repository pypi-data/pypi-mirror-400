# Corebrum Python Library

Execute Python code transparently on Corebrum's distributed compute infrastructure with minimal code changes.

## Installation

Install Corebrum using pip:

```bash
pip install corebrum
```

## Quick Start

### Using the Decorator Pattern

Decorate your functions to execute them on Corebrum:

```python
import corebrum

# Configure Corebrum connection (optional, defaults to http://localhost:6502)
corebrum.configure(
    base_url="http://localhost:6502",
    identity_id="your-identity-id"  # Optional
)

# Decorate function to run on Corebrum
@corebrum.run()
def process_data(data):
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(data)
    result = df.describe().to_dict()
    return result

# Call normally - executes on Corebrum
result = process_data([
    {"x": 1, "y": 2},
    {"x": 3, "y": 4},
    {"x": 5, "y": 6}
])

print(result)
```

### Using the Execute Method

Execute raw Python code directly:

```python
import corebrum

# Execute code with inputs
result = corebrum.execute("""
import math

def calculate():
    return math.sqrt(144)

# Must assign to a variable for execute() to capture it
result = calculate()
""", input_data={}, name="calculate_task")

print(result)  # 12.0
```

### With Input Data

```python
@corebrum.run()
def train_model(dataset_url, epochs=10):
    import torch
    # Your training code here
    return {"accuracy": 0.95, "loss": 0.05}

result = train_model("https://example.com/data.csv", epochs=20)
```

## Features

- **Transparent Execution**: Code runs as if it were local, but executes on Corebrum's distributed infrastructure
- **Automatic Dependency Detection**: Automatically detects and includes Python package dependencies
- **Input/Output Serialization**: Handles JSON-serializable inputs and outputs automatically
- **Error Handling**: Corebrum errors surface naturally as Python exceptions
- **Identity Support**: Works with Corebrum's identity and memory system
- **Timeout Control**: Configurable task timeouts
- **Progress Tracking**: Real-time status updates via Server-Sent Events (SSE)

## API Reference

### `Corebrum` Class

Main client class for interacting with Corebrum.

```python
client = Corebrum(
    base_url="http://localhost:6502",  # Corebrum web server URL
    identity_id=None,                   # Optional identity ID
    timeout=300,                        # Task timeout in seconds
    poll_interval=2.0,                  # Polling interval for status checks
    max_poll_attempts=300,              # Maximum polling attempts
)
```

### `@run()` Decorator

Execute a function on Corebrum.

```python
@client.run()
def my_function(x, y):
    return x + y

result = my_function(1, 2)  # Executes on Corebrum
```

**Options:**
- `input`: Additional input data dictionary
- `identity_id`: Override identity ID for this task
- `timeout`: Override timeout for this task

### `execute()` Method

Execute raw Python code on Corebrum.

```python
result = client.execute(
    code="""
def add(x, y):
    return x + y

# Must assign result to a variable for execute() to capture it
result = add(x, y)
""",
    input_data={"x": 1, "y": 2},  # Required: explicit input data
    name="my_task",                # Optional task name
    dependencies=["pandas"],        # Optional dependencies
)
```

## `run()` vs `execute()`: When to Use Which?

Both `run()` and `execute()` submit tasks to Corebrum and wait for results, but they differ in how they handle code and inputs:

### `corebrum.run()` - Decorator for Functions

**Purpose**: Decorator to run an existing function on Corebrum

**Best for**:
- Existing functions you want to run remotely
- When you want automatic argument extraction
- Minimal code changes (just add a decorator)

**How it works**:
- Extracts the function's source code using `inspect.getsource()`
- Automatically extracts function arguments from the function call
- Wraps the function definition and calls it with the extracted inputs
- Uses the function's return value as the result

**Example**:
```python
@corebrum.run()
def factorial(number):
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if number == 0 or number == 1:
        return 1
    result = 1
    for i in range(2, number + 1):
        result *= i
    return result

# Call it normally - arguments are automatically extracted
result = factorial(8)  # Executes on Corebrum
```

### `corebrum.execute()` - Execute Raw Code

**Purpose**: Execute raw Python code strings on Corebrum

**Best for**:
- Raw code strings (not in a function)
- Dynamic code generation
- When you need more control over input/output structure
- Working with code that isn't in a function

**How it works**:
- Executes the code directly (no function extraction needed)
- Requires explicit `input_data` dictionary
- Captures results by looking for common variable names (`result`, `output`, `data`, `value`, `answer`, `res`)
- Executes code in module namespace

**Example**:
```python
code = """
def factorial(number):
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if number == 0 or number == 1:
        return 1
    result = 1
    for i in range(2, number + 1):
        result *= i
    return result

# Must assign to a variable for execute() to capture it
result = factorial(number)
"""

result = corebrum.execute(
    code,
    input_data={"number": 8},
    name="factorial_task"
)
```

### Comparison Table

| Feature | `run()` | `execute()` |
|---------|---------|-------------|
| **Input** | Function object | Code string |
| **Arguments** | Auto-extracted from function call | Explicit `input_data` dict |
| **Code extraction** | Uses `inspect.getsource()` | Uses provided string |
| **Result capture** | Function return value | Looks for variables (`result`, `output`, etc.) |
| **Use case** | Existing functions you want to run remotely | Ad-hoc code, dynamic code generation |
| **Convenience** | Higher (just add decorator) | Lower (must structure code manually) |
| **Flexibility** | Lower (must be a function) | Higher (any code structure) |

### Quick Decision Guide

**Use `run()` when**:
- ✅ You have an existing function
- ✅ You want automatic argument extraction
- ✅ You want minimal code changes
- ✅ The code is already in a function

**Use `execute()` when**:
- ✅ You have raw code strings
- ✅ You're generating code dynamically
- ✅ You need more control over input/output structure
- ✅ You're working with code that isn't in a function
- ✅ You want to execute scripts or multi-statement code blocks

### Global Functions

For convenience, you can use global functions:

```python
import corebrum

# Configure global instance
corebrum.configure(base_url="http://localhost:6502")

# Use global decorator
@corebrum.run()
def my_function():
    return "Hello"

# Use global execute
result = corebrum.execute("print(42)")
```

## Examples

### Data Processing

```python
@corebrum.run()
def analyze_dataset(url):
    import pandas as pd
    import numpy as np
    
    df = pd.read_csv(url)
    return {
        "mean": df.mean().to_dict(),
        "std": df.std().to_dict(),
        "count": len(df)
    }

result = analyze_dataset("https://example.com/data.csv")
```

### Machine Learning

```python
@corebrum.run()
def train_classifier(features, labels):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    
    clf = RandomForestClassifier()
    scores = cross_val_score(clf, features, labels, cv=5)
    
    return {
        "mean_accuracy": scores.mean(),
        "std_accuracy": scores.std()
    }

result = train_classifier(X_train, y_train)
```

### Parallel Processing

```python
import corebrum
from concurrent.futures import ThreadPoolExecutor

@corebrum.run()
def process_chunk(chunk):
    # Process data chunk
    return sum(chunk)

chunks = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Submit multiple tasks in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
    results = [f.result() for f in futures]

print(results)  # [6, 15, 24]
```

## Example Scripts

The repository includes several example scripts in the `examples/` directory that demonstrate different use cases:

### `basic_usage.py`

Basic examples covering fundamental Corebrum usage:

- **Example 1**: Simple function execution with `@run()` decorator
- **Example 2**: Data processing with pandas (demonstrates automatic dependency installation)
- **Example 3**: Mathematical computations using standard library
- **Example 4**: Using `execute()` method for raw code execution

**Run it:**
```bash
python examples/basic_usage.py
```

### `advanced_usage.py`

Advanced features and patterns:

- **Example 1**: Functions with default arguments
- **Example 2**: Error handling and exception catching
- **Example 3**: Custom timeout configuration
- **Example 4**: Using identity context for memory access
- **Example 5**: `execute()` with input data
- **Example 6**: Comprehensive error handling patterns

**Run it:**
```bash
python examples/advanced_usage.py
```

### `factorial_demo.py`

Comprehensive demonstration comparing `run()` vs `execute()`:

- **Method 1**: Using `@run()` decorator - best for existing functions
- **Method 2**: Using `execute()` method - best for raw code strings
- **Method 3**: Parallel execution of multiple factorial calculations
- Includes detailed comments explaining when to use each approach

**Run it:**
```bash
python examples/factorial_demo.py
```

## Error Handling

Corebrum provides specific exception types:

```python
from corebrum.exceptions import (
    CorebrumError,
    TaskSubmissionError,
    TaskExecutionError,
    TaskTimeoutError,
)

try:
    result = my_function()
except TaskSubmissionError as e:
    print(f"Failed to submit task: {e}")
except TaskExecutionError as e:
    print(f"Task execution failed: {e}")
except TaskTimeoutError as e:
    print(f"Task timed out: {e}")
```

## Limitations

1. **Serialization**: Only JSON-serializable inputs and outputs are supported
2. **Dependencies**: Python packages must be available on Corebrum workers
3. **File I/O**: Local file access won't work (use URLs or Corebrum storage)
4. **Interactive Code**: Functions must be defined in files, not interactively
5. **State**: Functions should be stateless (no global state persistence)

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/Corebrum/corebrum-pip.git
cd corebrum-pip

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=corebrum --cov-report=html

# Run specific test file
pytest tests/test_corebrum.py
```

### Code Formatting

```bash
# Format code
black corebrum tests

# Check linting
flake8 corebrum tests

# Type checking
mypy corebrum
```

## Requirements

- Python 3.7+
- Corebrum server running and accessible
- Network access to Corebrum web server

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Documentation**: [GitHub README](https://github.com/Corebrum/corebrum-pip#readme)
- **Issues**: [GitHub Issues](https://github.com/Corebrum/corebrum-pip/issues)
- **Email**: hello@corebrum.com

## Changelog

### 0.1.0 (2025-01-02)
- Initial release
- Decorator pattern support (`@run()`)
- `execute()` method for raw code execution
- Automatic dependency detection
- Input/output serialization
- Error handling and exceptions
- Identity support
- Timeout configuration
