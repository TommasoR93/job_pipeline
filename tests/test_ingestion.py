from src.ingestion import create_session, rate_limit, make_request
from unittest.mock import MagicMock, patch
from requests.adapters import HTTPAdapter

def test_create_session():
    session = create_session()
    adapter = session.get_adapter("https://")
    assert isinstance(adapter, HTTPAdapter)

@patch("time.time")
def test_rate_limit(mock_time):
    mock_time.return_value = 10
    result = rate_limit(last_request_time=5, time_interval=6)
    assert result == 10

@patch("src.ingestion.rate_limit")
def test_make_request(mock_rate_limit):
    session = MagicMock()
    fake_response = MagicMock()
    session.get.return_value = fake_response
    mock_rate_limit.return_value = 10
    url = "http://example.com"
    params = {"q" : "test"}

    response, last_request_time = make_request(session, url, 0, params)

    assert response == fake_response
    assert last_request_time == 10
