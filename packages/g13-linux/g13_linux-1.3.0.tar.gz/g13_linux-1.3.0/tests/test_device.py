"""Tests for the device module."""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os

from g13_linux.device import (
    G13_VENDOR_ID,
    G13_PRODUCT_ID,
    _hidiocsfeature,
    _hidiocgfeature,
    HidrawDevice,
    find_g13_hidraw,
    open_g13,
    read_event,
    LibUSBDevice,
    open_g13_libusb,
)


class TestConstants:
    """Test device constants."""

    def test_vendor_id(self):
        assert G13_VENDOR_ID == 0x046D

    def test_product_id(self):
        assert G13_PRODUCT_ID == 0xC21C


class TestIoctlHelpers:
    """Test ioctl helper functions."""

    def test_hidiocsfeature(self):
        # Test that the ioctl code is computed correctly
        result = _hidiocsfeature(5)
        assert isinstance(result, int)
        # Should have length encoded in upper bits
        assert result & 0xFF0000 == 0x050000

    def test_hidiocgfeature(self):
        result = _hidiocgfeature(8)
        assert isinstance(result, int)
        assert result & 0xFF0000 == 0x080000


class TestHidrawDevice:
    """Test HidrawDevice class."""

    def test_init(self):
        device = HidrawDevice("/dev/hidraw0")
        assert device.path == "/dev/hidraw0"
        assert device._fd is None
        assert device._file is None

    @patch("builtins.open", mock_open())
    @patch("os.set_blocking")
    def test_open(self, mock_set_blocking):
        device = HidrawDevice("/dev/hidraw0")
        device.open()
        assert device._file is not None
        mock_set_blocking.assert_called_once()

    def test_read_returns_data(self):
        device = HidrawDevice("/dev/hidraw0")
        device._file = Mock()
        device._file.read.return_value = b"\x01\x02\x03"

        result = device.read(64)
        assert result == [1, 2, 3]

    def test_read_returns_none_on_empty(self):
        device = HidrawDevice("/dev/hidraw0")
        device._file = Mock()
        device._file.read.return_value = b""

        result = device.read(64)
        assert result is None

    def test_read_returns_none_on_blocking(self):
        device = HidrawDevice("/dev/hidraw0")
        device._file = Mock()
        device._file.read.side_effect = BlockingIOError()

        result = device.read(64)
        assert result is None

    def test_write(self):
        device = HidrawDevice("/dev/hidraw0")
        device._file = Mock()
        device._file.write.return_value = 5

        result = device.write([0x01, 0x02, 0x03, 0x04, 0x05])
        assert result == 5
        device._file.write.assert_called_once_with(b"\x01\x02\x03\x04\x05")

    @patch("fcntl.ioctl")
    def test_send_feature_report(self, mock_ioctl):
        device = HidrawDevice("/dev/hidraw0")
        device._fd = 3
        mock_ioctl.return_value = 5

        result = device.send_feature_report([0x07, 0xFF, 0x00, 0x00, 0x00])
        assert result == 5
        mock_ioctl.assert_called_once()

    def test_send_feature_report_not_open(self):
        device = HidrawDevice("/dev/hidraw0")
        with pytest.raises(RuntimeError, match="Device not open"):
            device.send_feature_report([0x07, 0xFF, 0x00, 0x00, 0x00])

    @patch("fcntl.ioctl")
    def test_get_feature_report(self, mock_ioctl):
        device = HidrawDevice("/dev/hidraw0")
        device._fd = 3

        result = device.get_feature_report(0x07, 5)
        assert isinstance(result, bytes)
        mock_ioctl.assert_called_once()

    def test_get_feature_report_not_open(self):
        device = HidrawDevice("/dev/hidraw0")
        with pytest.raises(RuntimeError, match="Device not open"):
            device.get_feature_report(0x07, 5)

    def test_close(self):
        device = HidrawDevice("/dev/hidraw0")
        mock_file = Mock()
        device._file = mock_file
        device._fd = 3

        device.close()
        mock_file.close.assert_called_once()
        assert device._file is None
        assert device._fd is None

    def test_close_when_not_open(self):
        device = HidrawDevice("/dev/hidraw0")
        device.close()  # Should not raise


class TestFindG13Hidraw:
    """Test find_g13_hidraw function."""

    @patch("glob.glob")
    def test_find_no_devices(self, mock_glob):
        mock_glob.return_value = []
        result = find_g13_hidraw()
        assert result is None

    @patch("glob.glob")
    @patch("builtins.open", mock_open(read_data="HID_ID=0003:0000046D:0000C21C\n"))
    def test_find_g13_found(self, mock_glob):
        mock_glob.return_value = ["/sys/class/hidraw/hidraw3"]
        result = find_g13_hidraw()
        assert result == "/dev/hidraw3"

    @patch("glob.glob")
    @patch("builtins.open", mock_open(read_data="HID_ID=0003:00001234:00005678\n"))
    def test_find_g13_wrong_device(self, mock_glob):
        mock_glob.return_value = ["/sys/class/hidraw/hidraw0"]
        result = find_g13_hidraw()
        assert result is None

    @patch("glob.glob")
    def test_find_g13_io_error(self, mock_glob):
        mock_glob.return_value = ["/sys/class/hidraw/hidraw0"]
        with patch("builtins.open", side_effect=IOError()):
            result = find_g13_hidraw()
        assert result is None


class TestOpenG13:
    """Test open_g13 function."""

    @patch("g13_linux.device.find_g13_hidraw")
    def test_open_g13_not_found(self, mock_find):
        mock_find.return_value = None
        with pytest.raises(RuntimeError, match="not found"):
            open_g13()

    @patch("g13_linux.device.find_g13_hidraw")
    @patch("g13_linux.device.HidrawDevice")
    def test_open_g13_success(self, mock_device_class, mock_find):
        mock_find.return_value = "/dev/hidraw3"
        mock_device = Mock()
        mock_device_class.return_value = mock_device

        result = open_g13()
        assert result == mock_device
        mock_device.open.assert_called_once()


class TestReadEvent:
    """Test read_event function."""

    def test_read_event_with_data(self):
        handle = Mock()
        handle.read.return_value = [0x01, 0x02, 0x03]

        result = read_event(handle)
        assert result == [0x01, 0x02, 0x03]

    def test_read_event_no_data(self):
        handle = Mock()
        handle.read.return_value = None

        result = read_event(handle)
        assert result is None


class TestLibUSBDevice:
    """Test LibUSBDevice class."""

    def test_init(self):
        device = LibUSBDevice()
        assert device._dev is None
        assert device._reattach is False

    def test_open_no_pyusb(self):
        device = LibUSBDevice()
        with patch.dict("sys.modules", {"usb.core": None, "usb.util": None}):
            with pytest.raises((RuntimeError, ImportError)):
                device.open()

    @patch("usb.core.find")
    def test_open_device_not_found(self, mock_find):
        mock_find.return_value = None
        device = LibUSBDevice()
        with pytest.raises(RuntimeError, match="not found"):
            device.open()

    def test_read_no_data(self):
        device = LibUSBDevice()
        device._ep_in = Mock()
        device._ep_in.read.side_effect = Exception("timeout")

        result = device.read(100)
        assert result is None

    def test_read_with_data(self):
        device = LibUSBDevice()
        device._ep_in = Mock()
        device._ep_in.read.return_value = [0x01, 0x02, 0x03]

        result = device.read(100)
        assert result == [0x01, 0x02, 0x03]

    def test_write(self):
        device = LibUSBDevice()
        device._dev = Mock()
        device._dev.write.return_value = 5

        result = device.write([0x01, 0x02, 0x03])
        assert result == 5

    def test_send_feature_report(self):
        device = LibUSBDevice()
        device._dev = Mock()
        device._dev.ctrl_transfer.return_value = 5

        result = device.send_feature_report([0x07, 0xFF, 0x00, 0x00, 0x00])
        assert result == 5

    def test_close(self):
        device = LibUSBDevice()
        device._dev = Mock()
        device._reattach = False

        with patch("usb.util.release_interface"):
            device.close()
        assert device._dev is None

    def test_close_with_reattach(self):
        device = LibUSBDevice()
        device._dev = Mock()
        device._reattach = True

        with patch("usb.util.release_interface"):
            device.close()
        assert device._dev is None


class TestOpenG13Libusb:
    """Test open_g13_libusb function."""

    @patch("g13_linux.device.LibUSBDevice")
    def test_open_g13_libusb(self, mock_device_class):
        mock_device = Mock()
        mock_device_class.return_value = mock_device

        result = open_g13_libusb()
        assert result == mock_device
        mock_device.open.assert_called_once()
