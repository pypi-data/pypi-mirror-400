import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from onecoder.tools.jules_tools import jules_status_tool

# Get the absolute path to the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the .env file
dotenv_path = os.path.join(script_dir, '..', '..', 'components', 'devcenter', '.env')

# Load environment variables from the .env file
from dotenv import load_dotenv
load_dotenv(dotenv_path)

@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get."""
    with patch('onecoder.jules_client.requests.get') as mock_get:
        yield mock_get

@patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
def test_jules_status_tool_success(mock_requests_get):
    """Test successful retrieval of Jules session status."""
    # Mock session response
    session_response = MagicMock()
    session_response.status_code = 200
    session_response.ok = True
    session_response.json.return_value = {
        "name": "sessions/12345",
        "id": "12345",
        "title": "Test Session",
        "state": "COMPLETED",
        "prompt": "Test prompt",
        "outputs": []
    }
    
    # Mock activities response
    activities_response = MagicMock()
    activities_response.status_code = 200
    activities_response.ok = True
    activities_response.json.return_value = {
        "activities": []
    }
    
    mock_requests_get.side_effect = [session_response, activities_response]

    session_id = "12345"
    result = jules_status_tool(session_id)

    assert "Session: 12345" in result
    assert "Title: Test Session" in result
    assert "Prompt: Test prompt" in result
    assert mock_requests_get.call_count == 2

@patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
def test_jules_status_tool_not_found(mock_requests_get):
    """Test handling of a 404 Not Found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.ok = False
    mock_requests_get.return_value = mock_response

    session_id = "nonexistent"
    result = jules_status_tool(session_id)

    assert "Jules session with ID 'nonexistent' not found." in result
    mock_requests_get.assert_called_once()

@patch.dict(os.environ, {"JULES_API_KEY": "test_key"})
def test_jules_status_tool_api_error(mock_requests_get):
    """Test handling of other API errors."""
    mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")
    
    session_id = "12345"
    result = jules_status_tool(session_id)

    assert "Error communicating with Jules API" in result
    mock_requests_get.assert_called_once()

def test_jules_status_tool_no_api_key():
    """Test that the function handles a missing API key gracefully."""
    with patch.dict(os.environ, {"JULES_API_KEY": ""}, clear=True):
        result = jules_status_tool("12345")
        assert "Error: JULES_API_KEY environment variable not set" in result