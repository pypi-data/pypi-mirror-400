# Corebrum Python Library Examples

This directory contains example scripts demonstrating how to use the Corebrum Python library.

## Examples

### `basic_usage.py`
Basic examples showing:
- Simple function execution
- Data processing with pandas
- Mathematical computations
- Using the `execute()` method

**Run:**
```bash
python examples/basic_usage.py
```

### `advanced_usage.py`
Advanced examples showing:
- Functions with default arguments
- Error handling
- Custom timeouts
- Identity context
- Execute with inputs

**Run:**
```bash
python examples/advanced_usage.py
```

### `factorial_demo.py`
Factorial calculation demo that mimics the Corebrum CLI command:
```bash
corebrum submit --file https://gist.github.com/chrismatthieu/e06cdd5c6c3787d7e68e2c6977d81e9e --input '{"number": 8}'
```

This demo shows three different ways to calculate factorials using Corebrum:
1. Using the `@corebrum.run()` decorator
2. Using `corebrum.execute()` method
3. Recursive factorial implementation

**Run:**
```bash
python examples/factorial_demo.py
```

## Prerequisites

Before running the examples, make sure:

1. **Corebrum server is running**: The examples connect to `http://localhost:6502` by default
   - Start Corebrum: `corebrum web` or `corebrum daemon`
   - Or update the `base_url` in the examples to point to your Corebrum server

2. **Corebrum Python library is installed**:
   ```bash
   pip install -e .
   ```

3. **Required dependencies are available on Corebrum workers**:
   - For examples using pandas: `pandas` must be installed on workers
   - Standard library modules work out of the box

## Configuration

You can configure the examples by modifying the `corebrum.configure()` call:

```python
corebrum.configure(
    base_url="http://your-corebrum-server:6502",
    identity_id="your-identity-id",  # Optional
    timeout=600  # Optional, in seconds
)
```

## Troubleshooting

### Connection Errors
If you see connection errors:
- Verify Corebrum server is running: `curl http://localhost:6502/api/jobs`
- Check firewall/network settings
- Update `base_url` if Corebrum is running on a different host/port

### Import Errors
If you see import errors:
- Make sure the package is installed: `pip install -e .`
- Check Python version (requires Python 3.7+)

### Task Execution Errors
If tasks fail:
- Check Corebrum worker logs
- Verify required dependencies are installed on workers
- Check task timeout settings

