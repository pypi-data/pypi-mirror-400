import time
from unittest.mock import MagicMock, patch

import pytest

import pretix_esncard.api as api
from pretix_esncard.api import CACHE_TTL, ExternalAPIError, fetch_card

VALID_CARD = {
    "code": "7F5DLWMYVE9",
    "tid": "2774279",
    "expiration-date": "2026-06-05",
    "status": "active",
    "section-code": "SE-LUND-ESN",
    "activation date": "2025-06-05",
}


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure cache is empty before each test."""
    api._cache.clear()
    yield
    api._cache.clear()


# ---------------------------
# Successful fetch
# ---------------------------


def test_fetch_card_success():
    fake_response = {"valid": True, "name": "Alice"}

    with patch.object(api.session, "get") as mock_get:
        mock = MagicMock()
        mock.json.return_value = fake_response
        mock.raise_for_status.return_value = None
        mock_get.return_value = mock

        result = fetch_card("123")

    assert result == fake_response
    assert "123" in api._cache


# ---------------------------
# Cache hit (within TTL)
# ---------------------------


def test_fetch_card_cache_hit():
    fake_data = {"valid": True}
    now = time.time()
    api._cache["123"] = (now, fake_data)

    with patch.object(api.session, "get") as mock_get:
        result = fetch_card("123")

    mock_get.assert_not_called()
    assert result == fake_data


# ---------------------------
# Cache expired → new request
# ---------------------------


def test_fetch_card_cache_expired():
    fake_old_data = {"valid": False}
    fake_new_data = {"valid": True}

    old_ts = time.time() - (CACHE_TTL + 1)
    api._cache["123"] = (old_ts, fake_old_data)

    with patch.object(api.session, "get") as mock_get:
        mock = MagicMock()
        mock.json.return_value = fake_new_data
        mock.raise_for_status.return_value = None
        mock_get.return_value = mock

        result = fetch_card("123")

    mock_get.assert_called_once()
    assert result == fake_new_data
    assert api._cache["123"][1] == fake_new_data


# ---------------------------
# API returns a list of length 1
# ---------------------------


def test_fetch_card_list_single_item():
    fake_list = [{"valid": True}]

    with patch.object(api.session, "get") as mock_get:
        mock = MagicMock()
        mock.json.return_value = fake_list
        mock.raise_for_status.return_value = None
        mock_get.return_value = mock

        result = fetch_card("123")

    assert result == fake_list[0]


# ---------------------------
# API returns a list of length > 1 → error
# ---------------------------


def test_fetch_card_list_multiple_items():
    fake_list = [{"a": 1}, {"b": 2}]

    with patch.object(api.session, "get") as mock_get:
        mock = MagicMock()
        mock.json.return_value = fake_list
        mock.raise_for_status.return_value = None
        mock_get.return_value = mock

        with pytest.raises(ExternalAPIError):
            fetch_card("123")


# ---------------------------
# API returns unexpected type
# ---------------------------


def test_fetch_card_unexpected_type():
    with patch.object(api.session, "get") as mock_get:
        mock = MagicMock()
        mock.json.return_value = "not a dict"
        mock.raise_for_status.return_value = None
        mock_get.return_value = mock

        with pytest.raises(ExternalAPIError):
            fetch_card("123")


# ---------------------------
# Network error → ExternalAPIError
# ---------------------------


def test_fetch_card_network_error():
    with patch.object(api.session, "get", side_effect=Exception("boom")):
        with pytest.raises(ExternalAPIError):
            fetch_card("123")
