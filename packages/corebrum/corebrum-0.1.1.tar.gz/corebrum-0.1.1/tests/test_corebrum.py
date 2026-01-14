"""
Tests for Corebrum Python library.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from corebrum import Corebrum, configure, run, execute
from corebrum.exceptions import (
    CorebrumError,
    TaskSubmissionError,
    TaskExecutionError,
    TaskTimeoutError,
)


class TestCorebrumClient:
    """Test Corebrum client class."""
    
    def test_init_default(self):
        """Test default initialization."""
        client = Corebrum()
        assert client.base_url == "http://localhost:6502"
        assert client.identity_id is None
        assert client.timeout == 300
    
    def test_init_custom(self):
        """Test custom initialization."""
        client = Corebrum(
            base_url="http://example.com:8080",
            identity_id="test-id",
            timeout=600,
        )
        assert client.base_url == "http://example.com:8080"
        assert client.identity_id == "test-id"
        assert client.timeout == 600
    
    def test_detect_dependencies(self):
        """Test dependency detection."""
        client = Corebrum()
        
        code = """
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import json
"""
        deps = client._detect_dependencies(code)
        assert "pandas" in deps
        assert "numpy" in deps
        assert "sklearn" in deps
        assert "os" not in deps  # stdlib
        assert "json" not in deps  # stdlib
    
    def test_is_json_serializable(self):
        """Test JSON serialization check."""
        client = Corebrum()
        
        assert client._is_json_serializable(1) is True
        assert client._is_json_serializable("string") is True
        assert client._is_json_serializable([1, 2, 3]) is True
        assert client._is_json_serializable({"key": "value"}) is True
        assert client._is_json_serializable(lambda x: x) is False
    
    def test_extract_inputs(self):
        """Test input extraction."""
        client = Corebrum()
        
        def test_func(a, b=10, c=None):
            return a + b
        
        inputs = client._extract_inputs(test_func, (5,), {"c": 20})
        assert inputs["a"] == 5
        assert inputs["b"] == 10
        assert inputs["c"] == 20
    
    def test_create_task_definition(self):
        """Test task definition creation."""
        client = Corebrum()
        
        task_def = client._create_task_definition(
            name="test_task",
            code="print('hello')",
            inputs={"x": 1},
            dependencies=["pandas"],
            timeout=60,
        )
        
        assert task_def["name"] == "test_task"
        assert task_def["version"] == "1.0.0"
        assert task_def["compute_logic"]["language"] == "python"
        assert task_def["compute_logic"]["code"] == "print('hello')"
        assert "pandas" in task_def["dependencies"]
    
    @patch('corebrum.client.requests.Session')
    def test_submit_and_wait_success(self, mock_session_class):
        """Test successful task submission and wait."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"event_type": "status", "data": {"state": "RUNNING", "task_id": "test-123"}}',
            b'data: {"event_type": "complete", "data": {"state": "COMPLETED", "task_id": "test-123"}}',
            b'data: {"event_type": "results", "data": {"artifacts": {"result.json": "{\\"result\\": 42}"}}}',
        ]
        mock_response.raise_for_status = Mock()
        
        # Mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Corebrum()
        client.session = mock_session
        
        task_def = {
            "name": "test",
            "compute_logic": {"language": "python", "code": "print(42)"},
        }
        
        result = client._submit_and_wait(task_def, {"x": 1})
        assert result == {"result": 42}
    
    @patch('corebrum.client.requests.Session')
    def test_submit_and_wait_error(self, mock_session_class):
        """Test task submission error."""
        # Mock response with error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        # Mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Corebrum()
        client.session = mock_session
        
        task_def = {
            "name": "test",
            "compute_logic": {"language": "python", "code": "print(42)"},
        }
        
        with pytest.raises(TaskSubmissionError):
            client._submit_and_wait(task_def, {})
    
    @patch('corebrum.client.requests.Session')
    def test_poll_for_results(self, mock_session_class):
        """Test polling for results."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"artifacts": {"result.json": '{"result": 42}'}},
        }
        
        # Mock session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Corebrum()
        client.session = mock_session
        
        results = client._poll_for_results("test-123")
        assert "artifacts" in results


class TestDecorator:
    """Test @run decorator."""
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_run_decorator(self, mock_submit):
        """Test @run decorator."""
        mock_submit.return_value = {"result": 42}
        
        client = Corebrum()
        
        @client.run()
        def test_func(x, y):
            return x + y
        
        result = test_func(1, 2)
        assert result == {"result": 42}
        assert mock_submit.called
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_run_decorator_with_kwargs(self, mock_submit):
        """Test @run decorator with kwargs."""
        mock_submit.return_value = {"result": 42}
        
        client = Corebrum(identity_id="test-id")
        
        @client.run(timeout=600)
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == {"result": 42}


class TestExecute:
    """Test execute() method."""
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_execute(self, mock_submit):
        """Test execute() method."""
        mock_submit.return_value = {"result": 42}
        
        client = Corebrum()
        result = client.execute("print(42)")
        
        assert result == {"result": 42}
        assert mock_submit.called
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_execute_with_inputs(self, mock_submit):
        """Test execute() with input data."""
        mock_submit.return_value = {"result": 10}
        
        client = Corebrum()
        result = client.execute(
            "result = x + y",
            input_data={"x": 3, "y": 7}
        )
        
        assert result == {"result": 10}


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_global_run(self, mock_submit):
        """Test global run() function."""
        mock_submit.return_value = {"result": 42}
        
        from corebrum import run
        
        @run()
        def test_func():
            return 42
        
        result = test_func()
        assert result == {"result": 42}
    
    @patch('corebrum.client.Corebrum._submit_and_wait')
    def test_global_execute(self, mock_submit):
        """Test global execute() function."""
        mock_submit.return_value = {"result": 42}
        
        from corebrum import execute
        
        result = execute("print(42)")
        assert result == {"result": 42}
    
    def test_configure(self):
        """Test configure() function."""
        from corebrum import configure
        
        configure(base_url="http://example.com", identity_id="test-id")
        
        from corebrum import _get_default
        client = _get_default()
        
        assert client.base_url == "http://example.com"
        assert client.identity_id == "test-id"


class TestExceptions:
    """Test exception classes."""
    
    def test_corebrum_error(self):
        """Test CorebrumError."""
        error = CorebrumError("test error")
        assert str(error) == "test error"
        assert isinstance(error, Exception)
    
    def test_task_submission_error(self):
        """Test TaskSubmissionError."""
        error = TaskSubmissionError("submission failed")
        assert str(error) == "submission failed"
        assert isinstance(error, CorebrumError)
    
    def test_task_execution_error(self):
        """Test TaskExecutionError."""
        error = TaskExecutionError("execution failed")
        assert str(error) == "execution failed"
        assert isinstance(error, CorebrumError)
    
    def test_task_timeout_error(self):
        """Test TaskTimeoutError."""
        error = TaskTimeoutError("timeout")
        assert str(error) == "timeout"
        assert isinstance(error, CorebrumError)
