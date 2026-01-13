"""Invoice building and Tax ID generation"""

import os
from typing import Any, Dict, List, Optional, Union

from .exceptions import InvoiceException
from .models import InvoiceData, InvoiceItem, UnitCode


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

    def __init__(
        self,
        serial_file: str = "last_serial.txt",
        enable_file_storage: bool = False,
    ):
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
    items: Optional[List[Any]] = None,
    seller_tin: Optional[str] = None,
    buyer_tin: Optional[str] = None,
    invoice_type: int = 1,
    invoice_pattern: int = 1,
    invoice_subject: int = 1,
    settlement_method: int = 1,
    tob: int = 2,
    indati2m: Optional[int] = None,
    irtaxid: Optional[str] = None,
    bid: Optional[str] = None,
    sbc: Optional[str] = None,
    bpc: Optional[str] = None,
    bbc: Optional[str] = None,
    ft: Optional[int] = None,
    bpn: Optional[str] = None,
    scln: Optional[str] = None,
    scc: Optional[str] = None,
    cdcn: Optional[str] = None,
    cdcd: Optional[int] = None,
    crn: Optional[str] = None,
    billid: Optional[str] = None,
    todam: float = 0.0,
    tonw: Optional[float] = None,
    torv: Optional[float] = None,
    tocv: Optional[float] = None,
    cap: Optional[float] = None,
    insp: Optional[float] = None,
    tvop: Optional[float] = None,
    tax17: Optional[float] = None,
    tinc: Optional[str] = None,
    lno: Optional[str] = None,
    ocu: Optional[str] = None,
    sg: Optional[List[Dict[str, str]]] = None,
    payments: Optional[List[Dict[str, Any]]] = None,
    invoice_data: Optional[InvoiceData] = None,
) -> Dict[str, Any]:
    """
    Build invoice dictionary according to Moadian specification.

    Args:
        tax_id: Generated Tax ID (string)
        invoice_number: Invoice number (string)
        timestamp: Invoice timestamp in milliseconds (int)
        items: List of invoice items (dicts or InvoiceItem objects)
        seller_tin: Seller Tax ID (string, optional if invoice_data provided)
        buyer_tin: Buyer Tax ID (string, optional if invoice_data provided)
        invoice_type: Invoice type (int, default: 1)
        invoice_pattern: Invoice pattern (int, default: 1)
        invoice_subject: Invoice subject (int, default: 1)
        settlement_method: Settlement method - 1=Cash, 2=Credit (int, default: 1)
        tob: Type of business (int, default: 2)
        indati2m: Invoice date 2 timestamp (int, optional)
        irtaxid: Related tax ID (string, optional)
        bid: Buyer ID (string, optional)
        sbc: Seller branch code (string, optional)
        bpc: Buyer postal code (string, optional)
        bbc: Buyer branch code (string, optional)
        ft: Fiscal type (int, optional)
        bpn: Buyer passport number (string, optional)
        scln: Seller customer location number (string, optional)
        scc: Seller customer code (string, optional)
        cdcn: Customer document code number (string, optional)
        cdcd: Customer document code date (int, optional)
        crn: Customer registration number (string, optional)
        billid: Bill ID (string, optional)
        todam: Total other discount amount (float, default: 0.0)
        tonw: Total net weight (float, optional)
        torv: Total return value (float, optional)
        tocv: Total other charge value (float, optional)
        cap: Cap (float, optional)
        insp: Inspection (float, optional)
        tvop: Total value of payments (float, optional)
        tax17: Tax 17 (float, optional)
        tinc: Tax ID number code (string, optional)
        lno: License number (string, optional)
        ocu: Other currency unit (string, optional)
        sg: Array of objects with sgid (string) and sgt (string) (optional)
        payments: Array of payment objects (optional, auto-generated if not provided)
        invoice_data: InvoiceData object (optional, for backward compatibility)

    Returns:
        Complete invoice dictionary ready for encryption
    """
    # Support backward compatibility: if items is InvoiceData (old API), use it
    if isinstance(items, InvoiceData):
        invoice_data = items
        items = None

    # Extract values from invoice_data if provided, but allow overrides from kwargs
    if invoice_data is not None:
        # Use invoice_data values as defaults, but allow kwargs to override
        if seller_tin is None:
            seller_tin = invoice_data.seller_tin
        if buyer_tin is None:
            buyer_tin = invoice_data.buyer_tin
        if items is None:
            items = invoice_data.items
        # Only use invoice_data defaults if not explicitly provided
        if invoice_type == 1:
            invoice_type = invoice_data.invoice_type
        if invoice_pattern == 1:
            invoice_pattern = invoice_data.invoice_pattern
        if invoice_subject == 1:
            invoice_subject = invoice_data.invoice_subject
        if settlement_method == 1:
            settlement_method = invoice_data.settlement_method

    if items is None:
        raise ValueError("items or invoice_data must be provided")

    # Convert InvoiceItem objects to dictionaries if needed
    items_dict = []
    for item in items:
        if isinstance(item, InvoiceItem):
            # Calculate totals
            pre_discount = float(item.amount * item.unit_fee)
            after_discount = float(pre_discount - item.discount)
            vat_amount = float(after_discount * item.vat_rate / 100.0)
            total = float(after_discount + vat_amount)

            # Normalize mu to string code
            mu_str = normalize_mu(item.mu)

            # Build dictionary directly from InvoiceItem
            item_dict = {
                "sstid": item.sstid,
                "sstt": item.sstt,
                "am": item.amount,
                "mu": mu_str,
                "nw": item.nw,
                "fee": item.unit_fee,
                "cfee": item.cfee,
                "cut": item.cut,
                "exr": item.exr,
                "ssrv": item.ssrv,
                "sscv": item.sscv,
                "prdis": pre_discount,
                "dis": item.discount,
                "adis": after_discount,
                "vra": item.vat_rate,
                "vba": item.vba,
                "vam": vat_amount,
                "odt": item.odt,
                "odr": item.odr,
                "odam": item.odam,
                "olt": item.olt,
                "olr": item.olr,
                "olam": item.olam,
                "consfee": item.consfee,
                "tsstam": total,
                "spro": item.spro,
                "bros": item.bros,
                "tcpbs": item.tcpbs,
                "cop": item.cop,
                "bsrn": item.bsrn,
            }
            items_dict.append(item_dict)
        else:
            items_dict.append(item)

    # Calculate totals from items
    total_pre_discount = sum(item["prdis"] for item in items_dict)
    total_discount = sum(item["dis"] for item in items_dict)
    total_after_discount = sum(item["adis"] for item in items_dict)
    total_vat = sum(item["vam"] for item in items_dict)
    total_bill = sum(item["tsstam"] for item in items_dict)

    # Build header dictionary with all fields
    header = {
        "taxid": tax_id,
        "indatim": timestamp,
        "indati2m": indati2m,
        "inty": invoice_type,
        "inno": invoice_number,
        "irtaxid": irtaxid,
        "inp": invoice_pattern,
        "ins": invoice_subject,
        "tins": seller_tin,
        "tob": tob,
        "bid": bid,
        "tinb": buyer_tin,
        "sbc": sbc,
        "bpc": bpc,
        "bbc": bbc,
        "ft": ft,
        "bpn": bpn,
        "scln": scln,
        "scc": scc,
        "cdcn": cdcn,
        "cdcd": cdcd,
        "crn": crn,
        "billid": billid,
        "tprdis": (total_pre_discount),
        "tdis": (total_discount),
        "tadis": (total_after_discount),
        "tvam": (total_vat),
        "todam": (todam),
        "tbill": (total_bill),
        "tonw": tonw,
        "torv": torv,
        "tocv": tocv,
        "setm": settlement_method,
        "cap": cap,
        "insp": insp,
        "tvop": tvop,
        "tax17": tax17,
        "tinc": tinc,
        "lno": lno,
        "ocu": ocu,
        "sg": sg,
    }

    # Determine payments
    if payments is not None:
        payments_list = payments
    elif settlement_method == 1:
        payments_list = []
    else:
        payments_list = None

    invoice = {
        "header": header,
        "body": items_dict,
        "payments": payments_list,
    }

    return invoice


def normalize_mu(mu: Union[UnitCode, str, int, None]) -> str:
    """
    Normalize measurement unit to string code.

    Converts UnitCode enum, int code, or string code to a string representation.
    If None is provided, defaults to UnitCode.NUMBER code.

    Args:
        mu: Measurement unit (UnitCode enum, string code, int code, or None)

    Returns:
        String representation of the measurement unit code
    """
    if mu is None:
        return str(UnitCode.NUMBER.code)

    if isinstance(mu, UnitCode):
        return str(mu.code)

    if isinstance(mu, int):
        unit = UnitCode.from_code(mu)
        return str(unit.code) if unit else str(mu)

    # It's already a string
    return str(mu)


def create_invoice_item(
    sstid: str,
    sstt: str,
    amount: float,
    unit_fee: float,
    vat_rate: float = 10.0,
    discount: float = 0.0,
    mu: Union[UnitCode, str, int] = UnitCode.NUMBER,
    nw: Optional[float] = None,
    cfee: Optional[float] = None,
    cut: Optional[str] = None,
    exr: Optional[float] = None,
    ssrv: Optional[float] = None,
    sscv: Optional[float] = None,
    vba: Optional[float] = None,
    odt: Optional[str] = None,
    odr: Optional[float] = None,
    odam: Optional[float] = None,
    olt: Optional[str] = None,
    olr: Optional[float] = None,
    olam: Optional[float] = None,
    consfee: Optional[float] = None,
    spro: Optional[Any] = None,
    bros: Optional[Any] = None,
    tcpbs: Optional[Any] = None,
    cop: Optional[Any] = None,
    bsrn: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create a single invoice item dictionary.

    Args:
        sstid: Service/Product ID
        sstt: Service/Product Title
        amount: Quantity (double)
        unit_fee: Unit price (double)
        vat_rate: VAT rate percentage (double, default: 10.0)
        discount: Discount amount (double, default: 0.0)
        mu: Measurement unit (UnitCode enum, string code, int code, or default NUMBER)
        nw: Net weight (double, optional)
        cfee: Currency fee (double, optional)
        cut: Currency unit type (string, optional)
        exr: Exchange rate (double, optional)
        ssrv: Service/Product sale rate value (double, optional)
        sscv: Service/Product sale currency value (double, optional)
        vba: VAT base amount (double, optional)
        odt: Other discount type (string, optional)
        odr: Other discount rate (double, optional)
        odam: Other discount amount (double, optional)
        olt: Other levy type (string, optional)
        olr: Other levy rate (double, optional)
        olam: Other levy amount (double, optional)
        consfee: Construction fee (double, optional)
        spro: Special proportion (optional, kept for backward compatibility)
        bros: Brokerage (optional, kept for backward compatibility)
        tcpbs: Tax calculation per base section (optional, kept for backward compatibility)
        cop: Customer order price (optional, kept for backward compatibility)
        bsrn: Buyer's serial number (optional, kept for backward compatibility)

    Returns:
        Invoice item dictionary
    """
    pre_discount = float(amount * unit_fee)
    after_discount = float(pre_discount - discount)
    vat_amount = float(after_discount * vat_rate / 100.0)
    total = float(after_discount + vat_amount)

    # Normalize mu to string code
    mu_str = normalize_mu(mu)

    # Build the dictionary with all fields directly
    item = {
        "sstid": sstid,
        "sstt": sstt,
        "am": amount,
        "mu": mu_str,
        "nw": nw,
        "fee": unit_fee,
        "cfee": cfee,
        "cut": cut,
        "exr": exr,
        "ssrv": ssrv,
        "sscv": sscv,
        "prdis": pre_discount,
        "dis": discount,
        "adis": after_discount,
        "vra": vat_rate,
        "vba": vba,
        "vam": vat_amount,
        "odt": odt,
        "odr": odr,
        "odam": odam,
        "olt": olt,
        "olr": olr,
        "olam": olam,
        "consfee": consfee,
        "tsstam": total,
        "spro": spro,
        "bros": bros,
        "tcpbs": tcpbs,
        "cop": cop,
        "bsrn": bsrn,
    }

    return item
