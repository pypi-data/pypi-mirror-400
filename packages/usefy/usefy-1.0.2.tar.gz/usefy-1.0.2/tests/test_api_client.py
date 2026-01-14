"""
Tests for API client
"""

import pytest
from unittest.mock import Mock, patch
from usageguard.api_client import UsageGuardAPIClient


def test_client_initialization():
    """Test client initialization"""
    client = UsageGuardAPIClient(
        api_key="test_key",
        base_url="https://api.test.com",
        timeout_ms=100,
    )
    
    assert client.api_key == "test_key"
    assert client.base_url == "https://api.test.com"
    assert client.timeout == 0.1


@patch('usageguard.api_client.requests.Session')
def test_check_success(mock_session_class):
    """Test successful pre-flight check"""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "decision": "allow",
        "estimated_cost": 0.05,
        "confidence": 0.65,
        "remaining_budget": 45.30,
    }
    
    mock_session = Mock()
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    decision = client.check(
        provider="openai",
        request={"endpoint": "/v1/chat/completions", "method": "POST", "metadata": {}},
        scope_context={"project_id": "proj_123"},
    )
    
    assert decision.decision == "allow"
    assert decision.estimated_cost == 0.05
    assert decision.confidence == 0.65
    assert decision.remaining_budget == 45.30


@patch('usageguard.api_client.requests.Session')
def test_check_block(mock_session_class):
    """Test blocked request"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "decision": "block",
        "reason": "Budget exceeded",
        "estimated_cost": 0.05,
        "remaining_budget": 0.0,
    }
    
    mock_session = Mock()
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    decision = client.check(
        provider="openai",
        request={"endpoint": "/v1/chat/completions", "method": "POST", "metadata": {}},
        scope_context={"project_id": "proj_123"},
    )
    
    assert decision.decision == "block"
    assert decision.reason == "Budget exceeded"


@patch('usageguard.api_client.requests.Session')
def test_check_timeout_fail_open(mock_session_class):
    """Test fail-open behavior on timeout"""
    import requests
    
    mock_session = Mock()
    mock_session.post.side_effect = requests.Timeout()
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    decision = client.check(
        provider="openai",
        request={"endpoint": "/v1/chat/completions", "method": "POST", "metadata": {}},
        scope_context={"project_id": "proj_123"},
    )
    
    # Should fail-open (allow)
    assert decision.decision == "allow"
    assert decision.metadata["fail_open"] is True
    assert "timeout" in decision.metadata["reason"]


@patch('usageguard.api_client.requests.Session')
def test_check_api_error_fail_open(mock_session_class):
    """Test fail-open behavior on API error"""
    mock_response = Mock()
    mock_response.status_code = 500
    
    mock_session = Mock()
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    decision = client.check(
        provider="openai",
        request={"endpoint": "/v1/chat/completions", "method": "POST", "metadata": {}},
        scope_context={"project_id": "proj_123"},
    )
    
    # Should fail-open (allow)
    assert decision.decision == "allow"
    assert decision.metadata["fail_open"] is True


@patch('usageguard.api_client.requests.Session')
def test_track_success(mock_session_class):
    """Test successful post-flight tracking"""
    mock_response = Mock()
    mock_response.status_code = 200
    
    mock_session = Mock()
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    result = client.track(
        provider="openai",
        response={"status_code": 200, "actual_cost": 0.048, "metadata": {}},
        scope_context={"project_id": "proj_123"},
        request_id="req_123",
        idempotency_key="idem_123",
        estimated_cost=0.05,
    )
    
    assert result is True


@patch('usageguard.api_client.requests.Session')
def test_track_failure_silent(mock_session_class):
    """Test that tracking failures are silent (fire-and-forget)"""
    mock_session = Mock()
    mock_session.post.side_effect = Exception("Network error")
    mock_session_class.return_value = mock_session
    
    client = UsageGuardAPIClient(api_key="test_key")
    
    # Should not raise exception
    result = client.track(
        provider="openai",
        response={"status_code": 200, "actual_cost": 0.048, "metadata": {}},
        scope_context={"project_id": "proj_123"},
        request_id="req_123",
        idempotency_key="idem_123",
    )
    
    assert result is False
