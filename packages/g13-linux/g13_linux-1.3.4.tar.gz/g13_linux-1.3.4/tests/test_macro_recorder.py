"""Tests for MacroRecorder."""

import pytest
from unittest.mock import MagicMock, patch

from g13_linux.gui.models.macro_recorder import MacroRecorder, RecorderState
from g13_linux.gui.models.macro_types import InputSource, MacroStepType


class TestRecorderState:
    """Tests for RecorderState enum."""

    def test_idle(self):
        """Test IDLE state value."""
        assert RecorderState.IDLE.value == "idle"

    def test_waiting(self):
        """Test WAITING state value."""
        assert RecorderState.WAITING.value == "waiting"

    def test_recording(self):
        """Test RECORDING state value."""
        assert RecorderState.RECORDING.value == "recording"

    def test_saving(self):
        """Test SAVING state value."""
        assert RecorderState.SAVING.value == "saving"


class TestMacroRecorderInit:
    """Tests for MacroRecorder initialization."""

    def test_init(self):
        """Test recorder initialization."""
        recorder = MacroRecorder()

        assert recorder.state == RecorderState.IDLE
        assert recorder.is_recording is False
        assert recorder.step_count == 0

    def test_state_property(self):
        """Test state property."""
        recorder = MacroRecorder()
        assert recorder.state == RecorderState.IDLE

    def test_is_recording_idle(self):
        """Test is_recording when idle."""
        recorder = MacroRecorder()
        assert recorder.is_recording is False

    def test_is_recording_waiting(self):
        """Test is_recording when waiting."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        assert recorder.is_recording is True

    def test_is_recording_recording(self):
        """Test is_recording when recording."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        assert recorder.is_recording is True

    def test_step_count_empty(self):
        """Test step_count with no steps."""
        recorder = MacroRecorder()
        assert recorder.step_count == 0

    def test_elapsed_ms_not_started(self):
        """Test elapsed_ms when timer not started."""
        recorder = MacroRecorder()
        assert recorder.elapsed_ms == 0


class TestMacroRecorderStartRecording:
    """Tests for start_recording method."""

    def test_start_recording_changes_state(self, qtbot):
        """Test start_recording changes to WAITING."""
        recorder = MacroRecorder()

        states = []
        recorder.state_changed.connect(states.append)

        recorder.start_recording()

        assert recorder.state == RecorderState.WAITING
        assert states == [RecorderState.WAITING]

    def test_start_recording_clears_steps(self, qtbot):
        """Test start_recording clears previous steps."""
        recorder = MacroRecorder()
        recorder._steps = [MagicMock()]

        recorder.start_recording()

        assert recorder._steps == []

    def test_start_recording_with_g13_only(self, qtbot):
        """Test start_recording with G13_ONLY source."""
        recorder = MacroRecorder()

        recorder.start_recording(InputSource.G13_ONLY)

        assert recorder._input_source == InputSource.G13_ONLY

    def test_start_recording_while_recording_emits_error(self, qtbot):
        """Test start_recording while already recording emits error."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING

        errors = []
        recorder.error_occurred.connect(errors.append)

        recorder.start_recording()

        assert len(errors) == 1
        assert "Already recording" in errors[0]

    def test_start_recording_starts_system_listener(self, qtbot):
        """Test start_recording with BOTH starts system listener."""
        recorder = MacroRecorder()

        with patch.object(recorder, "_start_system_listener") as mock_start:
            recorder.start_recording(InputSource.BOTH)
            mock_start.assert_called_once()

    def test_start_recording_g13_only_no_system_listener(self, qtbot):
        """Test start_recording with G13_ONLY doesn't start system listener."""
        recorder = MacroRecorder()

        with patch.object(recorder, "_start_system_listener") as mock_start:
            recorder.start_recording(InputSource.G13_ONLY)
            mock_start.assert_not_called()


class TestMacroRecorderStopRecording:
    """Tests for stop_recording method."""

    def test_stop_recording_when_idle(self):
        """Test stop_recording when idle returns None."""
        recorder = MacroRecorder()

        result = recorder.stop_recording()

        assert result is None

    def test_stop_recording_with_no_steps(self, qtbot):
        """Test stop_recording with no steps returns None."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING

        result = recorder.stop_recording()

        assert result is None
        assert recorder.state == RecorderState.IDLE

    def test_stop_recording_returns_macro(self, qtbot):
        """Test stop_recording returns macro with steps."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING

        # Simulate some recorded steps
        from g13_linux.gui.models.macro_types import MacroStep

        recorder._steps = [
            MacroStep(step_type=MacroStepType.KEY_PRESS, value="KEY_A"),
            MacroStep(step_type=MacroStepType.KEY_RELEASE, value="KEY_A"),
        ]

        result = recorder.stop_recording()

        assert result is not None
        assert len(result.steps) == 2
        assert recorder.state == RecorderState.IDLE

    def test_stop_recording_emits_complete(self, qtbot):
        """Test stop_recording emits recording_complete signal."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING

        from g13_linux.gui.models.macro_types import MacroStep

        recorder._steps = [
            MacroStep(step_type=MacroStepType.KEY_PRESS, value="KEY_A"),
        ]

        macros = []
        recorder.recording_complete.connect(macros.append)

        recorder.stop_recording()

        assert len(macros) == 1

    def test_stop_recording_stops_system_listener(self, qtbot):
        """Test stop_recording stops system listener."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._system_listener = MagicMock()

        with patch.object(recorder, "_stop_system_listener") as mock_stop:
            recorder.stop_recording()
            mock_stop.assert_called_once()

    def test_stop_recording_generates_release_events(self, qtbot):
        """Test stop_recording generates release for held keys."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._pressed_keys = {"G13:G5"}

        from g13_linux.gui.models.macro_types import MacroStep

        recorder._steps = [
            MacroStep(step_type=MacroStepType.G13_BUTTON, value="G5", is_press=True),
        ]

        result = recorder.stop_recording()

        # Should have original press + generated release
        assert len(result.steps) == 2
        assert result.steps[1].is_press is False


class TestMacroRecorderCancel:
    """Tests for cancel method."""

    def test_cancel_clears_state(self, qtbot):
        """Test cancel clears state."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._steps = [MagicMock()]
        recorder._pressed_keys = {"KEY:A"}

        recorder.cancel()

        assert recorder.state == RecorderState.IDLE
        assert recorder._steps == []
        assert recorder._pressed_keys == set()

    def test_cancel_stops_system_listener(self, qtbot):
        """Test cancel stops system listener."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._system_listener = MagicMock()

        with patch.object(recorder, "_stop_system_listener") as mock_stop:
            recorder.cancel()
            mock_stop.assert_called_once()

    def test_cancel_emits_state_changed(self, qtbot):
        """Test cancel emits state_changed."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING

        states = []
        recorder.state_changed.connect(states.append)

        recorder.cancel()

        assert RecorderState.IDLE in states


class TestMacroRecorderG13ButtonEvent:
    """Tests for on_g13_button_event method."""

    def test_g13_event_when_idle_ignored(self, qtbot):
        """Test G13 events are ignored when idle."""
        recorder = MacroRecorder()

        recorder.on_g13_button_event("G5", True)

        assert recorder.step_count == 0

    def test_g13_event_with_system_only_ignored(self, qtbot):
        """Test G13 events are ignored with SYSTEM_ONLY source."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        recorder._input_source = InputSource.SYSTEM_ONLY

        recorder.on_g13_button_event("G5", True)

        assert recorder.step_count == 0

    def test_g13_event_mr_button_ignored(self, qtbot):
        """Test MR button is ignored (it's the record trigger)."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        recorder._input_source = InputSource.G13_ONLY

        recorder.on_g13_button_event("MR", True)

        assert recorder.step_count == 0

    def test_g13_event_starts_recording(self, qtbot):
        """Test first G13 event starts recording."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        recorder._input_source = InputSource.G13_ONLY

        recorder.on_g13_button_event("G5", True)

        assert recorder.state == RecorderState.RECORDING
        assert recorder.step_count == 1

    def test_g13_event_records_step(self, qtbot):
        """Test G13 event records correct step."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._input_source = InputSource.G13_ONLY
        recorder._timer.start()

        steps = []
        recorder.step_recorded.connect(steps.append)

        recorder.on_g13_button_event("G10", True)

        assert len(steps) == 1
        assert steps[0].step_type == MacroStepType.G13_BUTTON
        assert steps[0].value == "G10"
        assert steps[0].is_press is True

    def test_g13_event_tracks_pressed(self, qtbot):
        """Test G13 event tracks pressed buttons."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._input_source = InputSource.G13_ONLY
        recorder._timer.start()

        recorder.on_g13_button_event("G5", True)
        assert "G13:G5" in recorder._pressed_keys

        recorder.on_g13_button_event("G5", False)
        assert "G13:G5" not in recorder._pressed_keys


class TestMacroRecorderSystemKeyEvent:
    """Tests for on_system_key_event method."""

    def test_system_event_when_idle_ignored(self, qtbot):
        """Test system events are ignored when idle."""
        recorder = MacroRecorder()

        recorder.on_system_key_event("KEY_A", True)

        assert recorder.step_count == 0

    def test_system_event_with_g13_only_ignored(self, qtbot):
        """Test system events are ignored with G13_ONLY source."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        recorder._input_source = InputSource.G13_ONLY

        recorder.on_system_key_event("KEY_A", True)

        assert recorder.step_count == 0

    def test_system_event_starts_recording(self, qtbot):
        """Test first system event starts recording."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING
        recorder._input_source = InputSource.SYSTEM_ONLY

        recorder.on_system_key_event("KEY_A", True)

        assert recorder.state == RecorderState.RECORDING
        assert recorder.step_count == 1

    def test_system_event_records_press(self, qtbot):
        """Test system key press records correct step."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._input_source = InputSource.BOTH
        recorder._timer.start()

        steps = []
        recorder.step_recorded.connect(steps.append)

        recorder.on_system_key_event("KEY_SPACE", True)

        assert len(steps) == 1
        assert steps[0].step_type == MacroStepType.KEY_PRESS
        assert steps[0].value == "KEY_SPACE"

    def test_system_event_records_release(self, qtbot):
        """Test system key release records correct step."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._input_source = InputSource.BOTH
        recorder._timer.start()

        steps = []
        recorder.step_recorded.connect(steps.append)

        recorder.on_system_key_event("KEY_B", False)

        assert len(steps) == 1
        assert steps[0].step_type == MacroStepType.KEY_RELEASE

    def test_system_event_tracks_pressed(self, qtbot):
        """Test system event tracks pressed keys."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._input_source = InputSource.BOTH
        recorder._timer.start()

        recorder.on_system_key_event("KEY_X", True)
        assert "KEY:KEY_X" in recorder._pressed_keys

        recorder.on_system_key_event("KEY_X", False)
        assert "KEY:KEY_X" not in recorder._pressed_keys


class TestMacroRecorderAddDelay:
    """Tests for add_delay method."""

    def test_add_delay_when_not_recording_ignored(self, qtbot):
        """Test add_delay is ignored when not recording."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.WAITING

        recorder.add_delay(500)

        assert recorder.step_count == 0

    def test_add_delay_records_step(self, qtbot):
        """Test add_delay records delay step."""
        recorder = MacroRecorder()
        recorder._state = RecorderState.RECORDING
        recorder._timer.start()

        steps = []
        recorder.step_recorded.connect(steps.append)

        recorder.add_delay(1000)

        assert len(steps) == 1
        assert steps[0].step_type == MacroStepType.DELAY
        assert steps[0].value == 1000


class TestMacroRecorderGenerateReleaseEvents:
    """Tests for _generate_release_events method."""

    def test_generate_release_no_pressed_keys(self, qtbot):
        """Test no release events when no pressed keys."""
        recorder = MacroRecorder()
        recorder._pressed_keys = set()
        initial_count = len(recorder._steps)

        recorder._generate_release_events()

        assert len(recorder._steps) == initial_count

    def test_generate_release_for_g13_buttons(self, qtbot):
        """Test release events for G13 buttons."""
        recorder = MacroRecorder()
        recorder._pressed_keys = {"G13:G5", "G13:G10"}
        recorder._timer.start()

        recorder._generate_release_events()

        assert len(recorder._steps) == 2
        for step in recorder._steps:
            assert step.step_type == MacroStepType.G13_BUTTON
            assert step.is_press is False

    def test_generate_release_for_system_keys(self, qtbot):
        """Test release events for system keys."""
        recorder = MacroRecorder()
        recorder._pressed_keys = {"KEY:KEY_A", "KEY:KEY_B"}
        recorder._timer.start()

        recorder._generate_release_events()

        assert len(recorder._steps) == 2
        for step in recorder._steps:
            assert step.step_type == MacroStepType.KEY_RELEASE
            assert step.is_press is False


class TestMacroRecorderSystemListener:
    """Tests for system listener methods."""

    def test_stop_system_listener_when_none(self, qtbot):
        """Test stop when no listener is safe."""
        recorder = MacroRecorder()
        recorder._system_listener = None

        # Should not raise
        recorder._stop_system_listener()

    def test_stop_system_listener_stops_and_clears(self, qtbot):
        """Test stop stops listener and clears reference."""
        recorder = MacroRecorder()
        mock_listener = MagicMock()
        recorder._system_listener = mock_listener

        recorder._stop_system_listener()

        mock_listener.stop.assert_called_once()
        assert recorder._system_listener is None

    def test_start_system_listener_without_pynput(self, qtbot):
        """Test start emits error when pynput not available."""
        recorder = MacroRecorder()

        errors = []
        recorder.error_occurred.connect(errors.append)

        with patch.dict("sys.modules", {"pynput": None}):
            with patch(
                "g13_linux.gui.models.macro_recorder.MacroRecorder._start_system_listener",
                wraps=recorder._start_system_listener,
            ):
                # Force ImportError
                original = recorder._start_system_listener

                def mock_start():
                    try:
                        raise ImportError("No pynput")
                    except ImportError:
                        recorder.error_occurred.emit(
                            "pynput not installed - system keyboard capture disabled"
                        )

                recorder._start_system_listener = mock_start
                recorder._start_system_listener()

        assert len(errors) == 1
        assert "pynput not installed" in errors[0]
