"""Tests for invoice building functions"""

from moadian_sdk.invoice import build_invoice_dict, create_invoice_item
from moadian_sdk.models import InvoiceData, InvoiceItem, UnitCode


class TestInvoiceItem:
    """Test invoice item creation"""

    def test_create_basic_item(self):
        """Test creating basic invoice item"""
        item = create_invoice_item(
            sstid="1234567890123",
            sstt="Test Product",
            amount=1,
            unit_fee=10000,
        )

        assert item["sstid"] == "1234567890123"
        assert item["sstt"] == "Test Product"
        assert item["am"] == 1
        assert item["fee"] == 10000
        assert item["vra"] == 10  # Default VAT rate
        assert item["dis"] == 0  # Default discount

    def test_calculate_totals(self):
        """Test total calculations"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=2,  # Quantity
            unit_fee=10000,  # Unit price
            vat_rate=10,
            discount=1000,
        )

        # Pre-discount: 2 * 10000 = 20000
        assert item["prdis"] == 20000

        # Discount: 1000
        assert item["dis"] == 1000

        # After discount: 20000 - 1000 = 19000
        assert item["adis"] == 19000

        # VAT: 19000 * 10% = 1900
        assert item["vam"] == 1900

        # Total: 19000 + 1900 = 20900
        assert item["tsstam"] == 20900

    def test_vat_calculation(self):
        """Test VAT calculation"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
            vat_rate=9,  # 9% VAT
        )

        # After discount: 10000 (no discount)
        assert item["adis"] == 10000
        # VAT: 10000 * 9% = 900
        assert item["vam"] == 900
        # Total: 10000 + 900 = 10900
        assert item["tsstam"] == 10900

    def test_zero_discount(self):
        """Test with zero discount"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
            discount=0,
        )

        assert item["prdis"] == item["adis"]
        assert item["dis"] == 0

    def test_custom_measurement_unit(self):
        """Test custom measurement unit with string"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
            mu="165",
        )

        assert item["mu"] == "165"

    def test_measurement_unit_with_enum(self):
        """Test measurement unit with UnitCode enum"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
            mu=UnitCode.HOUR,
        )

        assert item["mu"] == "165"

    def test_measurement_unit_with_int(self):
        """Test measurement unit with integer code"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
            mu=164,
        )

        assert item["mu"] == "164"

    def test_default_measurement_unit(self):
        """Test default measurement unit is NUMBER (1612)"""
        item = create_invoice_item(
            sstid="123",
            sstt="Product",
            amount=1,
            unit_fee=10000,
        )

        assert item["mu"] == "1612"

    def test_all_fields(self):
        """Test all fields are present"""
        item = create_invoice_item(
            sstid="1234567890123",
            sstt="Test Product",
            amount=5,
            unit_fee=20000,
            vat_rate=10,
            discount=5000,
            mu=UnitCode.KILOGRAM,
        )

        # Check all required fields
        required_fields = [
            "sstid",
            "sstt",
            "am",
            "mu",
            "fee",
            "prdis",
            "dis",
            "adis",
            "vra",
            "vam",
            "tsstam",
        ]
        for field in required_fields:
            assert field in item


class TestInvoiceBuilding:
    """Test invoice dictionary building"""

    def test_build_basic_invoice(self):
        """Test building basic invoice"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="1234567890",
            buyer_tin="0987654321",
            items=[
                create_invoice_item(
                    sstid="123",
                    sstt="Product",
                    amount=1,
                    unit_fee=10000,
                )
            ],
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        assert invoice_dict["header"]["taxid"] == tax_id
        assert invoice_dict["header"]["inno"] == invoice_number
        assert invoice_dict["header"]["indatim"] == timestamp
        assert invoice_dict["header"]["tins"] == "1234567890"
        assert invoice_dict["header"]["tinb"] == "0987654321"

    def test_invoice_totals(self):
        """Test invoice totals calculation"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="123",
            buyer_tin="456",
            items=[
                create_invoice_item(
                    sstid="1",
                    sstt="Item 1",
                    amount=2,
                    unit_fee=10000,
                    discount=1000,
                ),
                create_invoice_item(
                    sstid="2",
                    sstt="Item 2",
                    amount=1,
                    unit_fee=5000,
                    discount=0,
                ),
            ],
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        header = invoice_dict["header"]

        # Item 1: 2 * 10000 = 20000, discount 1000, after discount 19000, VAT 1900, total 20900
        # Item 2: 1 * 5000 = 5000, discount 0, after discount 5000, VAT 500, total 5500
        # Totals:
        # tprdis: 20000 + 5000 = 25000
        # tdis: 1000 + 0 = 1000
        # tadis: 19000 + 5000 = 24000
        # tvam: 1900 + 500 = 2400
        # tbill: 20900 + 5500 = 26400

        assert header["tprdis"] == 25000
        assert header["tdis"] == 1000
        assert header["tadis"] == 24000
        assert header["tvam"] == 2400
        assert header["tbill"] == 26400

    def test_settlement_method_cash(self):
        """Test cash settlement method"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="123",
            buyer_tin="456",
            items=[create_invoice_item("1", "Item", 1, 10000)],
            settlement_method=1,  # Cash
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        assert invoice_dict["header"]["setm"] == 1
        assert invoice_dict["payments"] == []

    def test_settlement_method_credit(self):
        """Test credit settlement method"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="123",
            buyer_tin="456",
            items=[create_invoice_item("1", "Item", 1, 10000)],
            settlement_method=2,  # Credit
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        assert invoice_dict["header"]["setm"] == 2
        assert invoice_dict["payments"] is None

    def test_invoice_with_invoiceitem_objects(self):
        """Test building invoice with InvoiceItem objects"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="123",
            buyer_tin="456",
            items=[
                InvoiceItem(
                    sstid="123",
                    sstt="Product",
                    amount=1,
                    unit_fee=10000,
                )
            ],
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        assert len(invoice_dict["body"]) == 1
        assert invoice_dict["body"][0]["sstid"] == "123"
        # Default measurement unit should be NUMBER (1612)
        assert invoice_dict["body"][0]["mu"] == "1612"

    def test_multiple_items(self):
        """Test invoice with multiple items"""
        tax_id = "TESTID0000100000000001"
        invoice_number = "0000000001"
        timestamp = 1704067200000

        invoice_data = InvoiceData(
            seller_tin="123",
            buyer_tin="456",
            items=[
                create_invoice_item("1", "Item 1", 1, 10000),
                create_invoice_item("2", "Item 2", 2, 5000),
                create_invoice_item("3", "Item 3", 3, 3000),
            ],
        )

        invoice_dict = build_invoice_dict(
            tax_id, invoice_number, timestamp, invoice_data
        )

        assert len(invoice_dict["body"]) == 3
        assert invoice_dict["body"][0]["sstid"] == "1"
        assert invoice_dict["body"][1]["sstid"] == "2"
        assert invoice_dict["body"][2]["sstid"] == "3"
