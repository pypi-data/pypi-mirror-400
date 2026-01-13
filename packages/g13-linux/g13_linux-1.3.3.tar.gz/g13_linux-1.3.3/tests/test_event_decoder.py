"""Tests for the EventDecoder module."""

import pytest
from g13_linux.gui.models.event_decoder import (
    EventDecoder,
    G13ButtonState,
    analyze_sample_data,
)


class TestG13ButtonState:
    """Tests for G13ButtonState dataclass."""

    def test_creation(self):
        """Test basic creation of G13ButtonState."""
        state = G13ButtonState(
            g_buttons=0b101,
            m_buttons=0b010,
            joystick_x=128,
            joystick_y=128,
            raw_data=b"\x00" * 8,
        )
        assert state.g_buttons == 0b101
        assert state.m_buttons == 0b010
        assert state.joystick_x == 128
        assert state.joystick_y == 128
        assert len(state.raw_data) == 8


class TestEventDecoderInit:
    """Tests for EventDecoder initialization."""

    def test_init(self):
        """Test EventDecoder initialization."""
        decoder = EventDecoder()
        assert decoder.last_state is None

    def test_button_map_exists(self):
        """Test that BUTTON_MAP contains expected buttons."""
        assert "G1" in EventDecoder.BUTTON_MAP
        assert "G22" in EventDecoder.BUTTON_MAP
        assert "M1" in EventDecoder.BUTTON_MAP
        assert "M3" in EventDecoder.BUTTON_MAP
        assert "MR" in EventDecoder.BUTTON_MAP

    def test_joystick_byte_positions(self):
        """Test joystick byte position constants."""
        assert EventDecoder.JOYSTICK_X_BYTE == 1
        assert EventDecoder.JOYSTICK_Y_BYTE == 2


class TestDecodeReport:
    """Tests for decode_report method."""

    def test_decode_empty_report(self):
        """Test decoding minimal valid report."""
        decoder = EventDecoder()
        data = bytes([0x00] * 8)
        state = decoder.decode_report(data)

        assert state.g_buttons == 0
        assert state.m_buttons == 0
        assert state.joystick_x == 0
        assert state.joystick_y == 0

    def test_decode_report_too_short(self):
        """Test that short reports raise ValueError."""
        decoder = EventDecoder()
        with pytest.raises(ValueError, match="Expected at least 8 bytes"):
            decoder.decode_report(bytes([0x00] * 5))

    def test_decode_report_from_list(self):
        """Test decoding from list instead of bytes."""
        decoder = EventDecoder()
        data = [0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00]
        state = decoder.decode_report(data)

        assert state.joystick_x == 0x80
        assert state.joystick_y == 0x80

    def test_decode_g1_pressed(self):
        """Test decoding G1 button press (byte 3, bit 0)."""
        decoder = EventDecoder()
        # Byte 3 = 0x01 means G1 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 1)  # G1 is bit 1

    def test_decode_g8_pressed(self):
        """Test decoding G8 button press (byte 3, bit 7)."""
        decoder = EventDecoder()
        # Byte 3 = 0x80 means G8 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 8)  # G8 is bit 8

    def test_decode_g9_pressed(self):
        """Test decoding G9 button press (byte 4, bit 0)."""
        decoder = EventDecoder()
        # Byte 4 = 0x01 means G9 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x01, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 9)  # G9 is bit 9

    def test_decode_g17_pressed(self):
        """Test decoding G17 button press (byte 5, bit 0)."""
        decoder = EventDecoder()
        # Byte 5 = 0x01 means G17 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x00, 0x01, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 17)  # G17 is bit 17

    def test_decode_g22_pressed(self):
        """Test decoding G22 button press (byte 5, bit 5)."""
        decoder = EventDecoder()
        # Byte 5 = 0x20 means G22 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x00, 0x20, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 22)  # G22 is bit 22

    def test_decode_m1_pressed(self):
        """Test decoding M1 button press (byte 6, bit 5)."""
        decoder = EventDecoder()
        # Byte 6 = 0x20 means M1 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x20, 0x00])
        state = decoder.decode_report(data)

        assert state.m_buttons & (1 << 1)  # M1 is bit 1

    def test_decode_m2_pressed(self):
        """Test decoding M2 button press (byte 6, bit 6)."""
        decoder = EventDecoder()
        # Byte 6 = 0x40 means M2 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x40, 0x00])
        state = decoder.decode_report(data)

        assert state.m_buttons & (1 << 2)  # M2 is bit 2

    def test_decode_m3_pressed(self):
        """Test decoding M3 button press (byte 6, bit 7)."""
        decoder = EventDecoder()
        # Byte 6 = 0x80 means M3 is pressed
        data = bytes([0x00, 0x80, 0x80, 0x00, 0x00, 0x00, 0x80, 0x00])
        state = decoder.decode_report(data)

        assert state.m_buttons & (1 << 3)  # M3 is bit 3

    def test_decode_multiple_buttons(self):
        """Test decoding multiple simultaneous button presses."""
        decoder = EventDecoder()
        # G1 + G9 + M1
        data = bytes([0x00, 0x80, 0x80, 0x01, 0x01, 0x00, 0x20, 0x00])
        state = decoder.decode_report(data)

        assert state.g_buttons & (1 << 1)  # G1
        assert state.g_buttons & (1 << 9)  # G9
        assert state.m_buttons & (1 << 1)  # M1

    def test_decode_joystick_values(self):
        """Test joystick value decoding."""
        decoder = EventDecoder()
        data = bytes([0x00, 0x40, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)

        assert state.joystick_x == 0x40  # 64
        assert state.joystick_y == 0xC0  # 192

    def test_decode_joystick_extremes(self):
        """Test joystick at extreme positions."""
        decoder = EventDecoder()

        # Full left/up (0, 0)
        data = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)
        assert state.joystick_x == 0
        assert state.joystick_y == 0

        # Full right/down (255, 255)
        data = bytes([0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00])
        state = decoder.decode_report(data)
        assert state.joystick_x == 255
        assert state.joystick_y == 255


class TestGetPressedButtons:
    """Tests for get_pressed_buttons method."""

    def test_no_buttons_pressed(self):
        """Test with no buttons pressed."""
        decoder = EventDecoder()
        state = G13ButtonState(
            g_buttons=0,
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )

        assert decoder.get_pressed_buttons(state) == []

    def test_g_buttons_pressed(self):
        """Test with G buttons pressed."""
        decoder = EventDecoder()
        # G1 and G5 pressed
        state = G13ButtonState(
            g_buttons=(1 << 1) | (1 << 5),
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )

        pressed = decoder.get_pressed_buttons(state)
        assert "G1" in pressed
        assert "G5" in pressed
        assert len(pressed) == 2

    def test_m_buttons_pressed(self):
        """Test with M buttons pressed."""
        decoder = EventDecoder()
        # M2 pressed
        state = G13ButtonState(
            g_buttons=0,
            m_buttons=(1 << 2),
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )

        pressed = decoder.get_pressed_buttons(state)
        assert "M2" in pressed
        assert len(pressed) == 1

    def test_other_buttons_from_raw_data(self):
        """Test detecting MR button from raw data."""
        decoder = EventDecoder()
        # MR is at byte 7, bit 0
        raw = bytearray(8)
        raw[7] = 0x01  # MR pressed

        state = G13ButtonState(
            g_buttons=0,
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(raw),
        )

        pressed = decoder.get_pressed_buttons(state)
        assert "MR" in pressed

    def test_uses_last_state_when_none_passed(self):
        """Test that last_state is used when no state passed."""
        decoder = EventDecoder()
        decoder.last_state = G13ButtonState(
            g_buttons=(1 << 3),  # G3
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )

        pressed = decoder.get_pressed_buttons()
        assert "G3" in pressed

    def test_returns_empty_when_no_state(self):
        """Test returns empty list when no state available."""
        decoder = EventDecoder()
        assert decoder.get_pressed_buttons() == []


class TestGetButtonChanges:
    """Tests for get_button_changes method."""

    def test_first_state_all_pressed(self):
        """Test first state reports all buttons as newly pressed."""
        decoder = EventDecoder()
        state = G13ButtonState(
            g_buttons=(1 << 1),  # G1
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )

        pressed, released = decoder.get_button_changes(state)
        assert "G1" in pressed
        assert released == []

    def test_button_press(self):
        """Test detecting new button press."""
        decoder = EventDecoder()

        # Initial state - no buttons
        state1 = G13ButtonState(
            g_buttons=0,
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        decoder.get_button_changes(state1)

        # Press G5
        state2 = G13ButtonState(
            g_buttons=(1 << 5),
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        pressed, released = decoder.get_button_changes(state2)

        assert "G5" in pressed
        assert released == []

    def test_button_release(self):
        """Test detecting button release."""
        decoder = EventDecoder()

        # Initial state - G5 pressed
        state1 = G13ButtonState(
            g_buttons=(1 << 5),
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        decoder.get_button_changes(state1)

        # Release G5
        state2 = G13ButtonState(
            g_buttons=0,
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        pressed, released = decoder.get_button_changes(state2)

        assert pressed == []
        assert "G5" in released

    def test_simultaneous_press_and_release(self):
        """Test press and release happening simultaneously."""
        decoder = EventDecoder()

        # Initial state - G1 pressed
        state1 = G13ButtonState(
            g_buttons=(1 << 1),
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        decoder.get_button_changes(state1)

        # Release G1, press G2
        state2 = G13ButtonState(
            g_buttons=(1 << 2),
            m_buttons=0,
            joystick_x=128,
            joystick_y=128,
            raw_data=bytes(8),
        )
        pressed, released = decoder.get_button_changes(state2)

        assert "G2" in pressed
        assert "G1" in released


class TestAnalyzeRawReport:
    """Tests for analyze_raw_report method."""

    def test_analyze_short_report(self):
        """Test analyzing too-short report."""
        decoder = EventDecoder()
        result = decoder.analyze_raw_report(bytes([0x00] * 5))
        assert "Invalid length" in result

    def test_analyze_valid_report(self):
        """Test analyzing valid report."""
        decoder = EventDecoder()
        data = bytes([0x00, 0x80, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00])
        result = decoder.analyze_raw_report(data)

        assert "USB HID Report Analysis" in result
        assert "8 bytes" in result
        assert "Non-zero bytes" in result

    def test_analyze_all_zeros(self):
        """Test analyzing all-zero report."""
        decoder = EventDecoder()
        data = bytes([0x00] * 8)
        result = decoder.analyze_raw_report(data)

        assert "All bytes are zero" in result

    def test_analyze_64_byte_report(self):
        """Test analyzing full 64-byte report."""
        decoder = EventDecoder()
        data = bytes([0x00] * 64)
        data = bytearray(data)
        data[3] = 0xFF  # Set some non-zero bytes
        data = bytes(data)

        result = decoder.analyze_raw_report(data)
        assert "64 bytes" in result


class TestHelperFunction:
    """Tests for analyze_sample_data helper."""

    def test_helper_function(self, capsys):
        """Test the helper function outputs expected info."""
        sample = bytes([0x00, 0x80, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00])
        analyze_sample_data(sample)

        captured = capsys.readouterr()
        assert "Raw Data Analysis" in captured.out
        assert "Decoded State" in captured.out
        assert "G-buttons bitmask" in captured.out
        assert "Pressed buttons" in captured.out
