"""Moadian API Client"""

import base64
import datetime
import json
import time
import uuid
from typing import Any, Dict, List, Optional

import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding

from .crypto import InvoiceEncryptor, load_server_key
from .exceptions import APIException, AuthenticationException, MoadianException
from .invoice import (
    SerialNumberManager,
    build_invoice_dict,
    generate_tax_id,
)
from .models import InvoiceData, InvoiceResponse, ServerInfo
from .utils import load_key_and_cert


class JWSGenerator:
    """JWS Token Generator for Moadian API Authentication"""

    def __init__(self, private_key, certificate):
        """
        Initialize JWS generator.

        Args:
            private_key: RSA private key (cryptography object)
            certificate: X.509 certificate (cryptography object)
        """
        self.private_key = private_key
        self.certificate = certificate

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Base64URL encode without padding"""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    def _get_certificate_base64(self) -> str:
        """Get base64-encoded certificate for x5c header"""
        cert_bytes = self.certificate.public_bytes(Encoding.DER)
        return base64.b64encode(cert_bytes).decode("utf-8")

    @staticmethod
    def _get_signature_time() -> str:
        """Get current UTC time in ISO 8601 format"""
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def generate(self, payload: Dict[str, Any]) -> str:
        """
        Generate JWS token.

        Args:
            payload: Dictionary containing nonce and clientId

        Returns:
            Complete JWS token string
        """
        # Build header
        header = {
            "alg": "RS256",
            "x5c": [self._get_certificate_base64()],
            "sigT": self._get_signature_time(),
            "crit": ["sigT"],
        }

        # Encode header and payload
        header_json = json.dumps(header, separators=(",", ":"))
        payload_json = json.dumps(payload, separators=(",", ":"))

        header_b64 = self._base64url_encode(header_json.encode("utf-8"))
        payload_b64 = self._base64url_encode(payload_json.encode("utf-8"))

        # Create signing input
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

        # Sign with RS256
        signature = self.private_key.sign(
            signing_input, padding.PKCS1v15(), hashes.SHA256()
        )

        # Encode signature
        signature_b64 = self._base64url_encode(signature)

        # Construct JWS token
        return f"{header_b64}.{payload_b64}.{signature_b64}"


class MoadianClient:
    """
    Complete Moadian Tax API Client.

    Implements all API endpoints according to the technical specification.
    """

    BASE_URL = "https://tp.tax.gov.ir/requestsmanager/api/v2"

    def __init__(
        self,
        client_id: str,
        certs_dir: str = "certs",
        private_key_file: str = "private_key.pem",
        certificate_file: str = "certificate.pem",
        password: Optional[bytes] = None,
        enable_serial_storage: bool = False,
        serial_file: str = "last_serial.txt",
    ):
        """
        Initialize Moadian client.

        Args:
            client_id: Fiscal ID (شناسه حافظه مالیاتی) or trusted company ID
            certs_dir: Directory containing certificate files (default: "certs")
            private_key_file: Private key filename (default: "private_key.pem")
            certificate_file: Certificate filename (default: "certificate.pem")
            password: Optional password for encrypted private key
            enable_serial_storage: If True, save serial numbers to file (default: False)
            serial_file: Path to serial file (default: "last_serial.txt")
        """
        self.client_id = client_id

        # Load private key and certificate
        self.private_key, self.certificate = load_key_and_cert(
            certs_dir=certs_dir,
            private_key_file=private_key_file,
            certificate_file=certificate_file,
            password=password,
        )

        # Initialize JWS generator
        self.jws_generator = JWSGenerator(self.private_key, self.certificate)

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "*/*", "Content-Type": "application/json"}
        )

        # Serial number manager
        self.serial_manager = SerialNumberManager(
            serial_file=serial_file,
            enable_file_storage=enable_serial_storage
        )

        # Rate limiting
        self._last_submission_time = None

    def _get_nonce(self, time_to_live: int = 30) -> str:
        """
        Get random nonce for authentication.

        Args:
            time_to_live: Nonce validity in seconds (10-200)

        Returns:
            Nonce string
        """
        url = f"{self.BASE_URL}/nonce"
        params = {"timeToLive": time_to_live}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["nonce"]
        except requests.exceptions.RequestException as e:
            raise MoadianException(f"Failed to get nonce: {e}") from e

    def _get_auth_token(self) -> str:
        """
        Generate authentication token (JWT).

        Returns:
            Bearer token string
        """
        nonce = self._get_nonce()
        payload = {"nonce": nonce, "clientId": self.client_id}
        return self.jws_generator.generate(payload)

    def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Any] = None,
    ) -> Any:
        """
        Make authenticated API request.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response JSON data
        """
        url = f"{self.BASE_URL}/{endpoint}"
        token = self._get_auth_token()

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationException(
                    f"Authentication failed: {e.response.text}"
                ) from e
            raise APIException(f"API error: {e.response.text}") from e
        except requests.exceptions.RequestException as e:
            raise MoadianException(f"Request failed: {e}") from e

    # =========================================================================
    # API Methods
    # =========================================================================

    def get_server_information(self) -> ServerInfo:
        """
        Get server information including timestamp and public keys.

        Returns:
            ServerInfo object
        """
        data = self._make_authenticated_request("GET", "server-information")
        return ServerInfo(
            server_time=data["serverTime"], public_keys=data["publicKeys"]
        )

    def get_fiscal_information(self, memory_id: str) -> Dict[str, Any]:
        """
        Get fiscal memory information.

        Args:
            memory_id: Fiscal memory ID (شناسه حافظه)

        Returns:
            Dictionary with fiscal information
        """
        params = {"memoryId": memory_id}
        return self._make_authenticated_request(
            "GET", "fiscal-information", params=params
        )

    def get_taxpayer_information(self, economic_code: str) -> Dict[str, Any]:
        """
        Get taxpayer information.

        Args:
            economic_code: Economic code (کد اقتصادی)

        Returns:
            Dictionary with taxpayer information
        """
        params = {"economicCode": economic_code}
        return self._make_authenticated_request(
            "GET", "taxpayer", params=params
        )

    def send_invoice(
        self,
        invoice_data: InvoiceData,
        force_serial: Optional[int] = None,
        min_delay: float = 15.0,
    ) -> InvoiceResponse:
        """
        Send invoice to Moadian system (simplified high-level method).

        This method handles:
        - Tax ID generation
        - Invoice building
        - Encryption
        - Submission
        - Serial number management

        Args:
            invoice_data: InvoiceData object containing invoice details
            force_serial: Optional serial number to use (for testing)
            min_delay: Minimum delay between submissions in seconds

        Returns:
            InvoiceResponse object with uid and reference_number.
            Use inquiry_by_uid() to check invoice status later.

        Raises:
            MoadianException: If submission fails
        """
        # Get serial number
        if force_serial is not None:
            serial = force_serial
            self.serial_manager.save_serial(serial)
        else:
            serial = self.serial_manager.get_next_serial()
            self.serial_manager.save_serial(serial)

        # Generate timestamp
        timestamp = int(datetime.datetime.now().timestamp() * 1000)

        # Generate Tax ID
        tax_id = generate_tax_id(self.client_id, timestamp, serial)
        invoice_number = tax_id[11:21]

        # Build invoice dictionary
        invoice_dict = build_invoice_dict(
            tax_id=tax_id,
            invoice_number=invoice_number,
            timestamp=timestamp,
            invoice_data=invoice_data,
        )

        # Get server information and encryption key
        server_info = self.get_server_information()
        if not server_info.public_keys:
            raise MoadianException("No server public keys available")

        server_key_info = server_info.public_keys[0]
        server_public_key = load_server_key(server_key_info["key"])
        server_key_id = server_key_info["id"]

        # Encrypt invoice
        encryptor = InvoiceEncryptor(
            private_key=self.private_key,
            certificate=self.certificate,
            server_public_key=server_public_key,
            server_key_id=server_key_id,
        )

        encrypted_payload = encryptor.prepare_invoice_for_submission(
            invoice_dict
        )

        # Prepare packet
        request_trace_id = str(uuid.uuid4())
        invoice_packet = {
            "header": {
                "requestTraceId": request_trace_id,
                "fiscalId": self.client_id,
            },
            "payload": encrypted_payload,
        }

        # Rate limiting
        if self._last_submission_time is not None:
            elapsed = time.time() - self._last_submission_time
            if elapsed < min_delay:
                wait_time = min_delay - elapsed
                time.sleep(wait_time)
        self._last_submission_time = time.time()

        # Submit
        result = self.send_invoices([invoice_packet], tax_id=tax_id, serial=serial)

        if result and len(result) > 0:
            return result[0]
        else:
            raise MoadianException("No response from API")

    def send_invoices(
        self, invoices: List[Dict[str, Any]], tax_id: Optional[str] = None, serial: Optional[int] = None
    ) -> List[InvoiceResponse]:
        """
        Send invoices to Moadian system (low-level method).

        Args:
            invoices: List of invoice packets, each containing:
                - header: Dict with requestTraceId and fiscalId
                - payload: JWE encrypted invoice string
            tax_id: Optional Tax ID to include in response
            serial: Optional serial number to include in response

        Returns:
            List of InvoiceResponse objects
        """
        data = self._make_authenticated_request(
            "POST", "invoice", json_data=invoices
        )

        return [
            InvoiceResponse(
                uid=item["uid"],
                reference_number=item["referenceNumber"],
                tax_id=tax_id or "",
                serial=serial or 0,
                packet_type=item.get("packetType"),
                data=item.get("data"),
            )
            for item in data["result"]
        ]

    def inquiry_by_reference_id(
        self,
        reference_ids: List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Inquiry invoice status by reference numbers.

        Args:
            reference_ids: List of reference numbers
            start: Start datetime (ISO 8601 format)
            end: End datetime (ISO 8601 format)

        Returns:
            List of invoice status information
        """
        params = {"referenceIds": reference_ids}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        return self._make_authenticated_request(
            "GET", "inquiry-by-reference-id", params=params
        )

    def inquiry_by_uid(
        self,
        uid_list: List[str],
        fiscal_id: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Inquiry invoice status by UIDs.

        Args:
            uid_list: List of UIDs (requestTraceId)
            fiscal_id: Fiscal ID (defaults to client_id)
            start: Start datetime (ISO 8601 format)
            end: End datetime (ISO 8601 format)

        Returns:
            List of invoice status information
        """
        params = {"uidList": uid_list, "fiscalId": fiscal_id or self.client_id}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        return self._make_authenticated_request(
            "GET", "inquiry-by-uid", params=params
        )

    def inquiry_by_time_range(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Inquiry invoices by time range.

        Args:
            start: Start datetime (ISO 8601 format)
            end: End datetime (ISO 8601 format)
            page_number: Page number (default: 1)
            page_size: Page size (1-100, default: 10)
            status: Filter by status (SUCCESS, FAILED, TIMEOUT, IN_PROGRESS)

        Returns:
            List of invoice information
        """
        params = {"pageNumber": page_number, "pageSize": page_size}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if status:
            params["status"] = status

        return self._make_authenticated_request("GET", "inquiry", params=params)

    def inquiry_invoice_status(
        self, tax_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Inquiry invoice status in portfolio.

        Args:
            tax_ids: List of tax IDs (شماره مالیاتی)

        Returns:
            List of invoice status information
        """
        params = {"taxIds": tax_ids}
        return self._make_authenticated_request(
            "GET", "inquiry-invoice-status", params=params
        )

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
