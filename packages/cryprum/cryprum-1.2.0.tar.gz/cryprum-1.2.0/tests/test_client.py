import time

import pytest
from unittest.mock import patch, MagicMock

from cryprum import Client
from cryprum.exceptions import CryprumError


@pytest.fixture
def mock_httpx():
    """Mock httpx.Client for all tests."""
    with patch("httpx.Client") as mock:
        yield mock


@pytest.fixture
def client(mock_httpx):
    """Create a Client instance with mocked HTTP."""
    c = Client(token="test-token")
    # Bypass JWT auto-refresh by setting last_call to now and providing mock jwt
    c._last_call = int(time.time())
    c._jwt = {"token": "mock-jwt-token"}
    return c


def make_response(json_data, status_code=200):
    """Helper to create mock response."""
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.headers = {"content-type": "application/json"}
    resp.status_code = status_code
    return resp


class TestAuth:
    def test_auth_jwt(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"success": True, "token": "jwt-token-123"}
        )

        result = client.auth_jwt_v1_post("access-key", ttl=3600)

        assert result["success"] is True
        assert result["token"] == "jwt-token-123"


class TestBalances:
    def test_tron_balances(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"TRX": 1000000, "USDT": 500000}
        )

        result = client.balances("tron", "TTestAddress123")

        assert result["TRX"] == 1000000
        assert result["USDT"] == 500000

    def test_ethereum_balances(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"ETH": "1000000000000000000", "USDT": 500000}
        )

        result = client.balances("ethereum", "0xTestAddress123")

        assert result["ETH"] == "1000000000000000000"

    def test_bsc_balances(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"BNB": "2000000000000000000", "USDT": 1000000}
        )

        result = client.balances("bsc", "0xTestAddress123")

        assert result["BNB"] == "2000000000000000000"


class TestTransaction:
    def test_transaction_creates_operation(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"id": "550e8400-e29b-41d4-a716-446655440000", "status": "pending"}
        )

        result = client.transaction(
            "ethereum",
            amount=1.0,
            currency="ETH",
            private_key="0xprivate",
            to_address="0xrecipient",
        )

        assert "id" in result
        assert result["status"] == "pending"

    def test_transaction_error(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"detail": "Insufficient balance"}
        )

        with pytest.raises(CryprumError):
            client.transaction(
                "ethereum",
                amount=1000.0,
                currency="ETH",
                private_key="0xprivate",
                to_address="0xrecipient",
            )


class TestTransactionInfo:
    def test_transaction_info(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {
                "block_number": 12345678,
                "txid": "0xtxhash123",
                "from_address": "0xfrom",
                "to_address": "0xto",
                "value": 1000000000000000000,
                "confirmations": 100,
            }
        )

        result = client.transaction_info("ethereum", "0xtxhash123")

        assert result["block_number"] == 12345678
        assert result["confirmations"] == 100


class TestOperationStatus:
    def test_operation_status_operating(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "operating",
                "external_id": None,
            }
        )

        result = client.operation_status("550e8400-e29b-41d4-a716-446655440000")

        assert result["status"] == "operating"
        assert result["external_id"] is None

    def test_operation_status_completed(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "external_id": "0xtxhash456",
            }
        )

        result = client.operation_status("550e8400-e29b-41d4-a716-446655440000")

        assert result["status"] == "completed"
        assert result["external_id"] == "0xtxhash456"

    def test_operation_not_found(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"detail": "Operation not found"}
        )

        with pytest.raises(CryprumError):
            client.operation_status("nonexistent-id")


class TestSubscribe:
    def test_subscribe(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {
                "new_count": 2,
                "add_count": 2,
                "upd_count": 0,
                "all_count": 5,
                "status": "ok",
            }
        )

        result = client.subscribe("ethereum", ["0xaddr1", "0xaddr2"])

        assert result["new_count"] == 2
        assert result["status"] == "ok"


class TestErrorHandling:
    def test_string_error_response(self, client, mock_httpx):
        resp = MagicMock()
        resp.json.return_value = "Internal server error"
        resp.headers = {"content-type": "application/json"}
        mock_httpx.return_value.request.return_value = resp

        with pytest.raises(CryprumError):
            client.balances("ethereum", "0xaddr")

    def test_detail_error_response(self, client, mock_httpx):
        mock_httpx.return_value.request.return_value = make_response(
            {"detail": "Unauthorized"}
        )

        with pytest.raises(CryprumError):
            client.balances("ethereum", "0xaddr")
