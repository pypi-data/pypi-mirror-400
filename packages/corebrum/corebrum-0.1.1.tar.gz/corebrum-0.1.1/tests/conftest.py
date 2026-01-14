"""
Pytest configuration and fixtures.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_corebrum_response():
    """Mock successful Corebrum API response."""
    response = Mock()
    response.status_code = 200
    response.iter_lines.return_value = [
        b'data: {"event_type": "status", "data": {"state": "RUNNING", "task_id": "test-123"}}',
        b'data: {"event_type": "complete", "data": {"state": "COMPLETED", "task_id": "test-123"}}',
        b'data: {"event_type": "results", "data": {"artifacts": {"result.json": "{\\"result\\": 42}"}}}',
    ]
    response.raise_for_status = Mock()
    return response


@pytest.fixture
def mock_corebrum_client(mock_corebrum_response):
    """Mock Corebrum client with successful response."""
    with patch('corebrum.client.requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session.post.return_value = mock_corebrum_response
        mock_session.get.return_value = mock_corebrum_response
        mock_session_class.return_value = mock_session
        yield mock_session

