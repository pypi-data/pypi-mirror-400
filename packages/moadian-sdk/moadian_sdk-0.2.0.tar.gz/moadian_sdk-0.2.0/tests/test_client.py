"""Tests for MoadianClient with mocked HTTP requests"""

from unittest.mock import Mock, patch

import pytest

from moadian_sdk import InvoiceData, MoadianClient, create_invoice_item
from moadian_sdk.exceptions import (
    APIException,
    AuthenticationException,
    MoadianException,
)
from moadian_sdk.models import ServerInfo


class TestMoadianClientMocked:
    """Test MoadianClient with mocked HTTP requests"""

    @pytest.fixture
    def mock_certificates(self):
        """Mock certificate loading"""
        with patch("moadian_sdk.client.load_key_and_cert") as mock_load:
            # Create mock private key and certificate
            mock_private_key = Mock()
            mock_certificate = Mock()
            mock_certificate.public_bytes.return_value = b"mock_cert_bytes"

            mock_load.return_value = (mock_private_key, mock_certificate)
            yield mock_load

    @pytest.fixture
    def client(self, mock_certificates):
        """Create client instance with mocked certificates"""
        return MoadianClient(
            client_id="TESTID",
            enable_serial_storage=False,
        )

    def test_get_nonce_success(self, client):
        """Test getting nonce with mocked request"""
        mock_response = Mock()
        mock_response.json.return_value = {"nonce": "test-nonce-12345"}
        mock_response.raise_for_status = Mock()

        client.session.get = Mock(return_value=mock_response)

        nonce = client._get_nonce()

        assert nonce == "test-nonce-12345"
        client.session.get.assert_called_once()

    def test_get_nonce_failure(self, client):
        """Test nonce request failure"""
        import requests

        client.session.get = Mock(
            side_effect=requests.exceptions.RequestException("Connection error")
        )

        with pytest.raises(MoadianException, match="Failed to get nonce"):
            client._get_nonce()

    def test_get_auth_token(self, client):
        """Test authentication token generation"""
        # Mock nonce request
        mock_response = Mock()
        mock_response.json.return_value = {"nonce": "test-nonce"}
        mock_response.raise_for_status = Mock()
        client.session.get = Mock(return_value=mock_response)

        # Mock JWS generation
        client.jws_generator.generate = Mock(return_value="mock.jws.token")

        token = client._get_auth_token()

        assert token == "mock.jws.token"
        client.jws_generator.generate.assert_called_once()

    def test_get_server_information(self, client):
        """Test get_server_information with mocked request"""
        mock_response_data = {
            "serverTime": 1704067200000,
            "publicKeys": [
                {
                    "id": "key-1",
                    "key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                }
            ],
        }

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        server_info = client.get_server_information()

        assert isinstance(server_info, ServerInfo)
        assert server_info.server_time == 1704067200000
        assert len(server_info.public_keys) == 1
        assert server_info.public_keys[0]["id"] == "key-1"

    def test_get_fiscal_information(self, client):
        """Test get_fiscal_information with mocked request"""
        mock_response_data = {"memoryId": "TESTID", "status": "active"}

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.get_fiscal_information("TESTID")

        assert result["memoryId"] == "TESTID"
        client._make_authenticated_request.assert_called_once()

    def test_get_taxpayer_information(self, client):
        """Test get_taxpayer_information with mocked request"""
        mock_response_data = {
            "economicCode": "1234567890",
            "name": "Test Company",
        }

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.get_taxpayer_information("1234567890")

        assert result["economicCode"] == "1234567890"
        client._make_authenticated_request.assert_called_once()

    def test_send_invoice_mocked(self, client):
        """Test send_invoice with all requests mocked"""
        # Mock server information
        mock_server_info = ServerInfo(
            server_time=1704067200000,
            public_keys=[
                {
                    "id": "key-1",
                    "key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
                }
            ],
        )
        client.get_server_information = Mock(return_value=mock_server_info)

        # Mock server public key loading
        mock_server_key = Mock()
        with patch(
            "moadian_sdk.client.load_server_key", return_value=mock_server_key
        ):
            # Mock invoice encryption
            mock_encryptor = Mock()
            mock_encryptor.prepare_invoice_for_submission.return_value = (
                "encrypted.payload"
            )
            with patch(
                "moadian_sdk.client.InvoiceEncryptor",
                return_value=mock_encryptor,
            ):
                # Mock send_invoices response
                mock_invoice_response = Mock()
                mock_invoice_response.uid = "test-uid-123"
                mock_invoice_response.reference_number = "REF-123"
                mock_invoice_response.tax_id = "TESTID0000100000000001"
                mock_invoice_response.serial = 1

                client.send_invoices = Mock(
                    return_value=[mock_invoice_response]
                )

                # Create invoice data
                invoice_data = InvoiceData(
                    seller_tin="1234567890",
                    buyer_tin="0987654321",
                    items=[create_invoice_item("123", "Test", 1, 10000)],
                )

                # Send invoice
                response = client.send_invoice(invoice_data)

                assert response.uid == "test-uid-123"
                assert response.reference_number == "REF-123"
                assert response.tax_id == "TESTID0000100000000001"
                assert response.serial == 1

    def test_send_invoices_mocked(self, client):
        """Test send_invoices with mocked request"""
        mock_response_data = {
            "result": [
                {
                    "uid": "test-uid-1",
                    "referenceNumber": "REF-1",
                    "packetType": "INVOICE",
                    "data": None,
                }
            ]
        }

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        invoices = [
            {
                "header": {
                    "requestTraceId": "test-uid-1",
                    "fiscalId": "TESTID",
                },
                "payload": "encrypted.payload",
            }
        ]

        result = client.send_invoices(
            invoices, tax_id="TESTID0000100000000001", serial=1
        )

        assert len(result) == 1
        assert result[0].uid == "test-uid-1"
        assert result[0].reference_number == "REF-1"
        assert result[0].tax_id == "TESTID0000100000000001"
        assert result[0].serial == 1

    def test_inquiry_by_uid(self, client):
        """Test inquiry_by_uid with mocked request"""
        mock_response_data = [
            {"uid": "test-uid-1", "status": "SUCCESS", "data": {}}
        ]

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.inquiry_by_uid(["test-uid-1"])

        assert len(result) == 1
        assert result[0]["status"] == "SUCCESS"
        client._make_authenticated_request.assert_called_once()

    def test_inquiry_by_reference_id(self, client):
        """Test inquiry_by_reference_id with mocked request"""
        mock_response_data = [{"referenceNumber": "REF-1", "status": "SUCCESS"}]

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.inquiry_by_reference_id(["REF-1"])

        assert len(result) == 1
        assert result[0]["status"] == "SUCCESS"

    def test_inquiry_by_time_range(self, client):
        """Test inquiry_by_time_range with mocked request"""
        mock_response_data = [
            {"uid": "uid-1", "status": "SUCCESS"},
            {"uid": "uid-2", "status": "SUCCESS"},
        ]

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.inquiry_by_time_range(
            start="2024-01-01T00:00:00Z", end="2024-01-31T23:59:59Z"
        )

        assert len(result) == 2

    def test_inquiry_invoice_status(self, client):
        """Test inquiry_invoice_status with mocked request"""
        mock_response_data = [
            {"taxId": "TESTID0000100000000001", "status": "SUCCESS"}
        ]

        client._make_authenticated_request = Mock(
            return_value=mock_response_data
        )

        result = client.inquiry_invoice_status(["TESTID0000100000000001"])

        assert len(result) == 1
        assert result[0]["taxId"] == "TESTID0000100000000001"

    def test_authentication_error(self, client):
        """Test handling of authentication errors"""
        import requests

        # Mock nonce request (success)
        mock_nonce_response = Mock()
        mock_nonce_response.json.return_value = {"nonce": "test-nonce"}
        mock_nonce_response.raise_for_status = Mock()
        client.session.get = Mock(return_value=mock_nonce_response)

        # Mock JWS generation
        client.jws_generator.generate = Mock(return_value="mock.token")

        # Mock authenticated request (401 error)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        http_error = requests.exceptions.HTTPError(response=mock_response)
        client.session.request = Mock(side_effect=http_error)

        with pytest.raises(AuthenticationException):
            client._make_authenticated_request("GET", "test-endpoint")

    def test_api_error(self, client):
        """Test handling of API errors"""
        import requests

        # Mock nonce request (success)
        mock_nonce_response = Mock()
        mock_nonce_response.json.return_value = {"nonce": "test-nonce"}
        mock_nonce_response.raise_for_status = Mock()
        client.session.get = Mock(return_value=mock_nonce_response)

        # Mock JWS generation
        client.jws_generator.generate = Mock(return_value="mock.token")

        # Mock authenticated request (500 error)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        http_error = requests.exceptions.HTTPError(response=mock_response)
        client.session.request = Mock(side_effect=http_error)

        with pytest.raises(APIException):
            client._make_authenticated_request("GET", "test-endpoint")

    def test_request_exception(self, client):
        """Test handling of request exceptions"""
        import requests

        # Mock nonce request (success)
        mock_nonce_response = Mock()
        mock_nonce_response.json.return_value = {"nonce": "test-nonce"}
        mock_nonce_response.raise_for_status = Mock()
        client.session.get = Mock(return_value=mock_nonce_response)

        # Mock JWS generation
        client.jws_generator.generate = Mock(return_value="mock.token")

        # Mock authenticated request (network error)
        client.session.request = Mock(
            side_effect=requests.exceptions.RequestException("Network error")
        )

        with pytest.raises(MoadianException, match="Request failed"):
            client._make_authenticated_request("GET", "test-endpoint")

    def test_close_session(self, client):
        """Test closing the session"""
        client.session.close = Mock()

        client.close()

        client.session.close.assert_called_once()

    def test_context_manager(self, client):
        """Test context manager usage"""
        client.close = Mock()

        with client:
            pass

        client.close.assert_called_once()
