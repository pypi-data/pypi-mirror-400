"""
Moadian SDK - Iranian Tax Organization API Client

A simple and clean SDK for interacting with the Moadian tax system.

Example:
    >>> from moadian_sdk import MoadianClient, InvoiceData, create_invoice_item
    >>>
    >>> # Initialize client
    >>> client = MoadianClient(
    ...     client_id="YOUR_FISCAL_ID",
    ...     certs_dir="certs"
    ... )
    >>>
    >>> # Create invoice items
    >>> items = [
    ...     create_invoice_item(
    ...         sstid="PRODUCT_ID",
    ...         sstt="Product Name",
    ...         amount=1,
    ...         unit_fee=10000,
    ...         vat_rate=10,
    ...     )
    ... ]
    >>>
    >>> # Create invoice data
    >>> invoice_data = InvoiceData(
    ...     seller_tin="YOUR_TAX_ID",
    ...     buyer_tin="BUYER_TAX_ID",
    ...     items=items,
    ...     settlement_method=1,
    ... )
    >>>
    >>> # Send invoice
    >>> with client:
    ...     response = client.send_invoice(invoice_data)
    ...     print(f"Invoice sent! UID: {response.uid}")
"""

from .client import MoadianClient
from .exceptions import (
    APIException,
    AuthenticationException,
    CertificateException,
    InvoiceException,
    MoadianException,
)
from .invoice import create_invoice_item
from .models import (
    InvoiceData,
    InvoiceItem,
    InvoiceResponse,
    InvoiceStatus,
    UnitCode,
)

__all__ = [
    # Client
    "MoadianClient",
    # Models
    "InvoiceData",
    "InvoiceItem",
    "InvoiceResponse",
    "InvoiceStatus",
    "UnitCode",
    # Utilities
    "create_invoice_item",
    # Exceptions
    "MoadianException",
    "AuthenticationException",
    "APIException",
    "CertificateException",
    "InvoiceException",
]

__version__ = "0.1.0"
