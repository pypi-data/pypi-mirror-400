"""Tests for the CLI module."""

import argparse
import pytest
from unittest.mock import Mock, patch, MagicMock

from g13_linux.cli import (
    COLOR_PRESETS,
    cmd_run,
    cmd_lcd,
    cmd_color,
    cmd_profile,
    main,
)


class TestColorPresets:
    """Test color preset definitions."""

    def test_has_basic_colors(self):
        assert "red" in COLOR_PRESETS
        assert "green" in COLOR_PRESETS
        assert "blue" in COLOR_PRESETS
        assert "white" in COLOR_PRESETS

    def test_red_is_correct(self):
        assert COLOR_PRESETS["red"] == (255, 0, 0)

    def test_green_is_correct(self):
        assert COLOR_PRESETS["green"] == (0, 255, 0)

    def test_blue_is_correct(self):
        assert COLOR_PRESETS["blue"] == (0, 0, 255)

    def test_off_is_black(self):
        assert COLOR_PRESETS["off"] == (0, 0, 0)

    def test_all_presets_are_rgb_tuples(self):
        for name, color in COLOR_PRESETS.items():
            assert isinstance(color, tuple), f"{name} is not a tuple"
            assert len(color) == 3, f"{name} doesn't have 3 components"
            assert all(0 <= c <= 255 for c in color), f"{name} has invalid values"


class TestCmdRun:
    """Test the run command."""

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.device.read_event")
    @patch("g13_linux.mapper.G13Mapper")
    def test_run_opens_device(self, mock_mapper, mock_read, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_read.side_effect = KeyboardInterrupt()

        args = argparse.Namespace()
        cmd_run(args)

        mock_open.assert_called_once()
        mock_device.close.assert_called_once()

    @patch("g13_linux.device.open_g13")
    def test_run_exits_on_device_error(self, mock_open):
        mock_open.side_effect = Exception("Device not found")

        args = argparse.Namespace()
        with pytest.raises(SystemExit) as exc_info:
            cmd_run(args)
        assert exc_info.value.code == 1


class TestCmdLcd:
    """Test the lcd command."""

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.lcd.G13LCD")
    def test_lcd_clear(self, mock_lcd_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_lcd = Mock()
        mock_lcd_class.return_value = mock_lcd

        args = argparse.Namespace(clear=True, text=[])
        cmd_lcd(args)

        mock_lcd.clear.assert_called_once()
        mock_device.close.assert_called_once()

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.lcd.G13LCD")
    def test_lcd_write_text(self, mock_lcd_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_lcd = Mock()
        mock_lcd_class.return_value = mock_lcd

        args = argparse.Namespace(clear=False, text=["Hello", "World"])
        cmd_lcd(args)

        mock_lcd.clear.assert_called_once()
        mock_lcd.write_text_centered.assert_called_once_with("Hello World")
        mock_device.close.assert_called_once()

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.lcd.G13LCD")
    def test_lcd_no_text_no_clear_exits(self, mock_lcd_class, mock_open):
        mock_open.return_value = Mock()

        args = argparse.Namespace(clear=False, text=[])
        with pytest.raises(SystemExit) as exc_info:
            cmd_lcd(args)
        assert exc_info.value.code == 1

    @patch("g13_linux.device.open_g13")
    def test_lcd_device_error_exits(self, mock_open):
        mock_open.side_effect = Exception("No device")

        args = argparse.Namespace(clear=True, text=[])
        with pytest.raises(SystemExit) as exc_info:
            cmd_lcd(args)
        assert exc_info.value.code == 1


class TestCmdColor:
    """Test the color command."""

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.backlight.G13Backlight")
    def test_color_preset(self, mock_backlight_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_backlight = Mock()
        mock_backlight_class.return_value = mock_backlight

        args = argparse.Namespace(color="red")
        cmd_color(args)

        mock_backlight.set_color.assert_called_once_with(255, 0, 0)
        mock_device.close.assert_called_once()

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.backlight.G13Backlight")
    def test_color_hex_with_hash(self, mock_backlight_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_backlight = Mock()
        mock_backlight_class.return_value = mock_backlight

        args = argparse.Namespace(color="#FF8000")
        cmd_color(args)

        mock_backlight.set_color.assert_called_once_with(255, 128, 0)

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.backlight.G13Backlight")
    def test_color_hex_without_hash(self, mock_backlight_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_backlight = Mock()
        mock_backlight_class.return_value = mock_backlight

        args = argparse.Namespace(color="00FF00")
        cmd_color(args)

        mock_backlight.set_color.assert_called_once_with(0, 255, 0)

    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.backlight.G13Backlight")
    def test_color_rgb_values(self, mock_backlight_class, mock_open):
        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_backlight = Mock()
        mock_backlight_class.return_value = mock_backlight

        args = argparse.Namespace(color="128,64,32")
        cmd_color(args)

        mock_backlight.set_color.assert_called_once_with(128, 64, 32)

    def test_color_invalid_exits(self):
        args = argparse.Namespace(color="notacolor")
        with pytest.raises(SystemExit) as exc_info:
            cmd_color(args)
        assert exc_info.value.code == 1

    def test_color_invalid_rgb_exits(self):
        args = argparse.Namespace(color="1,2")
        with pytest.raises(SystemExit) as exc_info:
            cmd_color(args)
        assert exc_info.value.code == 1

    @patch("g13_linux.device.open_g13")
    def test_color_device_error_exits(self, mock_open):
        mock_open.side_effect = Exception("No device")

        args = argparse.Namespace(color="red")
        with pytest.raises(SystemExit) as exc_info:
            cmd_color(args)
        assert exc_info.value.code == 1


class TestCmdProfile:
    """Test the profile command."""

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_list_empty(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.list_profiles.return_value = []
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="list")
        cmd_profile(args)

        mock_pm.list_profiles.assert_called_once()

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_list_with_profiles(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.list_profiles.return_value = ["default", "gaming"]
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="list")
        cmd_profile(args)

        mock_pm.list_profiles.assert_called_once()

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_show(self, mock_pm_class):
        mock_pm = Mock()
        mock_profile = Mock()
        mock_profile.name = "test"
        mock_profile.description = "Test profile"
        mock_profile.backlight = {"color": "#FF0000"}
        mock_profile.lcd = {"text": "Hello"}
        mock_profile.mappings = {"G1": "KEY_A"}
        mock_pm.load_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="show", name="test")
        cmd_profile(args)

        mock_pm.load_profile.assert_called_once_with("test")

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_show_not_found_exits(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.load_profile.side_effect = FileNotFoundError()
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="show", name="nonexistent")
        with pytest.raises(SystemExit) as exc_info:
            cmd_profile(args)
        assert exc_info.value.code == 1

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_create(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.profile_exists.return_value = False
        mock_profile = Mock()
        mock_pm.create_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="create", name="newprofile")
        cmd_profile(args)

        mock_pm.create_profile.assert_called_once_with("newprofile")
        mock_pm.save_profile.assert_called_once_with(mock_profile)

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_create_exists_exits(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.profile_exists.return_value = True
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="create", name="existing")
        with pytest.raises(SystemExit) as exc_info:
            cmd_profile(args)
        assert exc_info.value.code == 1

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_delete(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="delete", name="oldprofile")
        cmd_profile(args)

        mock_pm.delete_profile.assert_called_once_with("oldprofile")

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    def test_profile_delete_not_found_exits(self, mock_pm_class):
        mock_pm = Mock()
        mock_pm.delete_profile.side_effect = FileNotFoundError()
        mock_pm_class.return_value = mock_pm

        args = argparse.Namespace(profile_cmd="delete", name="nonexistent")
        with pytest.raises(SystemExit) as exc_info:
            cmd_profile(args)
        assert exc_info.value.code == 1

    @patch("g13_linux.gui.models.profile_manager.ProfileManager")
    @patch("g13_linux.device.open_g13")
    @patch("g13_linux.hardware.backlight.G13Backlight")
    def test_profile_load_applies_backlight(self, mock_bl_class, mock_open, mock_pm_class):
        mock_pm = Mock()
        mock_profile = Mock()
        mock_profile.name = "test"
        mock_profile.backlight = {"color": "#FF0000"}
        mock_pm.load_profile.return_value = mock_profile
        mock_pm_class.return_value = mock_pm

        mock_device = Mock()
        mock_open.return_value = mock_device
        mock_backlight = Mock()
        mock_bl_class.return_value = mock_backlight

        args = argparse.Namespace(profile_cmd="load", name="test")
        cmd_profile(args)

        mock_backlight.set_color.assert_called_once_with(255, 0, 0)


class TestMain:
    """Test the main entry point."""

    @patch("g13_linux.cli.cmd_run")
    def test_main_no_args_runs_daemon(self, mock_cmd_run):
        with patch("sys.argv", ["g13-linux"]):
            main()
        mock_cmd_run.assert_called_once()

    @patch("g13_linux.cli.cmd_run")
    def test_main_run_command(self, mock_cmd_run):
        with patch("sys.argv", ["g13-linux", "run"]):
            main()
        mock_cmd_run.assert_called_once()

    @patch("g13_linux.cli.cmd_lcd")
    def test_main_lcd_command(self, mock_cmd_lcd):
        with patch("sys.argv", ["g13-linux", "lcd", "Hello"]):
            main()
        mock_cmd_lcd.assert_called_once()

    @patch("g13_linux.cli.cmd_color")
    def test_main_color_command(self, mock_cmd_color):
        with patch("sys.argv", ["g13-linux", "color", "red"]):
            main()
        mock_cmd_color.assert_called_once()

    @patch("g13_linux.cli.cmd_profile")
    def test_main_profile_list(self, mock_cmd_profile):
        with patch("sys.argv", ["g13-linux", "profile", "list"]):
            main()
        mock_cmd_profile.assert_called_once()

    def test_main_profile_no_subcommand_exits(self):
        with patch("sys.argv", ["g13-linux", "profile"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_version(self):
        with patch("sys.argv", ["g13-linux", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
