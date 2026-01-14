"""
Corebrum Python Library - Execute Python code transparently on Corebrum compute mesh.

This library allows you to run Python functions and code on Corebrum's distributed
compute infrastructure with minimal code changes.

Example:
    >>> import corebrum
    >>> 
    >>> @corebrum.run()
    >>> def process_data(data):
    >>>     import pandas as pd
    >>>     return pd.DataFrame(data).describe().to_dict()
    >>> 
    >>> result = process_data([{"x": 1}, {"x": 2}])
"""

__version__ = "0.1.1"
__author__ = "Corebrum"
__email__ = "hello@corebrum.com"

from .client import Corebrum
from .exceptions import CorebrumError, TaskSubmissionError, TaskExecutionError, TaskTimeoutError

__all__ = [
    'Corebrum',
    'configure',
    'run',
    'execute',
    'CorebrumError',
    'TaskSubmissionError',
    'TaskExecutionError',
    'TaskTimeoutError',
]

# Global default instance
_default_corebrum = None

def _get_default():
    """Get or create default Corebrum instance."""
    global _default_corebrum
    if _default_corebrum is None:
        _default_corebrum = Corebrum()
    return _default_corebrum

# Convenience functions using default instance
def run(func=None, **kwargs):
    """Global decorator using default Corebrum instance."""
    return _get_default().run(func, **kwargs)

def execute(code: str, input_data=None, **kwargs):
    """Global execute function using default Corebrum instance."""
    return _get_default().execute(code, input_data, **kwargs)

def configure(base_url=None, identity_id=None, timeout=None):
    """Configure global Corebrum instance."""
    global _default_corebrum
    # Only pass parameters that are explicitly provided
    kwargs = {}
    if base_url is not None:
        kwargs['base_url'] = base_url
    if identity_id is not None:
        kwargs['identity_id'] = identity_id
    if timeout is not None:
        kwargs['timeout'] = timeout
    _default_corebrum = Corebrum(**kwargs)
