"""Tests for G13Device wrapper."""

import pytest
from unittest.mock import MagicMock, patch

from g13_linux.gui.models.g13_device import G13Device


class TestG13DeviceInit:
    """Tests for G13Device initialization."""

    def test_init_default(self):
        """Test default initialization."""
        device = G13Device()

        assert device._handle is None
        assert device._is_connected is False
        assert device._use_libusb is False

    def test_init_with_libusb(self):
        """Test initialization with libusb flag."""
        device = G13Device(use_libusb=True)

        assert device._use_libusb is True

    def test_is_connected_initially_false(self):
        """Test is_connected is False initially."""
        device = G13Device()
        assert device.is_connected is False

    def test_handle_initially_none(self):
        """Test handle is None initially."""
        device = G13Device()
        assert device.handle is None


class TestG13DeviceConnect:
    """Tests for connect method."""

    def test_connect_success_hidraw(self, qtbot):
        """Test successful connection via hidraw."""
        device = G13Device(use_libusb=False)

        mock_handle = MagicMock()

        connected = []
        device.device_connected.connect(lambda: connected.append(True))

        with patch(
            "g13_linux.gui.models.g13_device.open_g13", return_value=mock_handle
        ):
            result = device.connect()

        assert result is True
        assert device.is_connected is True
        assert device.handle is mock_handle
        assert len(connected) == 1

    def test_connect_success_libusb(self, qtbot):
        """Test successful connection via libusb."""
        device = G13Device(use_libusb=True)

        mock_handle = MagicMock()

        with patch(
            "g13_linux.gui.models.g13_device.open_g13_libusb", return_value=mock_handle
        ):
            result = device.connect()

        assert result is True
        assert device.is_connected is True

    def test_connect_failure_runtime_error(self, qtbot):
        """Test connection failure with RuntimeError."""
        device = G13Device()

        errors = []
        device.error_occurred.connect(errors.append)

        with patch(
            "g13_linux.gui.models.g13_device.open_g13",
            side_effect=RuntimeError("Device not found"),
        ):
            result = device.connect()

        assert result is False
        assert device.is_connected is False
        assert len(errors) == 1
        assert "Failed to connect" in errors[0]

    def test_connect_failure_exception(self, qtbot):
        """Test connection failure with generic exception."""
        device = G13Device()

        errors = []
        device.error_occurred.connect(errors.append)

        with patch(
            "g13_linux.gui.models.g13_device.open_g13",
            side_effect=Exception("Unknown error"),
        ):
            result = device.connect()

        assert result is False
        assert device.is_connected is False
        assert len(errors) == 1
        assert "Unexpected error" in errors[0]


class TestG13DeviceDisconnect:
    """Tests for disconnect method."""

    def test_disconnect_closes_handle(self, qtbot):
        """Test disconnect closes device handle."""
        device = G13Device()
        mock_handle = MagicMock()
        device._handle = mock_handle
        device._is_connected = True

        disconnected = []
        device.device_disconnected.connect(lambda: disconnected.append(True))

        device.disconnect()

        mock_handle.close.assert_called_once()
        assert device._handle is None
        assert device.is_connected is False
        assert len(disconnected) == 1

    def test_disconnect_when_not_connected(self, qtbot):
        """Test disconnect when not connected."""
        device = G13Device()

        disconnected = []
        device.device_disconnected.connect(lambda: disconnected.append(True))

        device.disconnect()

        assert device._handle is None
        assert len(disconnected) == 1

    def test_disconnect_handles_close_exception(self, qtbot):
        """Test disconnect handles close exception."""
        device = G13Device()
        mock_handle = MagicMock()
        mock_handle.close.side_effect = Exception("Close failed")
        device._handle = mock_handle
        device._is_connected = True

        errors = []
        device.error_occurred.connect(errors.append)

        device.disconnect()

        assert len(errors) == 1
        assert "Error closing device" in errors[0]
        assert device._handle is None


class TestG13DeviceReadEvent:
    """Tests for read_event_once method."""

    def test_read_event_not_connected(self):
        """Test read_event_once when not connected."""
        device = G13Device()

        result = device.read_event_once()

        assert result is None

    def test_read_event_no_handle(self):
        """Test read_event_once with no handle."""
        device = G13Device()
        device._is_connected = True  # Connected but no handle

        result = device.read_event_once()

        assert result is None

    def test_read_event_success(self, qtbot):
        """Test successful event read."""
        device = G13Device()
        device._is_connected = True
        device._handle = MagicMock()

        test_data = bytes([0x00, 0x80, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00])

        events = []
        device.raw_event_received.connect(events.append)

        with patch(
            "g13_linux.gui.models.g13_device.read_event", return_value=test_data
        ):
            result = device.read_event_once()

        assert result == test_data
        assert len(events) == 1
        assert events[0] == test_data

    def test_read_event_no_data(self, qtbot):
        """Test read_event_once with no data available."""
        device = G13Device()
        device._is_connected = True
        device._handle = MagicMock()

        events = []
        device.raw_event_received.connect(events.append)

        with patch("g13_linux.gui.models.g13_device.read_event", return_value=None):
            result = device.read_event_once()

        assert result is None
        assert len(events) == 0

    def test_read_event_exception(self, qtbot):
        """Test read_event_once handles exception."""
        device = G13Device()
        device._is_connected = True
        device._handle = MagicMock()

        errors = []
        device.error_occurred.connect(errors.append)

        with patch(
            "g13_linux.gui.models.g13_device.read_event",
            side_effect=Exception("Read error"),
        ):
            result = device.read_event_once()

        assert result is None
        assert len(errors) == 1
        assert "Error reading event" in errors[0]


class TestG13DeviceCleanup:
    """Tests for cleanup behavior."""

    def test_del_closes_handle(self):
        """Test __del__ closes handle."""
        device = G13Device()
        mock_handle = MagicMock()
        device._handle = mock_handle

        device.__del__()

        mock_handle.close.assert_called_once()
        assert device._handle is None
        assert device._is_connected is False

    def test_del_handles_exception(self):
        """Test __del__ handles close exception silently."""
        device = G13Device()
        mock_handle = MagicMock()
        mock_handle.close.side_effect = Exception("Close failed")
        device._handle = mock_handle

        # Should not raise
        device.__del__()

        assert device._handle is None

    def test_del_with_no_handle(self):
        """Test __del__ with no handle is safe."""
        device = G13Device()

        # Should not raise
        device.__del__()


class TestG13DeviceProperties:
    """Tests for property getters."""

    def test_is_connected_true(self):
        """Test is_connected returns True when connected."""
        device = G13Device()
        device._is_connected = True

        assert device.is_connected is True

    def test_is_connected_false(self):
        """Test is_connected returns False when not connected."""
        device = G13Device()
        device._is_connected = False

        assert device.is_connected is False

    def test_handle_returns_internal_handle(self):
        """Test handle property returns internal handle."""
        device = G13Device()
        mock_handle = MagicMock()
        device._handle = mock_handle

        assert device.handle is mock_handle
