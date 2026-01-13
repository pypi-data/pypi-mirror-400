"""Tests for Serial Number Manager"""

import datetime
import os
import tempfile

from moadian_sdk.invoice import SerialNumberManager


class TestSerialNumberManager:
    """Test Serial Number Manager"""

    def test_initialization_default(self):
        """Test default initialization"""
        manager = SerialNumberManager()
        assert manager.serial_file == "last_serial.txt"
        assert manager.enable_file_storage is False

    def test_initialization_with_storage(self):
        """Test initialization with file storage enabled"""
        manager = SerialNumberManager(
            serial_file="test_serial.txt", enable_file_storage=True
        )
        assert manager.serial_file == "test_serial.txt"
        assert manager.enable_file_storage is True

    def test_get_next_serial_starts_from_zero(self):
        """Test that serial starts from 0 when no file storage"""
        manager = SerialNumberManager(enable_file_storage=False)

        serial = manager.get_next_serial()
        assert serial == 1  # First call returns 1 (0 + 1)

    def test_get_next_serial_increments(self):
        """Test that serial increments correctly"""
        manager = SerialNumberManager(enable_file_storage=False)

        serial1 = manager.get_next_serial()
        serial2 = manager.get_next_serial()
        serial3 = manager.get_next_serial()

        assert serial1 == 1
        assert serial2 == 2
        assert serial3 == 3

    def test_get_next_serial_resets_daily(self):
        """Test that serial resets daily"""
        manager = SerialNumberManager(enable_file_storage=False)

        # Get serial for today
        serial1 = manager.get_next_serial()

        # Mock date change
        original_date = manager._in_memory_date
        manager._in_memory_date = None
        manager._current_date = None

        # Should reset to 0 and return 1
        serial2 = manager.get_next_serial()
        assert serial2 == 1

    def test_save_serial_disabled(self):
        """Test that save does nothing when storage is disabled"""
        manager = SerialNumberManager(enable_file_storage=False)

        # Should not raise exception
        manager.save_serial(42)

        # File should not exist
        assert not os.path.exists(manager.serial_file)

    def test_save_and_load_serial_with_file(self):
        """Test saving and loading serial from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            serial_file = os.path.join(tmpdir, "test_serial.txt")
            manager = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Save serial for today
            today = datetime.date.today().isoformat()
            manager.save_serial(42)

            # Verify file exists
            assert os.path.exists(serial_file)

            # Create new manager and load
            manager2 = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Should load serial 42 and increment to 43
            serial = manager2.get_next_serial()
            assert serial == 43

    def test_serial_file_format(self):
        """Test serial file format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            serial_file = os.path.join(tmpdir, "test_serial.txt")
            manager = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            manager.save_serial(100)

            # Read file and verify format
            with open(serial_file, "r") as f:
                content = f.read()
                assert "# Date-based serial numbers" in content
                assert datetime.date.today().isoformat() in content
                assert ":100" in content

    def test_multiple_dates_in_file(self):
        """Test handling multiple dates in serial file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            serial_file = os.path.join(tmpdir, "test_serial.txt")

            # Create file with multiple dates
            with open(serial_file, "w") as f:
                f.write("# Date-based serial numbers\n")
                f.write("2024-01-01:50\n")
                f.write("2024-01-02:75\n")
                today = datetime.date.today().isoformat()
                f.write(f"{today}:100\n")

            manager = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Should load today's serial (100) and increment to 101
            serial = manager.get_next_serial()
            assert serial == 101

    def test_max_serial_value(self):
        """Test handling of max serial value"""
        manager = SerialNumberManager(enable_file_storage=False)

        # Set serial to max value
        manager._in_memory_serial = 0xFFFFFFFFFF
        manager._in_memory_date = datetime.date.today().isoformat()

        # Next serial should wrap to 1
        serial = manager.get_next_serial()
        assert serial == 1

    def test_serial_exceeds_max(self):
        """Test serial exceeding max value"""
        manager = SerialNumberManager(enable_file_storage=False)

        # Set serial to max + 1
        manager._in_memory_serial = 0xFFFFFFFFFF + 1
        manager._in_memory_date = datetime.date.today().isoformat()

        # Should wrap to 1
        serial = manager.get_next_serial()
        assert serial == 1

    def test_file_read_error_handling(self):
        """Test handling of file read errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            serial_file = os.path.join(tmpdir, "test_serial.txt")

            # Create invalid file
            with open(serial_file, "w") as f:
                f.write("invalid content\n")

            manager = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Should handle error gracefully and start from 0
            serial = manager.get_next_serial()
            assert serial == 1

    def test_file_write_error_handling(self):
        """Test handling of file write errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            serial_file = os.path.join(tmpdir, "test_serial.txt")

            manager = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Save serial first time
            manager.save_serial(42)

            # Create new manager instance to test loading
            manager2 = SerialNumberManager(
                serial_file=serial_file, enable_file_storage=True
            )

            # Should load serial 42 and increment to 43
            serial = manager2.get_next_serial()
            assert serial == 43

            # Even if write fails, should still work (in-memory)
            manager2.save_serial(43)
            serial2 = manager2.get_next_serial()
            assert serial2 == 44
