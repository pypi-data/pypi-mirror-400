"""Tests for Tax ID generation"""

import datetime

import pytest

from moadian_sdk.exceptions import InvoiceException
from moadian_sdk.invoice import generate_tax_id


class TestTaxIDGeneration:
    """Test Tax ID generation algorithm"""

    def test_basic_tax_id_generation(self):
        """Test basic Tax ID generation"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000  # 2024-01-01 00:00:00 UTC
        serial = 1

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Tax ID should be 22 characters (6 fiscal + 5 date + 10 serial + 1 checksum)
        assert len(tax_id) == 22
        assert tax_id.startswith(fiscal_id.upper())

    def test_tax_id_format(self):
        """Test Tax ID format correctness"""
        fiscal_id = "ABCDEF"
        timestamp_ms = 1704067200000
        serial = 12345

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Should be uppercase
        assert tax_id.isupper()
        # Should start with fiscal ID
        assert tax_id[:6] == fiscal_id.upper()
        # Should be exactly 22 characters
        assert len(tax_id) == 22

    def test_fiscal_id_validation(self):
        """Test fiscal ID validation"""
        # Too short
        with pytest.raises(InvoiceException, match="exactly 6 characters"):
            generate_tax_id("ABC", 1704067200000, 1)

        # Too long
        with pytest.raises(InvoiceException, match="exactly 6 characters"):
            generate_tax_id("ABCDEFG", 1704067200000, 1)

        # Empty
        with pytest.raises(InvoiceException):
            generate_tax_id("", 1704067200000, 1)

    def test_fiscal_id_case_insensitive(self):
        """Test that fiscal ID is case-insensitive"""
        timestamp_ms = 1704067200000
        serial = 1

        tax_id_lower = generate_tax_id("abcdef", timestamp_ms, serial)
        tax_id_upper = generate_tax_id("ABCDEF", timestamp_ms, serial)

        # Should produce same result (uppercase)
        assert tax_id_lower == tax_id_upper
        assert tax_id_lower.startswith("ABCDEF")

    def test_date_calculation(self):
        """Test date calculation in Tax ID"""
        fiscal_id = "TESTID"
        serial = 1

        # Test with known date
        # 2024-01-01 00:00:00 UTC = 1704067200000 ms
        timestamp_ms = 1704067200000
        days_since_epoch = timestamp_ms // 86400000  # Should be 19723

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Date part should be in hex (5 digits)
        # Extract date part (positions 6-10)
        date_part_hex = tax_id[6:11]
        assert len(date_part_hex) == 5
        assert date_part_hex.isalnum()

    def test_serial_encoding(self):
        """Test serial number encoding"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000

        # Test with different serials
        serial1 = 1
        serial2 = 100
        serial3 = 0xFFFFFFFFFF  # Max value

        tax_id1 = generate_tax_id(fiscal_id, timestamp_ms, serial1)
        tax_id2 = generate_tax_id(fiscal_id, timestamp_ms, serial2)
        tax_id3 = generate_tax_id(fiscal_id, timestamp_ms, serial3)

        # All should be 22 characters
        assert len(tax_id1) == 22
        assert len(tax_id2) == 22
        assert len(tax_id3) == 22

        # Serial part should be different (positions 11-20)
        assert tax_id1[11:21] != tax_id2[11:21]
        assert tax_id2[11:21] != tax_id3[11:21]

    def test_checksum_included(self):
        """Test that checksum is included in Tax ID"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000
        serial = 12345

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Last character should be checksum digit (0-9)
        checksum_digit = tax_id[-1]
        assert checksum_digit.isdigit()
        assert 0 <= int(checksum_digit) <= 9

    def test_different_dates_produce_different_ids(self):
        """Test that different dates produce different Tax IDs"""
        fiscal_id = "TESTID"
        serial = 1

        # Same day, different times
        timestamp1 = 1704067200000  # 2024-01-01 00:00:00
        timestamp2 = 1704153600000  # 2024-01-02 00:00:00

        tax_id1 = generate_tax_id(fiscal_id, timestamp1, serial)
        tax_id2 = generate_tax_id(fiscal_id, timestamp2, serial)

        # Should be different due to date change
        assert tax_id1 != tax_id2
        # Date parts should be different
        assert tax_id1[6:11] != tax_id2[6:11]

    def test_different_serials_produce_different_ids(self):
        """Test that different serials produce different Tax IDs"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000

        serial1 = 1
        serial2 = 2

        tax_id1 = generate_tax_id(fiscal_id, timestamp_ms, serial1)
        tax_id2 = generate_tax_id(fiscal_id, timestamp_ms, serial2)

        # Should be different
        assert tax_id1 != tax_id2
        # Serial parts should be different
        assert tax_id1[11:21] != tax_id2[11:21]

    def test_serial_zero(self):
        """Test with serial zero"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000
        serial = 0

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        assert len(tax_id) == 22
        # Serial part should be zero-padded
        assert tax_id[11:21] == "0000000000"

    def test_large_serial(self):
        """Test with large serial number"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000
        serial = 9999999999  # Large serial

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        assert len(tax_id) == 22
        # Should handle large serials correctly
        assert tax_id[11:21].isalnum()

    def test_consistency(self):
        """Test that same inputs produce same Tax ID"""
        fiscal_id = "TESTID"
        timestamp_ms = 1704067200000
        serial = 12345

        tax_id1 = generate_tax_id(fiscal_id, timestamp_ms, serial)
        tax_id2 = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Should be identical
        assert tax_id1 == tax_id2

    def test_real_world_example(self):
        """Test with realistic values"""
        fiscal_id = "TESTID"
        # Current timestamp
        timestamp_ms = int(datetime.datetime.now().timestamp() * 1000)
        serial = 42

        tax_id = generate_tax_id(fiscal_id, timestamp_ms, serial)

        # Verify structure
        assert len(tax_id) == 22
        assert tax_id[:6] == "TESTID"
        assert tax_id[-1].isdigit()  # Checksum digit
