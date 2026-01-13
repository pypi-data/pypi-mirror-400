"""Tests for G13 button mapper."""

from unittest.mock import MagicMock, patch
from evdev import ecodes as e


class TestMapperParsing:
    """Test mapping format parsing without hardware."""

    def test_parse_simple_mapping(self):
        """Parse simple KEY_* string format."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping("KEY_A")

            assert keycodes == [e.KEY_A]

    def test_parse_combo_mapping(self):
        """Parse combo format with multiple keys."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping(
                {"keys": ["KEY_LEFTCTRL", "KEY_B"], "label": "Test combo"}
            )

            assert keycodes == [e.KEY_LEFTCTRL, e.KEY_B]

    def test_parse_invalid_key_returns_empty(self):
        """Invalid key names return empty list."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping("KEY_INVALID_NOT_REAL")

            assert keycodes == []

    def test_parse_empty_combo_returns_empty(self):
        """Empty combo returns empty list."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping({"keys": [], "label": "Empty"})

            assert keycodes == []


class TestProfileLoading:
    """Test loading profiles into mapper."""

    def test_load_simple_profile(self):
        """Load profile with simple key mappings."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            profile = {
                "mappings": {
                    "G1": "KEY_1",
                    "G2": "KEY_2",
                }
            }
            mapper.load_profile(profile)

            assert "G1" in mapper.button_map
            assert mapper.button_map["G1"] == [e.KEY_1]
            assert mapper.button_map["G2"] == [e.KEY_2]

    def test_load_combo_profile(self):
        """Load profile with key combinations."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            profile = {
                "mappings": {
                    "G1": {"keys": ["KEY_LEFTCTRL", "KEY_C"], "label": "Copy"},
                    "G2": {"keys": ["KEY_LEFTCTRL", "KEY_V"], "label": "Paste"},
                }
            }
            mapper.load_profile(profile)

            assert mapper.button_map["G1"] == [e.KEY_LEFTCTRL, e.KEY_C]
            assert mapper.button_map["G2"] == [e.KEY_LEFTCTRL, e.KEY_V]

    def test_load_mixed_profile(self):
        """Load profile with both simple and combo mappings."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            profile = {
                "mappings": {
                    "G1": "KEY_F1",
                    "G2": {"keys": ["KEY_LEFTALT", "KEY_F4"], "label": "Close"},
                }
            }
            mapper.load_profile(profile)

            assert mapper.button_map["G1"] == [e.KEY_F1]
            assert mapper.button_map["G2"] == [e.KEY_LEFTALT, e.KEY_F4]


class TestButtonEvents:
    """Test button event handling."""

    def test_button_press_emits_keys(self):
        """Button press emits all keys in order."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G1": [e.KEY_LEFTCTRL, e.KEY_B]}

            mapper.handle_button_event("G1", True)

            # Should write Ctrl, then B, then sync
            calls = mock_uinput.write.call_args_list
            assert len(calls) == 2
            assert calls[0][0] == (e.EV_KEY, e.KEY_LEFTCTRL, 1)
            assert calls[1][0] == (e.EV_KEY, e.KEY_B, 1)
            mock_uinput.syn.assert_called_once()

    def test_button_release_emits_keys_reversed(self):
        """Button release emits keys in reverse order."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G1": [e.KEY_LEFTCTRL, e.KEY_B]}

            mapper.handle_button_event("G1", False)

            # Should release B first, then Ctrl
            calls = mock_uinput.write.call_args_list
            assert len(calls) == 2
            assert calls[0][0] == (e.EV_KEY, e.KEY_B, 0)
            assert calls[1][0] == (e.EV_KEY, e.KEY_LEFTCTRL, 0)

    def test_unmapped_button_does_nothing(self):
        """Unmapped button press does nothing."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {}

            mapper.handle_button_event("G99", True)

            mock_uinput.write.assert_not_called()
            mock_uinput.syn.assert_not_called()


class TestMapperClose:
    """Test mapper cleanup."""

    def test_close_closes_uinput(self):
        """Close properly closes UInput."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.close()

            mock_uinput.close.assert_called_once()


class TestMapperSendKey:
    """Test single key emission."""

    def test_send_key_emits_press_and_release(self):
        """send_key emits press + release + sync."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.send_key(e.KEY_A)

            calls = mock_uinput.write.call_args_list
            assert len(calls) == 2
            assert calls[0][0] == (e.EV_KEY, e.KEY_A, 1)  # Press
            assert calls[1][0] == (e.EV_KEY, e.KEY_A, 0)  # Release
            mock_uinput.syn.assert_called_once()


class TestMapperHandleRawReport:
    """Test raw HID report handling."""

    def test_handle_raw_report_calls_decoder(self):
        """Raw report is passed to EventDecoder."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G1": [e.KEY_1]}

            # Mock decoder to return button press
            with patch.object(mapper.decoder, "decode_report") as mock_decode, \
                 patch.object(mapper.decoder, "get_button_changes") as mock_changes:
                mock_changes.return_value = (["G1"], [])  # G1 pressed

                mapper.handle_raw_report(bytes([0x00] * 8))

                mock_decode.assert_called_once()
                mock_changes.assert_called_once()
                # Should have emitted key press
                mock_uinput.write.assert_called()

    def test_handle_raw_report_button_release(self):
        """Raw report handles button release."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G2": [e.KEY_2]}

            with patch.object(mapper.decoder, "decode_report"), \
                 patch.object(mapper.decoder, "get_button_changes") as mock_changes:
                mock_changes.return_value = ([], ["G2"])  # G2 released

                mapper.handle_raw_report(bytes([0x00] * 8))

                # Should have emitted key release
                calls = mock_uinput.write.call_args_list
                assert any(call[0][2] == 0 for call in calls)  # Release state

    def test_handle_raw_report_invalid_report(self):
        """Invalid report is silently ignored."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()

            with patch.object(mapper.decoder, "decode_report", side_effect=ValueError("bad")):
                # Should not raise
                mapper.handle_raw_report(bytes([0xFF]))

            mock_uinput.write.assert_not_called()

    def test_handle_raw_report_combo_keys(self):
        """Raw report handles combo key mappings."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G3": [e.KEY_LEFTCTRL, e.KEY_C]}

            with patch.object(mapper.decoder, "decode_report"), \
                 patch.object(mapper.decoder, "get_button_changes") as mock_changes:
                mock_changes.return_value = (["G3"], [])

                mapper.handle_raw_report(bytes([0x00] * 8))

                # Should emit both keys
                calls = mock_uinput.write.call_args_list
                assert len(calls) == 2


class TestMapperInit:
    """Test mapper initialization."""

    def test_init_creates_uinput(self):
        """Mapper creates UInput on init."""
        mock_uinput = MagicMock()

        with patch("g13_linux.mapper.UInput", return_value=mock_uinput) as mock_cls:
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()

            mock_cls.assert_called_once()
            assert mapper.ui is mock_uinput

    def test_init_creates_decoder(self):
        """Mapper creates EventDecoder on init."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()

            assert mapper.decoder is not None

    def test_init_empty_button_map(self):
        """Mapper starts with empty button_map."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()

            assert mapper.button_map == {}


class TestMapperEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_mapping_none_type(self):
        """Parsing None returns empty list."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping(None)

            assert keycodes == []

    def test_parse_mapping_int_type(self):
        """Parsing unexpected type returns empty list."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            keycodes = mapper._parse_mapping(123)

            assert keycodes == []

    def test_load_profile_no_mappings_key(self):
        """Profile without mappings key works."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.load_profile({})

            assert mapper.button_map == {}

    def test_load_profile_clears_existing(self):
        """Loading new profile clears existing mappings."""
        with patch("g13_linux.mapper.UInput"):
            from g13_linux.mapper import G13Mapper

            mapper = G13Mapper()
            mapper.button_map = {"G1": [e.KEY_1]}

            mapper.load_profile({"mappings": {}})

            assert mapper.button_map == {}
