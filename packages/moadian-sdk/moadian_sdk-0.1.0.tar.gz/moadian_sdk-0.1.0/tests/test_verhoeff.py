"""Tests for Verhoeff checksum algorithm"""

from moadian_sdk.invoice import Verhoeff


class TestVerhoeff:
    """Test Verhoeff checksum algorithm"""

    def test_checksum_basic(self):
        """Test basic checksum calculation"""
        # Known test cases
        assert Verhoeff.checksum("123") == 3
        assert Verhoeff.checksum("1234") == 0
        assert Verhoeff.checksum("12345") == 1

    def test_checksum_empty_string(self):
        """Test checksum with empty string"""
        assert Verhoeff.checksum("") == 0

    def test_checksum_single_digit(self):
        """Test checksum with single digit"""
        assert Verhoeff.checksum("5") == 8
        # Verhoeff checksum for "0" is 4, not 0
        assert Verhoeff.checksum("0") == 4

    def test_checksum_long_number(self):
        """Test checksum with longer numbers"""
        # Test with 12-digit number (like serial)
        serial = "123456789012"
        checksum = Verhoeff.checksum(serial)
        assert isinstance(checksum, int)
        assert 0 <= checksum <= 9

    def test_validate_correct_checksum(self):
        """Test validation with correct checksum"""
        # Calculate checksum and append
        base = "123456789012"
        checksum = Verhoeff.checksum(base)
        number_with_check = base + str(checksum)

        assert Verhoeff.validate(number_with_check) is True

    def test_validate_incorrect_checksum(self):
        """Test validation with incorrect checksum"""
        base = "123456789012"
        checksum = Verhoeff.checksum(base)
        wrong_checksum = (checksum + 1) % 10
        number_with_wrong_check = base + str(wrong_checksum)

        assert Verhoeff.validate(number_with_wrong_check) is False

    def test_validate_empty_string(self):
        """Test validation with empty string"""
        assert Verhoeff.validate("") is True  # Empty string validates

    def test_checksum_consistency(self):
        """Test that checksum is consistent"""
        number = "651234567890"
        checksum1 = Verhoeff.checksum(number)
        checksum2 = Verhoeff.checksum(number)

        assert checksum1 == checksum2

    def test_validate_real_world_example(self):
        """Test with real-world like number"""
        # Simulate a decimal string like: UTF-8 codes + date + serial
        # Example: "651234567890" (12 digits)
        decimal_string = "651234567890"
        checksum = Verhoeff.checksum(decimal_string)
        full_number = decimal_string + str(checksum)

        assert Verhoeff.validate(full_number) is True

    def test_checksum_with_zeros(self):
        """Test checksum with numbers containing zeros"""
        # Verhoeff checksum calculations
        checksum_0000 = Verhoeff.checksum("0000")
        assert isinstance(checksum_0000, int)
        assert 0 <= checksum_0000 <= 9

        checksum_1000 = Verhoeff.checksum("1000")
        assert isinstance(checksum_1000, int)
        assert 0 <= checksum_1000 <= 9

        checksum_0100 = Verhoeff.checksum("0100")
        assert isinstance(checksum_0100, int)
        assert 0 <= checksum_0100 <= 9

    def test_validate_all_digits(self):
        """Test validation with all possible digits"""
        for digit in range(10):
            number = str(digit)
            checksum = Verhoeff.checksum(number)
            full = number + str(checksum)
            assert Verhoeff.validate(full) is True
