"""Invoice building and Tax ID generation"""

import os
from typing import Any, Dict, Optional

from .exceptions import InvoiceException
from .models import InvoiceData, InvoiceItem


class Verhoeff:
    """Verhoeff checksum algorithm implementation"""

    d_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]

    p_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
    ]

    inv_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

    @staticmethod
    def checksum(num_str: str) -> int:
        """Calculate Verhoeff checksum digit"""
        c = 0
        for i, digit_char in enumerate(reversed(num_str)):
            digit = int(digit_char)
            c = Verhoeff.d_table[c][Verhoeff.p_table[(i + 1) % 8][digit]]
        return Verhoeff.inv_table[c]

    @staticmethod
    def validate(num_str_with_check: str) -> bool:
        """Validate a number with Verhoeff checksum"""
        c = 0
        for i, digit_char in enumerate(reversed(num_str_with_check)):
            digit = int(digit_char)
            c = Verhoeff.d_table[c][Verhoeff.p_table[i % 8][digit]]
        return c == 0


class SerialNumberManager:
    """Manages sequential serial numbers for invoices"""

    def __init__(self, serial_file: str = "last_serial.txt", enable_file_storage: bool = False):
        """
        Initialize serial number manager.

        Args:
            serial_file: Path to serial file
            enable_file_storage: If True, save serials to file. If False, use in-memory only.
        """
        self.serial_file = serial_file
        self.enable_file_storage = enable_file_storage
        self._in_memory_serial: Optional[int] = None
        self._in_memory_date: Optional[str] = None

    def _get_today_key(self) -> str:
        """Get today's date as YYYY-MM-DD"""
        import datetime
        return datetime.date.today().isoformat()

    def get_next_serial(self) -> int:
        """Get next sequential serial number for today (resets daily)"""
        today = self._get_today_key()

        # If date changed, reset serial
        if self._in_memory_date != today:
            self._in_memory_date = today
            self._in_memory_serial = self._load_serial(today)

        # Increment serial
        self._in_memory_serial += 1

        # Validate max value (10 hex digits = 0xFFFFFFFFFF)
        if self._in_memory_serial > 0xFFFFFFFFFF:
            self._in_memory_serial = 1

        return self._in_memory_serial

    def _load_serial(self, date: str) -> int:
        """Load today's last serial from file or start from 0"""
        if not self.enable_file_storage:
            return 0

        if not os.path.exists(self.serial_file):
            return 0

        try:
            with open(self.serial_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Format: YYYY-MM-DD:serial_number
                    if ":" in line:
                        file_date, serial_str = line.split(":", 1)
                        if file_date == date:
                            return int(serial_str)
            return 0
        except (FileNotFoundError, ValueError, IndexError, IOError, OSError):
            return 0

    def save_serial(self, serial: int):
        """Save serial number for today (only if file storage is enabled)"""
        if not self.enable_file_storage:
            return

        today = self._get_today_key()

        # Read existing data
        lines = {}
        if os.path.exists(self.serial_file):
            try:
                with open(self.serial_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and ":" in line and not line.startswith("#"):
                            file_date, _ = line.split(":", 1)
                            lines[file_date] = line
            except (IOError, OSError):
                pass

        # Update today's serial
        lines[today] = f"{today}:{serial}"

        # Write back (keep only last 30 days to avoid file bloat)
        sorted_dates = sorted(lines.keys(), reverse=True)[:30]

        try:
            with open(self.serial_file, "w", encoding="utf-8") as f:
                f.write("# Date-based serial numbers (YYYY-MM-DD:serial)\n")
                for file_date in sorted_dates:
                    f.write(f"{lines[file_date]}\n")
        except (IOError, OSError):
            # Silently fail if can't write (server environments)
            pass


def generate_tax_id(fiscal_id: str, timestamp_ms: int, serial_int: int) -> str:
    """
    Generate Tax ID according to official documentation.

    Args:
        fiscal_id: 6-character fiscal memory ID
        timestamp_ms: Timestamp in milliseconds
        serial_int: Serial number (decimal)

    Returns:
        22-character Tax ID with Verhoeff checksum

    Raises:
        InvoiceException: If fiscal_id is invalid
    """
    # Validate fiscal ID
    part1 = fiscal_id.upper()
    if len(part1) != 6:
        raise InvoiceException("Fiscal ID must be exactly 6 characters")

    # Calculate days since Unix epoch
    days_since_epoch = timestamp_ms // 86_400_000

    # Part 2: Date in hex (5 digits, uppercase, zero-padded)
    part2 = format(days_since_epoch, "X").zfill(5).upper()

    # Part 3: Serial in hex (10 digits, uppercase, zero-padded)
    part3 = format(serial_int, "X").zfill(10).upper()

    # Build base hex Tax ID (without checksum)
    base_hex = part1 + part2 + part3

    # Build decimal string: UTF-8 + Date + Serial
    utf8_string = "".join(str(ord(ch)) for ch in part1)
    date_str = str(days_since_epoch).zfill(6)
    serial_str = str(serial_int).zfill(12)

    # Correct order per documentation: UTF-8 + Date + Serial
    decimal_string = utf8_string + date_str + serial_str

    # Calculate checksum
    check_digit = Verhoeff.checksum(decimal_string)

    # Complete Tax ID
    tax_id = base_hex + str(check_digit)

    return tax_id


def build_invoice_dict(
    tax_id: str,
    invoice_number: str,
    timestamp: int,
    invoice_data: InvoiceData,
) -> Dict[str, Any]:
    """
    Build invoice dictionary according to Moadian specification.

    Args:
        tax_id: Generated Tax ID
        invoice_number: Invoice number (extracted from Tax ID)
        timestamp: Invoice timestamp in milliseconds
        invoice_data: InvoiceData object containing invoice details

    Returns:
        Complete invoice dictionary ready for encryption
    """
    # Convert InvoiceItem objects to dictionaries if needed
    items_dict = []
    for item in invoice_data.items:
        if isinstance(item, InvoiceItem):
            items_dict.append(
                create_invoice_item(
                    sstid=item.sstid,
                    sstt=item.sstt,
                    amount=item.amount,
                    unit_fee=item.unit_fee,
                    vat_rate=item.vat_rate,
                    discount=item.discount,
                    measurement_unit=item.measurement_unit,
                )
            )
        else:
            items_dict.append(item)

    # Calculate totals from items
    total_pre_discount = sum(item["prdis"] for item in items_dict)
    total_discount = sum(item["dis"] for item in items_dict)
    total_after_discount = sum(item["adis"] for item in items_dict)
    total_vat = sum(item["vam"] for item in items_dict)
    total_bill = sum(item["tsstam"] for item in items_dict)

    invoice = {
        "header": {
            "taxid": tax_id,
            "indatim": timestamp,
            "inty": invoice_data.invoice_type,
            "inno": invoice_number,
            "irtaxid": None,
            "inp": invoice_data.invoice_pattern,
            "ins": invoice_data.invoice_subject,
            "tins": invoice_data.seller_tin,
            "tinb": invoice_data.buyer_tin,
            "tob": 2,
            "bid": None,
            "sbc": None,
            "bpc": None,
            "bbc": None,
            "ft": None,
            "bpn": None,
            "scln": None,
            "scc": None,
            "crn": None,
            "billid": None,
            "tprdis": total_pre_discount,
            "tdis": total_discount,
            "tadis": total_after_discount,
            "tvam": total_vat,
            "todam": 0,
            "tbill": total_bill,
            "setm": invoice_data.settlement_method,
            "tax17": None,
        },
        "body": items_dict,
        "payments": [] if invoice_data.settlement_method == 1 else None,
    }

    return invoice


def create_invoice_item(
    sstid: str,
    sstt: str,
    amount: int,
    unit_fee: int,
    vat_rate: int = 10,
    discount: int = 0,
    measurement_unit: str = "164",
) -> Dict[str, Any]:
    """
    Create a single invoice item dictionary.

    Args:
        sstid: Service/Product ID
        sstt: Service/Product Title
        amount: Quantity
        unit_fee: Unit price
        vat_rate: VAT rate percentage (default: 10)
        discount: Discount amount (default: 0)
        measurement_unit: Measurement unit code (default: "164")

    Returns:
        Invoice item dictionary
    """
    pre_discount = amount * unit_fee
    after_discount = pre_discount - discount
    vat_amount = int(after_discount * vat_rate / 100)
    total = after_discount + vat_amount

    return {
        "sstid": sstid,
        "sstt": sstt,
        "am": amount,
        "mu": measurement_unit,
        "fee": unit_fee,
        "cfee": None,
        "cut": None,
        "exr": None,
        "prdis": pre_discount,
        "dis": discount,
        "adis": after_discount,
        "vra": vat_rate,
        "vam": vat_amount,
        "odt": None,
        "odr": None,
        "odam": None,
        "olt": None,
        "olr": None,
        "olam": None,
        "consfee": None,
        "spro": None,
        "bros": None,
        "tcpbs": None,
        "cop": None,
        "bsrn": None,
        "tsstam": total,
    }
