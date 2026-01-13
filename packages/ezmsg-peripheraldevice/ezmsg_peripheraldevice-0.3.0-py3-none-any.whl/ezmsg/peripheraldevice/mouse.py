"""Mouse input via pynput."""

import queue
import threading
import time
import time as time_module
from collections import deque

import ezmsg.core as ez
import numpy as np
from ezmsg.baseproc import (
    BaseClockDrivenProducer,
    BaseClockDrivenUnit,
    BaseProducerUnit,
    BaseStatefulProducer,
    ClockDrivenSettings,
    ClockDrivenState,
    processor_state,
)
from ezmsg.util.messages.axisarray import AxisArray, replace
from pynput.mouse import Controller, Listener

# =============================================================================
# Polled Mouse Producer (takes LinearAxis from Clock)
# =============================================================================


class MousePollerSettings(ClockDrivenSettings):
    """Settings for MousePollerProducer."""

    fs: float = 60.0
    """
    Output sample rate in Hz (only used when n_time is None).

    When n_time is specified, the effective poll rate is derived from the clock:
    poll_rate = n_time / clock.gain (i.e., n_time samples per tick).

    When n_time is None, fs determines both the poll rate and output sample rate,
    with n_samples = fs * clock.gain per tick.
    """

    n_time: int | None = None
    """
    Samples per block.
    - If specified: fixed chunk size, poll rate derived from clock timing
    - If None: derived from fs * clock.gain, poll rate is fs
    """


@processor_state
class MousePollerState(ClockDrivenState):
    """State for MousePollerProducer."""

    controller: Controller | None = None
    template: AxisArray | None = None

    # Background polling state
    poll_thread: threading.Thread | None = None
    poll_buffer: deque | None = None
    stop_event: threading.Event | None = None
    last_position: tuple[float, float] = (0.0, 0.0)
    use_thread: bool = False
    poll_rate: float = 0.0


class MousePollerProducer(BaseClockDrivenProducer[MousePollerSettings, MousePollerState]):
    """
    Reads mouse position, optionally with high-rate background polling.

    Takes LinearAxis input (from Clock) and outputs mouse positions.

    Behavior depends on settings:

    **Fixed chunk mode (n_time is set):**
    - Each tick produces exactly n_time samples
    - Poll rate = n_time * clock_rate (derived from clock timing)
    - settings.fs is ignored
    - Thread used when n_time > 1

    **Variable chunk mode (n_time is None):**
    - Each tick produces fs * clock.gain samples (with fractional tracking)
    - Poll rate = fs (from settings)
    - Thread used when fs != clock_rate

    Input: LinearAxis (from Clock - provides timing info)
    Output: AxisArray with shape (n_samples, 2) - x, y channels
    """

    def _hash_message(self, message: AxisArray.LinearAxis) -> int:
        """
        Hash based on clock gain to detect rate changes.

        Returns different hash when clock rate changes significantly,
        triggering state reset and potential thread restart.
        """
        # Quantize gain to avoid floating point noise triggering resets
        quantized_gain = round(message.gain * 1e6)
        return hash(quantized_gain)

    def _reset_state(self, time_axis: AxisArray.LinearAxis) -> None:
        """Initialize mouse controller and optionally start polling thread."""
        # Stop any existing polling thread
        self._stop_poll_thread()

        self._state.controller = Controller()
        self._state.last_position = self._state.controller.position

        clock_rate = 1.0 / time_axis.gain if time_axis.gain > 0 else float("inf")

        if self.settings.n_time is not None:
            # Fixed chunk mode: poll rate derived from clock timing
            # Need n_time samples per tick, so poll at n_time * clock_rate
            self._state.poll_rate = self.settings.n_time * clock_rate
            need_thread = self.settings.n_time > 1
        else:
            # Variable chunk mode: poll rate is fs from settings
            # n_samples = fs * clock.gain (handled by base class)
            self._state.poll_rate = self.settings.fs
            # Need thread if fs != clock_rate (meaning n_samples != 1)
            need_thread = not np.isclose(self.settings.fs, clock_rate, rtol=0.01)

        self._state.use_thread = need_thread

        if self._state.use_thread:
            # Start background polling thread
            buffer_size = max(int(self._state.poll_rate * 10), 1000)
            self._state.poll_buffer = deque(maxlen=buffer_size)
            self._state.stop_event = threading.Event()
            self._state.poll_thread = threading.Thread(
                target=self._poll_loop,
                daemon=True,
            )
            self._state.poll_thread.start()

        # Pre-construct template AxisArray (shape will be updated in _produce)
        n_time_for_template = self.settings.n_time if self.settings.n_time is not None else 1
        self._state.template = AxisArray(
            data=np.zeros((n_time_for_template, 2), dtype=np.float64),
            dims=["time", "ch"],
            axes={
                "time": time_axis,
                "ch": AxisArray.CoordinateAxis(
                    data=np.array(["x", "y"]),
                    dims=["ch"],
                ),
            },
            key="mouse",
        )

    def _poll_loop(self) -> None:
        """Background thread that polls mouse at poll_rate."""
        interval = 1.0 / self._state.poll_rate
        last_poll = time_module.perf_counter() - interval

        while not self._state.stop_event.is_set():
            sleep_time = (last_poll + interval) - time_module.perf_counter()
            if sleep_time > 0:
                time_module.sleep(sleep_time)
            pos = self._state.controller.position
            self._state.poll_buffer.append(pos)
            self._state.last_position = pos
            last_poll = time_module.perf_counter()

    def _stop_poll_thread(self) -> None:
        """Stop the background polling thread if running."""
        if self._state.stop_event is not None:
            self._state.stop_event.set()
        if self._state.poll_thread is not None:
            self._state.poll_thread.join(timeout=1.0)
            self._state.poll_thread = None
        self._state.stop_event = None
        self._state.poll_buffer = None

    def _produce(self, n_samples: int, time_axis: AxisArray.LinearAxis) -> AxisArray:
        """Generate mouse position data."""
        if self._state.use_thread and self._state.poll_buffer is not None:
            # Get samples from buffer
            positions = []
            for _ in range(n_samples):
                if self._state.poll_buffer:
                    pos = self._state.poll_buffer.popleft()
                    self._state.last_position = pos
                else:
                    # Buffer empty - hold last known position
                    pos = self._state.last_position
                positions.append([pos[0], pos[1]])
            data = np.array(positions, dtype=np.float64)
        else:
            # Simple single-poll mode
            pos = self._state.controller.position
            data = np.array([[pos[0], pos[1]]], dtype=np.float64)

        return replace(
            self._state.template,
            data=data,
            axes={**self._state.template.axes, "time": time_axis},
        )

    def __del__(self) -> None:
        """Stop polling thread on destruction."""
        if hasattr(self, "_state"):
            self._stop_poll_thread()


class MousePoller(BaseClockDrivenUnit[MousePollerSettings, MousePollerProducer]):
    """
    Unit for reading mouse position from Clock input.

    Receives LinearAxis from Clock and outputs mouse positions.
    Supports both simple polling (one sample per tick) and high-rate
    background polling with buffering.
    """

    SETTINGS = MousePollerSettings


# =============================================================================
# Event-driven Mouse Listener Producer
# =============================================================================


class MouseListenerSettings(ez.Settings):
    """Settings for MouseListenerProducer."""

    pass


@processor_state
class MouseListenerState:
    """State for MouseListenerProducer."""

    listener: Listener | None = None
    event_queue: queue.Queue | None = None
    template: AxisArray | None = None


class MouseListenerProducer(BaseStatefulProducer[MouseListenerSettings, AxisArray, MouseListenerState]):
    """
    Produces mouse position events as they occur.

    Uses pynput.mouse.Listener to capture mouse move events with timestamps.
    Events are queued and emitted as AxisArray messages with irregular
    CoordinateAxis timestamps.

    Output: AxisArray with shape (n_events, 2) where n_events varies,
            time axis is CoordinateAxis with actual event timestamps.
    """

    def _reset_state(self) -> None:
        """Initialize listener and queue."""
        self._state.event_queue = queue.Queue()

        def on_move(x: int, y: int) -> None:
            """Callback for mouse movement events."""
            print(f"on_move called: ({x}, {y})")  # DEBUG
            self._state.event_queue.put((x, y, time.monotonic()))

        # def on_click(x, y, button, pressed):
        #     print(f"{'Pressed' if pressed else 'Released'} at {(x, y)}")
        #     if not pressed:
        #         # Stop listener
        #         return False

        self._state.listener = Listener(
            on_move=on_move,
            # on_click=on_click
        )
        self._state.listener.start()

        # Check if process is trusted for input monitoring (macOS)
        if hasattr(Listener, "IS_TRUSTED"):
            if not Listener.IS_TRUSTED:
                import warnings

                warnings.warn(
                    "Process is not trusted for input monitoring. "
                    "On macOS, add your terminal to Accessibility clients: "
                    "System Settings > Privacy & Security > Accessibility. "
                    "Then fully restart your terminal (Cmd+Q).",
                    RuntimeWarning,
                    stacklevel=2,
                )

        # Pre-construct template AxisArray
        self._state.template = AxisArray(
            data=np.zeros((0, 2), dtype=np.float64),
            dims=["time", "ch"],
            axes={
                "time": AxisArray.CoordinateAxis(
                    data=np.array([], dtype=np.float64),
                    dims=["time"],
                    unit="s",
                ),
                "ch": AxisArray.CoordinateAxis(
                    data=np.array(["x", "y"]),
                    dims=["ch"],
                ),
            },
            key="mouse",
        )

    def _hash_message(self) -> int:
        # Return constant - state persists across calls
        return 0

    def _drain_queue(self) -> tuple[list[float], list[float], list[float]]:
        """Drain all events from queue."""
        x_vals: list[float] = []
        y_vals: list[float] = []
        timestamps: list[float] = []

        while True:
            try:
                x, y, t = self._state.event_queue.get_nowait()
                x_vals.append(float(x))
                y_vals.append(float(y))
                timestamps.append(t)
            except queue.Empty:
                break

        return x_vals, y_vals, timestamps

    def _build_output(self, x_vals: list[float], y_vals: list[float], timestamps: list[float]) -> AxisArray | None:
        """Build output AxisArray from collected events."""
        if not timestamps:
            return None

        data = np.column_stack([x_vals, y_vals])
        time_axis = replace(
            self._state.template.axes["time"],
            data=np.array(timestamps, dtype=np.float64),
        )

        return replace(
            self._state.template,
            data=data,
            axes={"time": time_axis, "ch": self._state.template.axes["ch"]},
        )

    def __call__(self) -> AxisArray | None:
        """Synchronous production - drain queue and return events."""
        if self._hash == -1:
            self._reset_state()
            self._hash = 0

        x_vals, y_vals, timestamps = self._drain_queue()
        return self._build_output(x_vals, y_vals, timestamps)

    async def _produce(self) -> AxisArray | None:
        """Async production - drain queue and return events."""
        x_vals, y_vals, timestamps = self._drain_queue()
        return self._build_output(x_vals, y_vals, timestamps)

    def __del__(self) -> None:
        """Clean up listener on destruction."""
        if hasattr(self, "_state") and self._state.listener is not None:
            self._state.listener.stop()


class MouseListener(BaseProducerUnit[MouseListenerSettings, AxisArray, MouseListenerProducer]):
    """
    Unit for event-driven mouse position capture.

    Produces AxisArray messages with mouse positions and their timestamps
    as events occur. Time axis is an irregular CoordinateAxis.
    """

    SETTINGS = MouseListenerSettings
