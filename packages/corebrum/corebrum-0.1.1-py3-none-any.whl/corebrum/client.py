"""
Corebrum client for executing Python code on distributed compute infrastructure.
"""

import ast
import inspect
import json
import os
import sys
import time
from typing import Any, Callable, Optional, Dict, List, Union
from functools import wraps

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    CorebrumError,
    TaskSubmissionError,
    TaskExecutionError,
    TaskTimeoutError,
)


class Corebrum:
    """
    Corebrum client for executing Python code on distributed infrastructure.
    
    Args:
        base_url: Base URL of Corebrum web server (default: http://localhost:6502)
        identity_id: Optional identity ID for memory context
        timeout: Task timeout in seconds (default: 300)
        poll_interval: Polling interval for status checks in seconds (default: 2)
        max_poll_attempts: Maximum number of polling attempts (default: 300)
    
    Example::
        
        corebrum = Corebrum(base_url="http://localhost:6502")
        
        @corebrum.run()
        def my_function(x, y):
            return x + y
        
        result = my_function(1, 2)  # Executes on Corebrum
    """
    
    # Standard library modules that don't need to be in dependencies
    _STDLIB_MODULES = {
        'os', 'sys', 'json', 'time', 'datetime', 'math', 'random', 'collections',
        'itertools', 'functools', 'operator', 'string', 're', 'hashlib', 'base64',
        'urllib', 'http', 'email', 'csv', 'xml', 'html', 'sqlite3', 'pickle',
        'copy', 'gc', 'inspect', 'ast', 'types', 'typing', 'dataclasses', 'enum',
        'abc', 'contextlib', 'pathlib', 'io', 'tempfile', 'shutil', 'glob',
        'fnmatch', 'linecache', 'locale', 'gettext', 'unicodedata', 'codecs',
        'traceback', 'warnings', 'logging', 'weakref', 'array', 'struct', 'mmap',
        'ctypes', 'threading', 'multiprocessing', 'queue', 'concurrent', 'asyncio',
        'selectors', 'socket', 'ssl', 'socketserver', 'http', 'urllib', 'email',
        'json', 'mailbox', 'mimetypes', 'base64', 'binhex', 'binascii', 'quopri',
        'uu', 'html', 'xml', 'secrets', 'statistics', 'decimal', 'fractions',
        'numbers', 'cmath', 'random', 'secrets', 'statistics'
    }
    
    def __init__(
        self,
        base_url: str = "http://localhost:6502",
        identity_id: Optional[str] = None,
        timeout: int = 300,
        poll_interval: float = 2.0,
        max_poll_attempts: int = 300,
    ):
        self.base_url = base_url.rstrip('/')
        self.identity_id = identity_id
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_poll_attempts = max_poll_attempts
        
        # Create session with retry strategy and connection pooling
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=5,  # Limit connection pool size (reduce to avoid overwhelming server)
            pool_maxsize=5,     # Limit max connections per host
            pool_block=False,   # Don't block if pool is full, raise error instead
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def run(self, func: Optional[Callable] = None, **kwargs):
        """
        Decorator to execute function on Corebrum.
        
        Args:
            func: Function to decorate (if None, returns decorator)
            **kwargs: Additional options (input, identity_id, timeout, etc.)
        
        Returns:
            Decorated function that executes on Corebrum
        
        Example::
            
            @corebrum.run()
            def process_data(data):
                import pandas as pd
                return pd.DataFrame(data).describe().to_dict()
            
            result = process_data([{"x": 1}, {"x": 2}])
        """
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **func_kwargs):
                # Get source code
                try:
                    source = inspect.getsource(f)
                except OSError:
                    raise TaskSubmissionError(
                        f"Could not get source code for {f.__name__}. "
                        "Make sure the function is defined in a file, not interactively."
                    )
                
                # Get function name
                func_name = f.__name__
                
                # Extract inputs
                inputs = self._extract_inputs(f, args, func_kwargs)
                
                # Merge with decorator kwargs
                if 'input' in kwargs:
                    if isinstance(kwargs['input'], dict):
                        inputs.update(kwargs['input'])
                    else:
                        inputs['input'] = kwargs['input']
                
                # Detect dependencies
                dependencies = self._detect_dependencies(source)
                
                # Create wrapper code that calls the function
                wrapper_code = self._create_wrapper_code(source, func_name, inputs)
                
                # Create task definition
                task_def = self._create_task_definition(
                    name=func_name,
                    code=wrapper_code,
                    inputs=inputs,
                    dependencies=dependencies,
                    timeout=kwargs.get('timeout', self.timeout),
                )
                
                # Submit and wait
                return self._submit_and_wait(
                    task_def,
                    inputs,
                    identity_id=kwargs.get('identity_id', self.identity_id),
                )
            
            return wrapper
        
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def execute(
        self,
        code: str,
        input_data: Optional[Dict[str, Any]] = None,
        name: str = "inline_task",
        dependencies: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Execute raw Python code on Corebrum.
        
        Args:
            code: Python code to execute
            input_data: Optional input data dictionary
            name: Task name (default: "inline_task")
            dependencies: Optional list of dependencies (auto-detected if None)
            **kwargs: Additional options (identity_id, timeout, etc.)
        
        Returns:
            Execution result
        
        Example::
            
            result = corebrum.execute(\"\"\"
                import math
                def calculate():
                    return math.sqrt(144)
                calculate()
            \"\"\")
            print(result)  # 12.0
        """
        if dependencies is None:
            dependencies = self._detect_dependencies(code)
        
        try:
            # Create wrapper code
            wrapper_code = self._create_execute_wrapper(code, input_data or {})
            
            # Create task definition
            task_def = self._create_task_definition(
                name=name,
                code=wrapper_code,
                inputs=input_data or {},
                dependencies=dependencies,
                timeout=kwargs.get('timeout', self.timeout),
            )
            
            # Submit and wait
            return self._submit_and_wait(
                task_def,
                input_data,
                identity_id=kwargs.get('identity_id', self.identity_id),
            )
        except Exception as e:
            # Wrap any errors during task creation/submission
            if isinstance(e, (TaskSubmissionError, TaskExecutionError, TaskTimeoutError)):
                raise
            raise TaskSubmissionError(f"Failed to create or submit task '{name}': {e}")
    
    def _create_wrapper_code(self, source: str, func_name: str, inputs: Dict[str, Any]) -> str:
        """Create wrapper code that calls the function and returns result."""
        # Extract just the function definition and body
        lines = source.split('\n')
        
        # Find function definition
        func_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and func_name in line:
                func_start = i
                break
        
        if func_start is None:
            raise TaskSubmissionError(f"Could not find function definition for {func_name}")
        
        # Get function body (everything after def)
        func_lines = lines[func_start:]
        
        # Remove decorators if present
        while func_lines and not func_lines[0].strip().startswith('def '):
            func_lines.pop(0)
        
        func_code = '\n'.join(func_lines)
        
        # Create wrapper that calls the function with inputs
        input_vars = []
        for key in inputs.keys():
            input_vars.append(f"{key} = inputs.get('{key}')")
        
        wrapper = f"""import json

# Input data
inputs = {json.dumps(inputs)}

# Set input variables
{chr(10).join(input_vars)}

# Function code
{func_code}

# Call function and return result
try:
    result = {func_name}({', '.join(inputs.keys())})
    print(json.dumps(result))
except Exception as e:
    import traceback
    # Print error as JSON to stdout
    # The client will check for "error" key and raise TaskExecutionError
    error_output = json.dumps({{
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }})
    print(error_output)
    # Don't raise or exit - let the process complete normally
    # The client's _extract_result will detect the error and raise TaskExecutionError
"""
        return wrapper
    
    def _create_execute_wrapper(self, code: str, inputs: Dict[str, Any]) -> str:
        """Create wrapper code for execute() method."""
        import textwrap
        
        # Dedent the user's code to remove common leading whitespace
        # This handles cases where code is provided with indentation (e.g., from triple-quoted strings)
        dedented_code = textwrap.dedent(code).strip()
        
        input_vars = []
        for key, value in inputs.items():
            input_vars.append(f"{key} = {json.dumps(value)}")
        
        # For execute(), wrap the code to capture its result
        # Execute code directly - variables will be in the module namespace
        wrapper = f"""import json

# Input data
{chr(10).join(input_vars)}

# User code (may define functions, variables, etc.)
{dedented_code}

# Capture result - check for common result variable names in current namespace
# Variables defined in the code above are in the global namespace of this script
# Use a different variable name to avoid overwriting user's result
captured_result = None
# Check globals() since we're at module level
for var_name in ['result', 'output', 'data', 'value', 'answer', 'res']:
    if var_name in globals():
        captured_result = globals()[var_name]
        break

# If no result found, return error message
if captured_result is None:
    captured_result = {{"error": "No result variable found. Please assign the result to a variable (e.g., result = factorial(number)) or print JSON output."}}

# Print result as JSON
print(json.dumps(captured_result))
"""
        return wrapper
    
    def _create_task_definition(
        self,
        name: str,
        code: str,
        inputs: Dict[str, Any],
        dependencies: List[str],
        timeout: int,
    ) -> Dict[str, Any]:
        """Create a Corebrum TaskDefinition from Python code."""
        # API requires timeout_seconds to always be present (u32)
        # and dependencies to always be present (even if empty array)
        # inputs and outputs arrays are also required
        task_def = {
            "name": name,
            "version": "1.0.0",
            "description": f"Auto-generated task: {name}",  # Required field
            "compute_logic": {
                "type": "script",  # Required: "script" for Python code execution (not "python")
                "language": "python",
                "code": code,
                "timeout_seconds": timeout,  # Required u32 field
            },
            "dependencies": dependencies if dependencies else [],  # Always present
            "inputs": [{"name": k, "type": "any"} for k in inputs.keys()],  # Required array
            "outputs": [{"name": "result", "type": "any"}],  # Required array
        }
        
        return task_def
    
    def _extract_inputs(self, func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Extract function inputs as JSON-serializable dict."""
        sig = inspect.signature(func)
        try:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
        except TypeError as e:
            raise TaskSubmissionError(f"Invalid function arguments: {e}")
        
        inputs = {}
        for name, value in bound.arguments.items():
            if self._is_json_serializable(value):
                inputs[name] = value
            else:
                # Try to convert to string representation
                inputs[name] = str(value)
        
        return inputs
    
    def _detect_dependencies(self, code: str) -> List[str]:
        """Detect Python imports from code."""
        dependencies = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        if module not in self._STDLIB_MODULES:
                            dependencies.append(module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        if module not in self._STDLIB_MODULES:
                            dependencies.append(module)
        except SyntaxError:
            # If code has syntax errors, we'll let Corebrum handle it
            pass
        
        # Remove duplicates while preserving order
        seen = set()
        unique_deps = []
        for dep in dependencies:
            if dep not in seen:
                seen.add(dep)
                unique_deps.append(dep)
        
        return unique_deps
    
    def _is_json_serializable(self, obj: Any) -> bool:
        """Check if object is JSON serializable."""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False
    
    def _submit_and_wait(
        self,
        task_def: Dict[str, Any],
        input_data: Optional[Dict[str, Any]],
        identity_id: Optional[str] = None,
    ) -> Any:
        """Submit task to Corebrum and wait for results."""
        # Prepare request payload
        payload = {
            "task_definition": task_def,
        }
        
        # API expects input as a JSON string - always include it, even if empty
        if input_data:
            payload["input"] = json.dumps(input_data)
        else:
            payload["input"] = "{}"  # Empty JSON object as string
        
        if identity_id:
            payload["identity_id"] = identity_id
        
        # Submit task
        task_id_from_headers = None  # Initialize before try block
        try:
            # For stream=True, we need a longer timeout for the initial connection
            # The server needs time to accept the request and start the SSE stream
            # Use a tuple: (connect_timeout, read_timeout)
            # Connect timeout: fail fast if server is unreachable
            # Read timeout: allow time for server to start streaming
            import time as time_module
            submit_start = time_module.time()
            
            # Make POST request with timeout
            # Use shorter connect timeout to fail fast if server is unreachable
            # But allow longer read timeout for server to start SSE stream
            try:
                # Ensure we're actually making the request
                response = self.session.post(
                    f"{self.base_url}/api/submit-and-wait",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    stream=True,  # SSE stream
                    timeout=(3, 20),  # (connect: 3s, read: 20s) - shorter timeouts to fail faster
                )
            except requests.exceptions.ConnectTimeout:
                raise TaskSubmissionError(
                    f"Failed to connect to server at {self.base_url} within 3 seconds. "
                    "Please ensure the Corebrum server is running and accessible."
                )
            except requests.exceptions.ReadTimeout:
                raise TaskSubmissionError(
                    f"Server at {self.base_url} did not respond within 20 seconds. "
                    "The server may be overloaded or the request may be too large. "
                    "This may indicate the server is not processing the request."
                )
            except requests.exceptions.Timeout as e:
                # Catch any other timeout exceptions
                raise TaskSubmissionError(
                    f"Request to {self.base_url} timed out: {e}. "
                    "The server may be overloaded or unreachable."
                )
            except Exception as e:
                # Catch any other exceptions during POST request
                raise TaskSubmissionError(
                    f"Failed to submit task: {e}. "
                    f"This may indicate a connection issue or server problem."
                )
            submit_elapsed = time_module.time() - submit_start
            
            # Check response status before raising
            # Note: With stream=True, we might get 200 even if there's an error in the stream
            # But if we get a non-200 status, the request definitely failed
            if response.status_code not in (200, 201):
                # Try to get error details from response
                error_detail = f"HTTP {response.status_code}"
                try:
                    # For streamed responses, we need to read the content carefully
                    # But first, let's try to get error from headers or initial response
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'error' in error_data:
                        error_detail = error_data['error']
                    elif isinstance(error_data, dict) and 'message' in error_data:
                        error_detail = error_data['message']
                    elif response.text:
                        error_detail = response.text[:500]
                except (ValueError, json.JSONDecodeError):
                    # If we can't parse JSON, try to get text
                    try:
                        # For streamed responses, text might not be available immediately
                        if hasattr(response, 'text') and response.text:
                            error_detail = response.text[:500]
                        else:
                            error_detail = f"HTTP {response.status_code}: {response.reason}"
                    except:
                        error_detail = f"HTTP {response.status_code}"
                
                # Close the response before raising
                try:
                    response.close()
                except:
                    pass
                
                raise TaskSubmissionError(
                    f"Failed to submit task: Server returned {response.status_code}. {error_detail}. "
                    f"This means the task was NOT submitted to Corebrum."
                )
            
            response.raise_for_status()
            
            # Check response headers for task_id (some APIs return it there)
            if hasattr(response, 'headers'):
                task_id_from_headers = (
                    response.headers.get('X-Task-Id') or
                    response.headers.get('Task-Id') or
                    response.headers.get('X-Corebrum-Task-Id') or
                    response.headers.get('Location')  # Sometimes task_id is in Location header
                )
                # Extract task_id from Location header if it's a URL
                if task_id_from_headers and task_id_from_headers.startswith('http'):
                    # Try to extract task_id from URL path
                    import re
                    match = re.search(r'/([a-f0-9-]{36})', task_id_from_headers)
                    if match:
                        task_id_from_headers = match.group(1)
        except requests.exceptions.HTTPError as e:
            # Try to extract error message from response
            error_msg = f"Failed to submit task: {e}"
            if hasattr(e.response, 'text') and e.response.text:
                try:
                    error_data = e.response.json()
                    if isinstance(error_data, dict) and 'error' in error_data:
                        error_msg = f"Failed to submit task: {error_data['error']}"
                    elif isinstance(error_data, dict) and 'message' in error_data:
                        error_msg = f"Failed to submit task: {error_data['message']}"
                    else:
                        error_msg = f"Failed to submit task: {e.response.text[:500]}"
                except (ValueError, json.JSONDecodeError):
                    error_msg = f"Failed to submit task: {e.response.text[:500]}"
            raise TaskSubmissionError(error_msg)
        except requests.exceptions.RequestException as e:
            raise TaskSubmissionError(f"Failed to submit task: {e}")
        
        # Parse SSE stream - but don't wait too long, poll if needed
        task_id = task_id_from_headers  # Start with task_id from headers if available
        task_status = None
        results = None
        
        # Debug: Check if we got task_id from headers
        # if task_id_from_headers:
        #     print(f"DEBUG: Got task_id from headers: {task_id_from_headers}")
        
        try:
            # Try to read from SSE stream - get task_id quickly, then poll for results
            # The server sends results in the SSE stream when task completes, but polling is more reliable
            # So we use SSE to get task_id quickly, then break and poll
            stream_timeout = 5.0  # Wait up to 5 seconds for task_id in SSE stream, then break and poll
            start_time = time.time()
            lines_read = 0
            sse_events_received = []  # Track what we receive for debugging
            first_event_received = False
            
            try:
                # Use iter_lines with default chunk_size (not 1, as that can be very slow)
                # The key is to break quickly when we get task_id or timeout
                for line in response.iter_lines(decode_unicode=False):
                    lines_read += 1
                    elapsed = time.time() - start_time
                    
                    # If we have results from SSE stream, break immediately - we're done!
                    if results:
                        break
                    
                    # If we've been waiting too long, break and fall back to polling
                    if elapsed > stream_timeout:
                        # Timeout waiting for results in SSE - fall back to polling
                        break
                    
                    # Track if we've received any events (to detect if stream is completely dead)
                    if line and line.strip():
                        first_event_received = True
                    
                    if not line:
                        continue
                    
                    # Track non-empty lines for debugging
                    if line.strip():
                        sse_events_received.append(line[:200])  # Store first 200 chars
                    
                    # SSE format: "data: {...json...}"
                    if line.startswith(b"data: "):
                        try:
                            json_str = line[6:].decode('utf-8')
                            data = json.loads(json_str)
                            # SSE events use "type" or "event_type" - check both
                            event_type = data.get("type") or data.get("event_type", "")
                            event_data = data.get("data", {})
                            
                            # Check for "results" event - server sends this when task completes with results
                            # The server sends: {"event_type": "results", "data": {...results_json...}}
                            # The results_json might be the actual results dict, or it might be wrapped
                            if event_type == "results":
                                # Server sent results in SSE stream - use them directly!
                                # event_data contains the results JSON from the server
                                # It might be the actual results dict, or it might need unwrapping
                                if isinstance(event_data, dict):
                                    # Check if event_data has artifacts directly (unwrapped format)
                                    artifacts = event_data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        # We have complete results from SSE - use them!
                                        results = event_data
                                        if "task_id" in event_data and not task_id:
                                            task_id = event_data["task_id"]
                                        break
                                    # Check if event_data is wrapped (e.g., {"data": {...}})
                                    if "data" in event_data and isinstance(event_data["data"], dict):
                                        nested_data = event_data["data"]
                                        artifacts = nested_data.get("artifacts", {})
                                        if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                            results = nested_data
                                            if "task_id" in nested_data and not task_id:
                                                task_id = nested_data["task_id"]
                                            break
                                # Also check if results are at top level of data
                                if isinstance(data, dict) and "artifacts" in data:
                                    artifacts = data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = data
                                        if "task_id" in data and not task_id:
                                            task_id = data["task_id"]
                                        break
                            
                            # Also check for artifacts in any event (fallback - in case event_type is wrong)
                            if isinstance(event_data, dict) and "artifacts" in event_data and not results:
                                artifacts = event_data.get("artifacts", {})
                                if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                    status = event_data.get("status") or event_data.get("state")
                                    if status == "COMPLETED":
                                        results = event_data
                                        if "task_id" in event_data and not task_id:
                                            task_id = event_data["task_id"]
                                        break
                            
                            # Check for "complete" event - task is done, might have results
                            if event_type == "complete":
                                if isinstance(event_data, dict):
                                    status = event_data.get("status") or event_data.get("state")
                                    if status == "COMPLETED":
                                        # Check if we have artifacts in the complete event
                                        artifacts = event_data.get("artifacts", {})
                                        if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                            results = event_data
                                            if "task_id" in event_data and not task_id:
                                                task_id = event_data["task_id"]
                                            break
                                        # If no artifacts, break and poll (polling is more reliable)
                                        if "task_id" in event_data and not task_id:
                                            task_id = event_data["task_id"]
                                        if task_id:
                                            break
                            
                            # Check if task_id is at top level - extract it
                            if "task_id" in data and not task_id:
                                task_id = data["task_id"]
                            
                            # Also check if task_id is in event_data (status JSON from server)
                            # The server includes task_id in the status JSON
                            if isinstance(event_data, dict) and "task_id" in event_data and not task_id:
                                task_id = event_data["task_id"]
                            
                            # If we have task_id and waited a bit, break and poll (polling is more reliable)
                            if task_id and elapsed > 1.0:
                                break
                            
                            # Recursively search for task_id in the data structure (fallback)
                            if not task_id:
                                def find_task_id(obj, depth=0, max_depth=2):
                                    if depth > max_depth:
                                        return None
                                    if isinstance(obj, dict):
                                        if "task_id" in obj:
                                            return obj["task_id"]
                                        # Check event_data first (most likely location)
                                        for key, value in obj.items():
                                            result = find_task_id(value, depth + 1, max_depth)
                                            if result:
                                                return result
                                    elif isinstance(obj, list):
                                        for item in obj:
                                            result = find_task_id(item, depth + 1, max_depth)
                                            if result:
                                                return result
                                    return None
                                
                                # Search event_data first (where status JSON is)
                                if isinstance(event_data, dict):
                                    found_task_id = find_task_id(event_data, max_depth=2)
                                    if found_task_id:
                                        task_id = found_task_id
                                
                                # Fallback: search entire data structure
                                if not task_id:
                                    found_task_id = find_task_id(data, max_depth=2)
                                    if found_task_id:
                                        task_id = found_task_id
                            
                            # If we have task_id and waited a bit, break and poll (polling is more reliable)
                            if task_id and elapsed > 1.0:
                                break
                            
                            # If we have results, break - we're done!
                            if results:
                                break
                            
                            # Handle "task_id" event - server sends this first with the task_id
                            if event_type == "task_id":
                                if "task_id" in event_data and not task_id:
                                    task_id = event_data["task_id"]
                                    # Break immediately - we have task_id, now poll for results
                                    break
                                elif "task_id" in data and not task_id:
                                    task_id = data["task_id"]
                                    # Break immediately - we have task_id, now poll for results
                                    break
                            
                            if event_type == "status" or event_type == "task_status":
                                task_status = event_data.get("state") or event_data.get("status")
                                # task_id should be in event_data (the status JSON from server)
                                # The server code includes task_id in status JSON
                                if isinstance(event_data, dict):
                                    # Check for task_id in event_data first (most common location)
                                    if "task_id" in event_data and not task_id:
                                        task_id = event_data["task_id"]
                                    # Also check nested structures
                                    if "data" in event_data and isinstance(event_data["data"], dict):
                                        if "task_id" in event_data["data"] and not task_id:
                                            task_id = event_data["data"]["task_id"]
                                # Fallback: check top-level data
                                if "task_id" in data and not task_id:
                                    task_id = data["task_id"]
                                
                                # If we have task_id and waited a bit, break and poll (polling is more reliable)
                                if task_id and elapsed > 1.0:
                                    break
                                
                                # Check if status is COMPLETED and we have artifacts - use them!
                                if task_status == "COMPLETED" and isinstance(event_data, dict):
                                    artifacts = event_data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = event_data
                                        break
                                
                                # If we have results, break - we're done!
                                if results:
                                    break
                            
                            elif event_type == "complete" or event_type == "task_complete":
                                task_status = event_data.get("state") or event_data.get("status")
                                if "task_id" in event_data and not task_id:
                                    task_id = event_data["task_id"]
                                elif "task_id" in data and not task_id:
                                    task_id = data["task_id"]
                                
                                # Complete event might contain results directly
                                if isinstance(event_data, dict) and "artifacts" in event_data:
                                    artifacts = event_data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = event_data
                                        break
                                elif isinstance(data, dict) and "artifacts" in data:
                                    artifacts = data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = data
                                        break
                                
                                # If task is complete but no results yet, break and poll (polling is more reliable)
                                if task_id:
                                    break
                            
                            elif event_type == "results":
                                # Server sent results in SSE stream - use them directly!
                                if isinstance(event_data, dict):
                                    artifacts = event_data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = event_data
                                        if "task_id" in event_data and not task_id:
                                            task_id = event_data["task_id"]
                                        break
                                # Also check if results are at top level
                                if isinstance(data, dict) and "artifacts" in data:
                                    artifacts = data.get("artifacts", {})
                                    if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                        results = data
                                        if "task_id" in data and not task_id:
                                            task_id = data["task_id"]
                                        break
                                # Fallback: use event_data even if artifacts check fails
                                if not results and isinstance(event_data, dict):
                                    results = event_data
                                    if "task_id" in event_data and not task_id:
                                        task_id = event_data["task_id"]
                                    break
                            
                            elif event_type == "error":
                                error_msg = event_data.get("error", "Unknown error")
                                raise TaskExecutionError(f"Task execution error: {error_msg}")
                        
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
            except Exception as stream_error:
                # If stream reading fails, log but continue to polling
                # This handles cases where stream hangs or errors
                if not task_id:
                    # If we don't have task_id, we can't poll - this is a problem
                    # But let's try to continue anyway in case task_id was set
                    pass
            finally:
                # Always close the response to free up resources IMMEDIATELY
                # This is critical to prevent hanging
                try:
                    response.close()
                except:
                    pass
                # Also close the underlying connection
                try:
                    if hasattr(response.raw, 'close'):
                        response.raw.close()
                except:
                    pass
            
            # If we didn't get results from SSE stream, poll for them using task_id
            # This handles cases where the stream closes before results are sent
            if not results:
                if task_id:
                    # Poll immediately - don't wait, as results might already be available
                    # The polling function will handle retries if results aren't ready yet
                    try:
                        results = self._poll_for_results(task_id)
                    except TaskExecutionError as e:
                        # If polling fails, try to get status to see if task completed
                        # Sometimes results endpoint fails but status works
                        try:
                            status_response = self.session.get(
                                f"{self.base_url}/api/status/{task_id}",
                                timeout=10,
                            )
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status_info = status_data.get("data", {})
                                if status_info.get("status") == "COMPLETED":
                                    # Task completed but results endpoint failed
                                    # Wait a bit longer and try results one more time
                                    time.sleep(1.0)
                                    try:
                                        results = self._poll_for_results(task_id)
                                    except:
                                        # If still failing, raise original error with more context
                                        raise TaskExecutionError(
                                            f"Task {task_id} completed but results endpoint returned 500 error. "
                                            f"This may be a temporary server issue. Original error: {e}"
                                        )
                                else:
                                    raise e
                            else:
                                raise e
                        except Exception as fallback_error:
                            # If status check also fails, raise original error
                            raise TaskExecutionError(
                                f"Failed to get results for task {task_id}. "
                                f"Results endpoint error: {e}. "
                                f"Status check error: {fallback_error}"
                            )
                else:
                    # If we don't have task_id, we can't poll
                    # This is a critical error - the server should provide task_id
                    # Check if we received any events at all
                    if not first_event_received and lines_read == 0:
                        # No events received - the stream might not have started
                        # But the task might have been submitted - try using /api/submit to get task_id
                        # Actually, we can't do that since we already submitted via /api/submit-and-wait
                        raise TaskExecutionError(
                            f"No SSE events received from server after {stream_timeout} seconds. "
                            "The task may not have been submitted, or the server is not sending SSE events. "
                            f"Please check server logs and ensure the Corebrum server is running at {self.base_url}. "
                            "If the task was submitted (check server logs for task_id), you may need to rebuild the server "
                            "with the latest SSE changes to include task_id in events."
                        )
                    
                    # If we received events but no task_id, the server might not be sending it
                    # This is a critical issue - we need task_id to poll for results
                    error_msg = (
                        f"No task_id received from stream after {stream_timeout} seconds. "
                        f"Received {lines_read} lines from stream. "
                        "The task was likely submitted (check server logs for task_id), but the server did not provide "
                        "a task_id in the SSE stream. This prevents the client from polling for results. "
                        "Please rebuild the Corebrum server with the latest changes to include task_id in SSE events, "
                        "or check server logs to manually retrieve the task_id."
                    )
                    
                    # Try one more time to extract task_id from any events we received
                    if sse_events_received:
                        # Try to parse the events we received to find task_id
                        for event_line in sse_events_received:
                            try:
                                if event_line.startswith(b"data: "):
                                    json_str = event_line[6:].decode('utf-8')
                                    event_data = json.loads(json_str)
                                    # Recursively search for task_id
                                    def find_task_id(obj):
                                        if isinstance(obj, dict):
                                            if "task_id" in obj:
                                                return obj["task_id"]
                                            for v in obj.values():
                                                result = find_task_id(v)
                                                if result:
                                                    return result
                                        elif isinstance(obj, list):
                                            for item in obj:
                                                result = find_task_id(item)
                                                if result:
                                                    return result
                                        return None
                                    found_id = find_task_id(event_data)
                                    if found_id:
                                        task_id = found_id
                                        break
                            except:
                                continue
                    
                    if not task_id:
                        raise TaskExecutionError(error_msg)
                    # Try to get task_id from response body if available
                    if hasattr(response, 'text') and response.text:
                        try:
                            # Try to parse response body for any clues
                            response_data = response.json()
                            if isinstance(response_data, dict):
                                if 'task_id' in response_data:
                                    task_id = response_data['task_id']
                                    # Retry polling with this task_id
                                    time.sleep(0.5)
                                    try:
                                        results = self._poll_for_results(task_id)
                                        if results:
                                            # Success! Continue with results
                                            pass
                                        else:
                                            raise TaskExecutionError(error_msg)
                                    except Exception as poll_error:
                                        raise TaskExecutionError(
                                            f"{error_msg} Found task_id in response but polling failed: {poll_error}"
                                        )
                                elif 'error' in response_data:
                                    error_msg = f"{error_msg} Server error: {response_data.get('error')}"
                        except (ValueError, json.JSONDecodeError):
                            pass
                    raise TaskExecutionError(error_msg)
            
            if not results:
                raise TaskExecutionError("Task completed but no results were returned")
            
            # Extract result from artifacts
            return self._extract_result(results)
        
        except TaskExecutionError:
            raise
        except Exception as e:
            raise TaskExecutionError(f"Failed to get task results: {e}")
    
    def _poll_for_results(self, task_id: str) -> Dict[str, Any]:
        """Poll for task results."""
        # Use shorter timeout and fewer attempts for faster failure
        max_attempts = min(self.max_poll_attempts, 150)  # Cap at 150 attempts (5 minutes max)
        poll_interval = self.poll_interval
        
        # Debug logging can be enabled via environment variable or removed for production
        debug_enabled = os.environ.get("COREBRUM_DEBUG", "false").lower() == "true"
        
        if debug_enabled:
            print(f"DEBUG: Starting to poll for results (task {task_id[:8]}...)")
        
        for attempt in range(max_attempts):
            try:
                if debug_enabled and attempt < 5:
                    print(f"DEBUG: Poll attempt {attempt + 1} for task {task_id[:8]}... - making HTTP request")
                
                try:
                    # Use a longer timeout - the server may need time to query Zenoh
                    # and the response might be large
                    response = self.session.get(
                        f"{self.base_url}/api/results/{task_id}",
                        timeout=(5, 60),  # (connect: 5s, read: 60s) - longer read timeout for server processing
                    )
                    if debug_enabled and attempt < 5:
                        print(f"DEBUG: HTTP request completed - status {response.status_code}")
                except Exception as req_error:
                    if debug_enabled:
                        print(f"DEBUG: HTTP request failed: {req_error}")
                    raise
                
                # DEBUG: Always log status code for first few attempts
                if debug_enabled and attempt < 5:
                    print(f"DEBUG: Poll attempt {attempt + 1} for task {task_id[:8]}... - HTTP {response.status_code}")
                
                if response.status_code == 200:
                    if debug_enabled and attempt < 5:
                        print(f"DEBUG: Got 200 response, parsing JSON...")
                    try:
                        data = response.json()
                        if debug_enabled and attempt < 5:
                            print(f"DEBUG: JSON parsed successfully, data type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                    except Exception as json_error:
                        if debug_enabled:
                            print(f"DEBUG: JSON parse failed: {json_error}, response text: {response.text[:200]}")
                        raise
                    
                    # DEBUG: Log what we received (only first few attempts to avoid spam)
                    if debug_enabled and attempt < 3:
                        import json
                        print(f"DEBUG: Received response for task {task_id[:8]}... (attempt {attempt + 1}):")
                        print(f"  Status: {response.status_code}")
                        print(f"  Data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                        if isinstance(data, dict) and "data" in data:
                            print(f"  Data['data'] keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'not a dict'}")
                            if isinstance(data['data'], dict):
                                print(f"  Data['data'] has artifacts: {'artifacts' in data['data']}")
                                print(f"  Data['data'] status: {data['data'].get('status')}")
                                artifacts = data['data'].get('artifacts', {})
                                print(f"  Data['data'] artifacts: {artifacts}")
                                print(f"  Artifacts is dict: {isinstance(artifacts, dict)}")
                                print(f"  Artifacts length: {len(artifacts) if isinstance(artifacts, dict) else 'N/A'}")
                    
                    # The server returns ResultsResponse: {"success": true, "data": {...results...}}
                    # The results JSON has: {"artifacts": {...}, "status": "COMPLETED", ...}
                    
                    # First check if it's wrapped in ResultsResponse format: {"success": true, "data": {...}}
                    if isinstance(data, dict) and data.get("success") and "data" in data:
                        result_data = data["data"]
                        if isinstance(result_data, dict):
                            status = result_data.get("status") or result_data.get("state")
                            
                            if debug_enabled and attempt < 3:
                                print(f"DEBUG: Checking wrapped format - status: {status}")
                                print(f"DEBUG: result_data keys: {list(result_data.keys())}")
                            
                            # Only return if status is COMPLETED
                            if status == "COMPLETED":
                                # Check if artifacts exist and are non-empty
                                artifacts = result_data.get("artifacts", {})
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Status is COMPLETED, checking artifacts: {artifacts}")
                                    print(f"DEBUG: artifacts type: {type(artifacts)}")
                                    print(f"DEBUG: artifacts check: {artifacts and isinstance(artifacts, dict) and len(artifacts) > 0}")
                                
                                if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                    # Task completed with results - return immediately
                                    if debug_enabled:
                                        print(f"DEBUG: ✅ Returning result_data with artifacts and COMPLETED status (attempt {attempt + 1})")
                                    # Always print success message (not just in debug mode) to help diagnose
                                    print(f"✅ Task {task_id[:8]}... completed with results (attempt {attempt + 1})")
                                    return result_data
                                # Task completed but no artifacts yet - might be a race condition, continue polling
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Task COMPLETED but artifacts empty, continuing to poll...")
                                # Sleep before next poll attempt (but not on first attempt)
                                if attempt > 0:
                                    time.sleep(self.poll_interval)
                                continue
                            
                            # If status is RUNNING or PENDING, continue polling
                            if status in ["RUNNING", "PENDING"]:
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Task status is {status}, continuing to poll...")
                                # Sleep before next poll attempt (but not on first attempt)
                                if attempt > 0:
                                    time.sleep(self.poll_interval)
                                continue
                            
                            # If we get here and status is not COMPLETED/RUNNING/PENDING, log it
                            if debug_enabled and attempt < 3:
                                print(f"DEBUG: ⚠️  Unexpected status: {status}, continuing to poll...")
                            # Sleep before next poll attempt (but not on first attempt)
                            if attempt > 0:
                                time.sleep(self.poll_interval)
                            continue
                    
                    # Check if data has artifacts directly (unwrapped format)
                    # This handles cases where the API returns results directly without wrapping
                    if isinstance(data, dict) and "artifacts" in data:
                        status = data.get("status") or data.get("state")
                        
                        # Only return if status is COMPLETED
                        if status == "COMPLETED":
                            # Check if artifacts exist and are non-empty
                            artifacts = data.get("artifacts", {})
                            if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                # Task completed with results - return immediately
                                print(f"✅ Task {task_id[:8]}... completed with results (attempt {attempt + 1}, unwrapped format)")
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Returning unwrapped data with artifacts and COMPLETED status")
                                return data
                            # Task completed but no artifacts yet - continue polling
                            if debug_enabled and attempt < 3:
                                print(f"DEBUG: Task COMPLETED but artifacts empty, continuing to poll...")
                        
                        # If status is RUNNING or PENDING, continue polling
                        if status in ["RUNNING", "PENDING"]:
                            if debug_enabled and attempt < 3:
                                print(f"DEBUG: Task status is {status}, continuing to poll...")
                            # Sleep before next poll attempt (but not on first attempt)
                            if attempt > 0:
                                time.sleep(self.poll_interval)
                            continue
                    
                    # Check nested data structure (fallback - handles {"data": {...}} without "success")
                    if isinstance(data, dict) and "data" in data:
                        nested_data = data["data"]
                        if isinstance(nested_data, dict):
                            status = nested_data.get("status") or nested_data.get("state")
                            
                            # Only return if status is COMPLETED
                            if status == "COMPLETED":
                                # Check if artifacts exist and are non-empty
                                artifacts = nested_data.get("artifacts", {})
                                if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                    if debug_enabled and attempt < 3:
                                        print(f"DEBUG: Returning nested_data with artifacts and COMPLETED status")
                                    return nested_data
                                # Task completed but no artifacts yet - continue polling
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Task COMPLETED but artifacts empty, continuing to poll...")
                            
                            # If status is RUNNING or PENDING, continue polling
                            if status in ["RUNNING", "PENDING"]:
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Task status is {status}, continuing to poll...")
                                # Sleep before next poll attempt (but not on first attempt)
                                if attempt > 0:
                                    time.sleep(self.poll_interval)
                                continue
                    
                    # If status is completed, return the data anyway (but check artifacts)
                    if isinstance(data, dict):
                        status = data.get("status") or data.get("state")
                        if status == "COMPLETED":
                            artifacts = data.get("artifacts", {})
                            if artifacts and isinstance(artifacts, dict) and len(artifacts) > 0:
                                if debug_enabled and attempt < 3:
                                    print(f"DEBUG: Returning data with COMPLETED status at top level")
                                return data
                            # COMPLETED but no artifacts - continue polling
                            if debug_enabled and attempt < 3:
                                print(f"DEBUG: Task COMPLETED but artifacts empty, continuing to poll...")
                            # Sleep before next poll attempt (but not on first attempt)
                            if attempt > 0:
                                time.sleep(self.poll_interval)
                            continue
                    
                    # If we get here, we have data but didn't recognize it as complete
                    # Continue polling - don't return incomplete data
                    if debug_enabled and attempt < 3:
                        print(f"DEBUG: Got 200 response but task not complete, continuing to poll...")
                    # Sleep before next poll attempt (but not on first attempt)
                    if attempt > 0:
                        time.sleep(self.poll_interval)
                    continue
                
                elif response.status_code == 404:
                    # Task not ready yet - but check if we've been polling for a while
                    # If we've polled many times and still getting 404, check status endpoint
                    # to see if task actually completed (server might have results but API endpoint broken)
                    if debug_enabled and attempt < 5:
                        print(f"DEBUG: Got 404 for task {task_id[:8]}... (attempt {attempt + 1})")
                    if attempt > 5:  # After 5 attempts (~5 seconds), check status
                        try:
                            status_response = self.session.get(
                                f"{self.base_url}/api/status/{task_id}",
                                timeout=5,
                            )
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status_info = status_data.get("data", status_data)
                                if isinstance(status_info, dict):
                                    status = status_info.get("status") or status_info.get("state")
                                    if status == "COMPLETED":
                                        # Task is completed but results endpoint returns 404
                                        # Wait a bit longer and try again - server might need time to make results available via HTTP
                                        if attempt < 20:  # Try up to 20 more times
                                            if debug_enabled and attempt < 10:
                                                print(f"DEBUG: Task completed but results endpoint returned 404, waiting longer... (attempt {attempt + 1})")
                                            time.sleep(self.poll_interval * 2)  # Wait longer
                                            continue
                                        else:
                                            # After many attempts, give up
                                            raise TaskExecutionError(
                                                f"Task {task_id} completed on Corebrum (status: COMPLETED), "
                                                "but the results endpoint returned 404 after many attempts. "
                                                "This may be a server-side issue with the results endpoint."
                                            )
                        except requests.exceptions.RequestException:
                            pass  # Ignore errors when checking status
                    
                    # Task not ready yet - sleep before next attempt (but not before first attempt)
                    if attempt > 0:
                        time.sleep(self.poll_interval)
                    continue
                
                elif response.status_code == 500:
                    # Server error - might be temporary, wait and retry
                    # But don't retry forever - give up after a few attempts
                    if attempt < 5:  # Retry 500 errors up to 5 times (increased from 3)
                        # Wait longer for 500 errors, with exponential backoff
                        wait_time = self.poll_interval * (1 + attempt * 0.5)
                        time.sleep(wait_time)
                        continue
                    else:
                        # After 5 retries, try to get status instead to see if task completed
                        try:
                            status_response = self.session.get(
                                f"{self.base_url}/api/status/{task_id}",
                                timeout=5,
                            )
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status_info = status_data.get("data", {})
                                if status_info.get("status") == "COMPLETED" or status_info.get("state") == "COMPLETED":
                                    # Task completed but results endpoint is broken
                                    # The task completed successfully, but we can't get results
                                    # This is a server-side issue - raise a helpful error
                                    raise TaskExecutionError(
                                        f"Task {task_id} completed successfully on Corebrum, but the results endpoint "
                                        f"returned 500 error after {attempt + 1} attempts. "
                                        f"This is a server-side issue. The task result is available on the server "
                                        f"but cannot be retrieved via the API. Please check server logs."
                                    )
                                elif status_info.get("status") == "FAILED" or status_info.get("state") == "FAILED":
                                    error_msg = status_info.get("error", "Task failed")
                                    raise TaskExecutionError(f"Task {task_id} failed: {error_msg}")
                        except TaskExecutionError:
                            raise  # Re-raise our custom errors
                        except Exception as status_error:
                            # If status check also fails, raise original 500 error
                            pass
                        raise TaskExecutionError(
                            f"Server error (500) when fetching results for task {task_id} after {attempt + 1} attempts. "
                            f"The task may have completed but the results endpoint is unavailable. "
                            f"Please check server logs for task {task_id}."
                        )
                
                else:
                    response.raise_for_status()
            
            except requests.exceptions.RequestException as e:
                # On last attempt, raise the error
                if attempt == self.max_poll_attempts - 1:
                    raise TaskExecutionError(f"Failed to get results for task {task_id}: {e}")
                time.sleep(self.poll_interval)
                continue
        
        raise TaskTimeoutError(
            f"Task {task_id} did not complete within timeout "
            f"({self.max_poll_attempts * self.poll_interval} seconds)"
        )
    
    def _extract_result(self, results: Dict[str, Any]) -> Any:
        """Extract result from Corebrum results structure."""
        # Check for artifacts
        artifacts = results.get("artifacts", {})
        
        # Look for result.json
        if "result.json" in artifacts:
            result_str = artifacts["result.json"]
            if isinstance(result_str, str):
                try:
                    parsed = json.loads(result_str)
                    # If result is a dict with "error" key, it's an error message
                    if isinstance(parsed, dict) and "error" in parsed:
                        # This is an error from the wrapper code
                        error_msg = parsed.get("error", "Unknown error")
                        error_type = parsed.get("error_type", "Exception")
                        traceback_str = parsed.get("traceback", "")
                        # Include error type and traceback in the exception message
                        full_error = f"{error_type}: {error_msg}"
                        if traceback_str:
                            full_error += f"\n{traceback_str}"
                        raise TaskExecutionError(full_error)
                    # If result is a dict with "result" key, unwrap it (common wrapper pattern)
                    if isinstance(parsed, dict):
                        # If it's a single-key dict with "result", unwrap it
                        if "result" in parsed and len(parsed) == 1:
                            return parsed["result"]
                        # If it's a dict with "result" and other keys, prefer "result"
                        if "result" in parsed:
                            return parsed["result"]
                    return parsed
                except json.JSONDecodeError:
                    # If it's not valid JSON, try to parse as number
                    try:
                        if result_str.isdigit() or (result_str.startswith('-') and result_str[1:].isdigit()):
                            return int(result_str)
                        if '.' in result_str:
                            return float(result_str)
                    except:
                        pass
                    return result_str
            return result_str
        
        # Look for any JSON artifact
        for key, value in artifacts.items():
            if key.endswith('.json'):
                if isinstance(value, str):
                    try:
                        parsed = json.loads(value)
                        # Unwrap if it's a single-key dict with "result"
                        if isinstance(parsed, dict) and "result" in parsed and len(parsed) == 1:
                            return parsed["result"]
                        return parsed
                    except json.JSONDecodeError:
                        continue
                return value
        
        # Return entire results dict if no specific artifact found
        return results

