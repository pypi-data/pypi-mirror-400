"""Cryptography module for JWS signing and JWE encryption"""

import base64
import datetime
import json
import os
from typing import Any, Dict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .exceptions import CertificateException


def load_server_key(key_base64: str):
    """
    Load server's public key from base64 string.

    Args:
        key_base64: Base64-encoded public key

    Returns:
        RSA public key object

    Raises:
        CertificateException: If key cannot be loaded
    """
    try:
        key_bytes = base64.b64decode(key_base64)
        return load_der_public_key(key_bytes, backend=default_backend())
    except Exception as e:
        raise CertificateException(
            f"Failed to load server public key: {e}"
        ) from e


class InvoiceEncryptor:
    """
    Encrypts and signs invoices for Moadian system.

    Process:
    1. Sign invoice with JWS (RS256)
    2. Encrypt signed invoice with JWE (RSA-OAEP-256 + AES256-GCM)
    """

    def __init__(
        self, private_key, certificate, server_public_key, server_key_id
    ):
        """
        Initialize encryptor.

        Args:
            private_key: Your RSA private key for signing
            certificate: Your X.509 certificate
            server_public_key: Server's RSA public key for encryption
            server_key_id: Server's public key ID
        """
        self.private_key = private_key
        self.certificate = certificate
        self.server_public_key = server_public_key
        self.server_key_id = server_key_id

    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Base64URL encode without padding"""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """Base64URL decode with padding"""
        padding_needed = 4 - (len(data) % 4)
        if padding_needed != 4:
            data += "=" * padding_needed
        return base64.urlsafe_b64decode(data)

    def _get_certificate_base64(self) -> str:
        """Get base64-encoded certificate (DER format)"""
        cert_bytes = self.certificate.public_bytes(serialization.Encoding.DER)
        return base64.b64encode(cert_bytes).decode("utf-8")

    @staticmethod
    def _get_signature_time() -> str:
        """Get current UTC time for signature"""
        return datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def sign_invoice(self, invoice_dict: Dict[str, Any]) -> str:
        """
        Sign invoice with JWS (RS256).

        Args:
            invoice_dict: Invoice data as dictionary

        Returns:
            JWS compact serialization string
        """
        # Build JWS header
        header = {
            "alg": "RS256",
            "x5c": [self._get_certificate_base64()],
            "sigT": self._get_signature_time(),
            "crit": ["sigT"],
        }

        # Serialize to JSON without whitespace
        header_json = json.dumps(header, separators=(",", ":"))
        payload_json = json.dumps(
            invoice_dict, separators=(",", ":"), ensure_ascii=False
        )

        # Base64URL encode
        header_b64 = self._base64url_encode(header_json.encode("utf-8"))
        payload_b64 = self._base64url_encode(payload_json.encode("utf-8"))

        # Create signing input
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

        # Sign with RS256
        signature = self.private_key.sign(
            signing_input, padding.PKCS1v15(), hashes.SHA256()
        )

        signature_b64 = self._base64url_encode(signature)

        # Return JWS compact serialization
        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def encrypt_invoice(self, signed_invoice: str) -> str:
        """
        Encrypt signed invoice with JWE (RSA-OAEP-256 + AES256-GCM).

        Args:
            signed_invoice: JWS string from sign_invoice()

        Returns:
            JWE compact serialization string
        """
        # Build JWE header
        header = {
            "alg": "RSA-OAEP-256",
            "enc": "A256GCM",
            "kid": self.server_key_id,
        }

        header_json = json.dumps(header, separators=(",", ":"))
        header_b64 = self._base64url_encode(header_json.encode("utf-8"))

        # Generate AES key (256 bits = 32 bytes)
        aes_key = os.urandom(32)

        # Encrypt AES key with server's RSA public key (RSA-OAEP-256)
        encrypted_key = self.server_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        encrypted_key_b64 = self._base64url_encode(encrypted_key)

        # Generate IV for AES-GCM (96 bits = 12 bytes)
        iv = os.urandom(12)
        iv_b64 = self._base64url_encode(iv)

        # Additional Authenticated Data (AAD)
        aad = header_b64.encode("ascii")

        # Encrypt payload with AES-256-GCM
        aesgcm = AESGCM(aes_key)
        ciphertext_with_tag = aesgcm.encrypt(
            iv, signed_invoice.encode("utf-8"), aad
        )

        # Split ciphertext and authentication tag
        # AESGCM appends 16-byte tag at the end
        ciphertext = ciphertext_with_tag[:-16]
        auth_tag = ciphertext_with_tag[-16:]

        ciphertext_b64 = self._base64url_encode(ciphertext)
        auth_tag_b64 = self._base64url_encode(auth_tag)

        # Return JWE compact serialization
        return (
            f"{header_b64}."
            f"{encrypted_key_b64}."
            f"{iv_b64}."
            f"{ciphertext_b64}."
            f"{auth_tag_b64}"
        )

    def prepare_invoice_for_submission(
        self, invoice_dict: Dict[str, Any]
    ) -> str:
        """
        Complete process: sign then encrypt invoice.

        Args:
            invoice_dict: Invoice data dictionary

        Returns:
            JWE encrypted invoice ready for submission
        """
        # Step 1: Sign with JWS
        signed = self.sign_invoice(invoice_dict)

        # Step 2: Encrypt with JWE
        encrypted = self.encrypt_invoice(signed)

        return encrypted
