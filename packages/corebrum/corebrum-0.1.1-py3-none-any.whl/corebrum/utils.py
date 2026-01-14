"""
Utility functions for Corebrum Python library.
"""

import json
import inspect
from typing import Any, Dict, Optional


def serialize_inputs(obj: Any) -> Any:
    """
    Recursively serialize an object to JSON-compatible types.
    
    Args:
        obj: Object to serialize
    
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {k: serialize_inputs(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_inputs(item) for item in obj]
    elif isinstance(obj, set):
        return [serialize_inputs(item) for item in obj]
    else:
        # Try JSON serialization
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Fallback to string representation
            return str(obj)


def get_function_source(func) -> Optional[str]:
    """
    Get source code of a function.
    
    Args:
        func: Function object
    
    Returns:
        Source code string or None if unavailable
    """
    try:
        return inspect.getsource(func)
    except (OSError, TypeError):
        return None


def validate_task_definition(task_def: Dict[str, Any]) -> bool:
    """
    Validate a task definition structure.
    
    Args:
        task_def: Task definition dictionary
    
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ["name", "version", "compute_logic"]
    
    for field in required_fields:
        if field not in task_def:
            raise ValueError(f"Task definition missing required field: {field}")
    
    compute_logic = task_def["compute_logic"]
    if not isinstance(compute_logic, dict):
        raise ValueError("compute_logic must be a dictionary")
    
    if "language" not in compute_logic:
        raise ValueError("compute_logic missing required field: language")
    
    return True
