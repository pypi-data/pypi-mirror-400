"""Data models for Moadian SDK"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class InvoiceStatus(Enum):
    """Invoice status enumeration"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"


@dataclass
class ServerInfo:
    """Server information response"""

    server_time: int
    public_keys: List[Dict[str, Any]]


@dataclass
class InvoiceResponse:
    """Invoice submission response"""

    uid: str
    reference_number: str
    tax_id: str
    serial: int
    packet_type: Optional[str] = None
    data: Optional[Any] = None


@dataclass
class InvoiceItem:
    """Invoice item data"""

    sstid: str  # Service/Product ID
    sstt: str  # Service/Product Title
    amount: int  # Quantity
    unit_fee: int  # Unit price
    vat_rate: int = 10  # VAT rate percentage
    discount: int = 0  # Discount amount
    measurement_unit: str = "164"  # Measurement unit code


@dataclass
class InvoiceData:
    """Complete invoice data"""

    seller_tin: str  # Seller Tax ID
    buyer_tin: str  # Buyer Tax ID
    items: List[InvoiceItem]
    settlement_method: int = 1  # 1=Cash, 2=Credit
    invoice_type: int = 1  # Invoice type
    invoice_pattern: int = 1  # Invoice pattern
    invoice_subject: int = 1  # Invoice subject
