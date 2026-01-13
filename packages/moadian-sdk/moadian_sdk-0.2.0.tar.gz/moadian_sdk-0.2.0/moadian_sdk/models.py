"""Data models for Moadian SDK"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class InvoiceStatus(Enum):
    """Invoice status enumeration"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"


class UnitCode(Enum):
    """واحدهای سنجش - Measurement Units"""

    # ردیف 1-15
    PIECE = (1611, "تیکه")
    NUMBER = (1612, "عدد")
    SET = (1613, "جمع")
    BAG = (1618, "تورب")
    PACKET = (1619, "ست")
    HAND = (1620, "دست")
    CARTON = (1624, "کارتن")
    METER = (1627, "متر")
    BRANCH = (1628, "شاخه")
    PACK = (1629, "پاکت")
    DEVICE = (1631, "دستگاه")
    BUNDLE = (1640, "بنچه")
    ROLL = (1641, "رول")
    PANEL = (1642, "طاقه")
    PAIR = (1643, "جفت")

    # ردیف 16-29
    SQUARE_METER = (1645, "متر مربع")
    PALLET = (1649, "پالت")
    BRANCH_2 = (1661, "فرعی")
    BOTTLE_PACK = (1668, "در یک بطری")
    SHEET = (1673, "قواشی")
    BUNDLE_2 = (1694, "قواشه (bundle)")
    LITER = (1637, "لیتر")
    BOWL = (1650, "ساشه")
    CAPSULE = (1683, "کپسول")
    BOTTLE = (1656, "بطدیل")
    DOZEN_HALF = (1630, "(دوازن)طقه")
    BOOK = (163, "قاب")
    CUBE = (1660, "عطر")
    CUBIC_METER = (1647, "متر مکعب")

    # ردیف 30-58
    BAG_2 = (1689, "توب")
    TUBE = (1690, "تیم دوجین")
    DOZEN = (1635, "فروه")
    KILOGRAM = (164, "کیلوگرم")
    TRAY = (1638, "طری")
    LARGE = (161, "برگ")
    BUCKET = (1625, "سطل")
    DAY = (1654, "روزی")
    BOX = (1646, "شانخه")
    DRUM = (1644, "قوطی")
    VOLUME = (1617, "جلد")
    BAG_3 = (162, "تورب")
    HOUR = (165, "شتر")
    COIL = (1610, "کلاف")
    CASE = (1615, "کیسه")
    FRAME = (1680, "طبرا")
    CONTAINER = (1639, "پنگ")
    CYLINDER = (1614, "گلند")
    CARTON_PACKAGE = (1687, "فاقد شبته بندی")
    MASTER_CASE = (1693, "کارتن (master case)")
    PAGE = (166, "صفحه")
    MAGAZINE = (1666, "مجزن")
    TANK = (1626, "تانکر")
    UNIT = (1648, "ده")
    PIECE_2 = (1684, "سید")
    LEAF = (169, "برن")
    BANK = (1651, "بانک")
    CYLINDER_2 = (1633, "سیلندر")
    CARTON_REFRIGERATOR = (1679, "فورت یخزه")

    # New items from second table (ردیف 59-89)
    WOOD = (168, "چوب")
    CHICKEN = (1665, "چیک")
    CHEEK = (1659, "چلیک")
    CUP = (1636, "جام")
    GRAM = (1622, "گرم")
    PIECE_3 = (1616, "تچ")
    CANDLE = (1652, "شمله")
    CARAT = (1678, "قیراط")
    MILLI_LITER = (16100, "میلی لیتر")
    MILLI_METER = (16101, "میلی متر")
    MILLI_GRAM = (16102, "میلی گرم")
    HOUR_2 = (16103, "ساعت")
    DAY_2 = (16104, "روز")
    TON_KILOMETER = (16105, "تن کیلومتر")
    KILOWATT_HOUR = (1669, "کیلووات ساعت")
    LITER_2 = (1676, "شتر")
    TUBE_2 = (16110, "تابه")
    MINUTE = (16111, "دقیقه")
    UNIT_2 = (16112, "ده")
    YEAR = (16113, "سال")
    PIECE_4 = (16114, "قطعه")
    SQUARE_CENTIMETER = (16115, "سانتی متر")
    SQUARE_METER_2 = (16116, "سانتی متر مربع")
    BUNDLE_3 = (1632, "فروند")
    UNIT_3 = (1653, "واحد")
    LIVAN = (16108, "لیوان")
    TON = (16117, "تونت")
    MEGAWATT_HOUR = (16118, "مگا وات ساعت")
    KILOGRAM_PER_TUBE = (16119, "کیلگو پایت بر تابه")
    RIYAL = (1681, "ریال")
    HALF_DOZEN = (1667, "جاطقه (دیسک)")
    BUNDLE_4 = (16120, "بسته (جلد)")

    # Additional from first table (ردیف 91-102)
    LITER_3 = (16121, "سینتر")
    CALORIE = (16122, "کالری")
    AMPERE = (16125, "آمپر")
    MILLI_AMPERE = (16126, "میلی آمپر")
    MISKAL = (16127, "مثقال")
    SEER = (16128, "سیر")
    TIME = (16129, "ده(time)")
    MEGA_BYTE = (16130, "مگا بویت")
    GALON = (16131, "گالون")
    BARREL = (16132, "برمن")
    BASKET = (16133, "باسکت")
    NIGHT = (16134, "شبم شماء")

    def __init__(self, code, persian_name):
        self.code = code
        self.persian_name = persian_name

    @classmethod
    def from_code(cls, code):
        """Get enum member by code"""
        for member in cls:
            if member.code == code:
                return member
        return None

    @classmethod
    def from_persian(cls, persian_name):
        """Get enum member by Persian name"""
        for member in cls:
            if member.persian_name == persian_name:
                return member
        return None

    def __int__(self):
        """Allow int() conversion to return the code"""
        return self.code

    def __str__(self):
        """String representation returns Persian name"""
        return self.persian_name

    def __repr__(self):
        """Repr shows both code and name"""
        return f"UnitCode.{self.name}({self.code}, '{self.persian_name}')"


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
    amount: float  # Quantity (double)
    unit_fee: float  # Unit price (double)
    vat_rate: float = 10.0  # VAT rate percentage (double)
    discount: float = 0.0  # Discount amount (double)
    mu: Union[UnitCode, str, int] = None  # Measurement unit code
    nw: Optional[float] = None  # Net weight (double, optional)
    cfee: Optional[float] = None  # Currency fee (double, optional)
    cut: Optional[str] = None  # Currency unit type (string, optional)
    exr: Optional[float] = None  # Exchange rate (double, optional)
    ssrv: Optional[float] = (
        None  # Service/Product sale rate value (double, optional)
    )
    sscv: Optional[float] = (
        None  # Service/Product sale currency value (double, optional)
    )
    vba: Optional[float] = None  # VAT base amount (double, optional)
    odt: Optional[str] = None  # Other discount type (string, optional)
    odr: Optional[float] = None  # Other discount rate (double, optional)
    odam: Optional[float] = None  # Other discount amount (double, optional)
    olt: Optional[str] = None  # Other levy type (string, optional)
    olr: Optional[float] = None  # Other levy rate (double, optional)
    olam: Optional[float] = None  # Other levy amount (double, optional)
    consfee: Optional[float] = None  # Construction fee (double, optional)
    spro: Optional[Any] = (
        None  # Special proportion (optional, kept for backward compatibility)
    )
    bros: Optional[Any] = (
        None  # Brokerage (optional, kept for backward compatibility)
    )
    tcpbs: Optional[Any] = (
        None  # Tax calculation per base section (optional, kept for backward compatibility)
    )
    cop: Optional[Any] = (
        None  # Customer order price (optional, kept for backward compatibility)
    )
    bsrn: Optional[Any] = (
        None  # Buyer's serial number (optional, kept for backward compatibility)
    )

    def __post_init__(self):
        """Set default measurement unit if not provided"""
        if self.mu is None:
            self.mu = UnitCode.NUMBER


@dataclass
class InvoiceData:
    """Complete invoice data"""

    seller_tin: str  # Seller Tax ID
    buyer_tin: str  # Buyer Tax ID
    items: List[InvoiceItem]  # List of InvoiceItem objects or dicts
    settlement_method: int = 1  # 1=Cash, 2=Credit
    invoice_type: int = 1  # Invoice type
    invoice_pattern: int = 1  # Invoice pattern
    invoice_subject: int = 1  # Invoice subject
