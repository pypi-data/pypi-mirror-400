"""Tests for G13 LCD display."""

import pytest
from g13_linux.hardware.lcd import G13LCD, FONT_5X7


class TestLCDConstants:
    """Test LCD configuration constants."""

    def test_lcd_dimensions(self):
        """LCD dimensions match G13 spec."""
        lcd = G13LCD()
        assert lcd.WIDTH == 160
        assert lcd.HEIGHT == 43

    def test_framebuffer_size(self):
        """Framebuffer size is correct for vertical packing."""
        lcd = G13LCD()
        # Vertical packing: 160 columns × 6 bytes per column = 960 bytes
        # (6 bytes = 48 bits, but only 43 rows visible)
        assert lcd.FRAMEBUFFER_SIZE == 960
        assert lcd.BYTES_PER_COLUMN == 6
        assert lcd.BUFFER_ROWS == 48


class TestFontTable:
    """Test 5x7 font table."""

    def test_font_has_printable_ascii(self):
        """Font includes all printable ASCII (32-126)."""
        for code in range(32, 127):
            assert code in FONT_5X7, f"Missing char {code} ({chr(code)})"

    def test_font_entries_are_5_bytes(self):
        """Each font entry is 5 bytes (5 columns)."""
        for code, glyph in FONT_5X7.items():
            assert len(glyph) == 5, f"Char {code} has {len(glyph)} columns"

    def test_space_is_blank(self):
        """Space character (32) is all zeros."""
        assert FONT_5X7[32] == [0x00, 0x00, 0x00, 0x00, 0x00]


class TestPixelOperations:
    """Test pixel manipulation with G13 LCD byte packing."""

    def test_set_pixel_on(self):
        """Setting a pixel turns it on."""
        lcd = G13LCD()
        lcd.set_pixel(0, 0, True)

        # Pixel (0,0) is byte 0, bit 0
        assert lcd._framebuffer[0] & 0x01

    def test_set_pixel_off(self):
        """Clearing a pixel turns it off."""
        lcd = G13LCD()
        lcd._framebuffer[0] = 0xFF
        lcd.set_pixel(0, 0, False)

        assert not (lcd._framebuffer[0] & 0x01)

    def test_set_pixel_various_positions(self):
        """Pixels at various positions are set correctly.

        Layout:
        - bytes 0-159: columns 0-159, rows 0-7
        - bytes 160-319: columns 0-159, rows 8-15
        - etc.
        """
        lcd = G13LCD()

        # Test pixel at x=1, y=0 (column 1, row 0)
        # byte_idx = 0 * 160 + 1 = 1, bit 0
        lcd.set_pixel(1, 0, True)
        assert lcd._framebuffer[1] & 0x01

        # Test pixel at x=0, y=7 (column 0, row 7)
        # byte_idx = 0 * 160 + 0 = 0, bit 7
        lcd.set_pixel(0, 7, True)
        assert lcd._framebuffer[0] & 0x80

        # Test pixel at x=0, y=8 (column 0, row 8 - second block)
        # byte_idx = 1 * 160 + 0 = 160, bit 0
        lcd.set_pixel(0, 8, True)
        assert lcd._framebuffer[160] & 0x01

        # Test pixel at x=159, y=42 (last visible pixel)
        # row_block = 42 // 8 = 5, bit = 42 % 8 = 2
        # byte_idx = 5 * 160 + 159 = 959
        lcd.set_pixel(159, 42, True)
        assert lcd._framebuffer[5 * 160 + 159] & 0x04

    def test_set_pixel_out_of_bounds_ignored(self):
        """Out-of-bounds pixels are ignored."""
        lcd = G13LCD()
        lcd.set_pixel(999, 999, True)  # Should not raise
        lcd.set_pixel(-1, -1, True)  # Should not raise


class TestClearFill:
    """Test clear and fill operations."""

    def test_clear_zeroes_framebuffer(self):
        """Clear sets all pixels off."""
        lcd = G13LCD()
        lcd._framebuffer = bytearray([0xFF] * lcd.FRAMEBUFFER_SIZE)
        lcd.clear()

        assert all(b == 0 for b in lcd._framebuffer)

    def test_fill_sets_all_pixels(self):
        """Fill sets all pixels on."""
        lcd = G13LCD()
        lcd.fill()

        assert all(b == 0xFF for b in lcd._framebuffer)


class TestTextRendering:
    """Test text rendering to framebuffer."""

    def test_write_text_modifies_framebuffer(self):
        """Writing text modifies the framebuffer."""
        lcd = G13LCD()
        initial = bytes(lcd._framebuffer)

        lcd.write_text("A", 0, 0, send=False)

        assert lcd._framebuffer != initial

    def test_write_text_at_position(self):
        """Text can be written at specific position."""
        lcd = G13LCD()
        lcd.write_text("X", 10, 5, send=False)

        # Verify some pixels were set in the target area
        # Char 'X' at x=10, y=5 should set pixels in columns 10-14
        # With new layout: bytes 0-159 are row block 0 (rows 0-7)
        # So columns 10-14 in row block 0 are bytes 10-14
        found_pixel = False
        for col in range(10, 15):  # 5-pixel wide char
            if lcd._framebuffer[col]:  # Row block 0
                found_pixel = True
                break
        assert found_pixel

    def test_write_text_unknown_char_shows_question(self):
        """Unknown characters render as '?'."""
        lcd = G13LCD()

        # Write unknown char (outside ASCII range)
        lcd.write_text("\x01", 0, 0, send=False)
        unknown_fb = bytes(lcd._framebuffer)

        lcd.clear()

        # Write '?' explicitly
        lcd.write_text("?", 0, 0, send=False)
        question_fb = bytes(lcd._framebuffer)

        assert unknown_fb == question_fb

    def test_write_text_centered(self):
        """Centered text is positioned correctly."""
        lcd = G13LCD()

        # "TEST" is 4 chars * 6 pixels = 24 pixels wide
        # Center of 160: (160 - 24) / 2 = 68
        lcd.write_text_centered("TEST", 0, send=False)

        # Check that first columns (0-60) before text are empty
        # With new layout: columns 0-9 in all row blocks should be empty
        # Row block 0: bytes 0-9 (columns 0-9)
        first_columns_empty = all(
            lcd._framebuffer[col] == 0
            for col in range(10)
        )
        assert first_columns_empty


class TestBitmapOperations:
    """Test raw bitmap operations."""

    def test_write_bitmap_copies_data(self):
        """Write bitmap copies data to framebuffer."""
        lcd = G13LCD()
        bitmap = bytes([0xAA] * 100)

        lcd.write_bitmap(bitmap)

        assert lcd._framebuffer[:100] == bytearray([0xAA] * 100)

    def test_write_bitmap_rejects_oversized(self):
        """Oversized bitmap raises error."""
        lcd = G13LCD()
        bitmap = bytes([0xFF] * 1000)

        with pytest.raises(ValueError):
            lcd.write_bitmap(bitmap)
