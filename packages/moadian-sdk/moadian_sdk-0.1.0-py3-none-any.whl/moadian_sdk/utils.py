"""Utility functions for certificate loading"""

import os
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate

from .exceptions import CertificateException


def load_key_and_cert(
    certs_dir: str = "certs",
    private_key_file: str = "private_key.pem",
    certificate_file: str = "certificate.pem",
    password: Optional[bytes] = None,
) -> Tuple[object, object]:
    """
    Load and parse private key and certificate from files.

    Args:
        certs_dir: Directory containing certificate files (default: "certs")
        private_key_file: Private key filename (default: "private_key.pem")
        certificate_file: Certificate filename (default: "certificate.pem")
        password: Optional password for encrypted private key

    Returns:
        Tuple of (private_key_object, certificate_object)

    Raises:
        CertificateException: If files cannot be found or are invalid
    """
    private_key_path = os.path.join(certs_dir, private_key_file)
    certificate_path = os.path.join(certs_dir, certificate_file)

    # Check if files exist
    if not os.path.exists(private_key_path):
        raise CertificateException(
            f"Private key file not found: {private_key_path}"
        )

    if not os.path.exists(certificate_path):
        raise CertificateException(
            f"Certificate file not found: {certificate_path}"
        )

    # Read and parse files
    try:
        with open(private_key_path, "rb") as f:
            private_key_data = f.read()

        with open(certificate_path, "rb") as f:
            certificate_data = f.read()

        # Parse into cryptography objects
        private_key = load_pem_private_key(
            private_key_data, password=password, backend=default_backend()
        )
        certificate = load_pem_x509_certificate(
            certificate_data, backend=default_backend()
        )

        return private_key, certificate

    except Exception as e:
        raise CertificateException(
            f"Failed to load certificate/key: {e}"
        ) from e
