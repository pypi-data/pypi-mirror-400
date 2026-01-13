"""
Progress Tracking
=================

Progress bars and callbacks for long-running simulations.
"""

import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterator, Optional

# Try to import tqdm
try:
    from tqdm.auto import tqdm as tqdm_auto

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm_auto = None

from .logging import get_logger

logger = get_logger("progress")


@dataclass
class ProgressInfo:
    """Information about current progress."""

    current: int
    total: int
    elapsed: float
    eta: Optional[float]
    rate: Optional[float]
    message: str = ""

    @property
    def percent(self) -> float:
        """Progress percentage."""
        return (self.current / self.total * 100) if self.total > 0 else 0.0

    @property
    def remaining(self) -> int:
        """Remaining iterations."""
        return max(0, self.total - self.current)


class SimpleProgress:
    """Simple progress bar without tqdm dependency."""

    def __init__(self, total: int, desc: str = "", unit: str = "it", disable: bool = False):
        self.total = total
        self.desc = desc
        self.unit = unit
        self.disable = disable
        self.current = 0
        self.start_time = time.time()
        self._last_print = 0

    def update(self, n: int = 1) -> None:
        """Update progress by n steps."""
        self.current += n

        if self.disable:
            return

        # Print at most every 0.1 seconds
        now = time.time()
        if now - self._last_print < 0.1 and self.current < self.total:
            return
        self._last_print = now

        self._print_progress()

    def _print_progress(self) -> None:
        """Print progress bar to stderr."""
        elapsed = time.time() - self.start_time

        # Calculate ETA (guard against zero elapsed time on fast systems)
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate
            eta_str = self._format_time(eta)
        else:
            rate = 0
            eta_str = "?"

        # Build progress bar
        bar_width = 30
        filled = int(bar_width * self.current / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        # Format output
        desc = f"{self.desc}: " if self.desc else ""
        time_info = f"[{self._format_time(elapsed)}<{eta_str}, {rate:.1f}{self.unit}/s]"
        line = f"\r{desc}|{bar}| {self.current}/{self.total} {time_info}"

        sys.stderr.write(line)
        sys.stderr.flush()

        if self.current >= self.total:
            sys.stderr.write("\n")

    def _format_time(self, seconds: float) -> str:
        """Format seconds as mm:ss or hh:mm:ss."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}:{int(seconds % 60):02d}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}:{minutes:02d}:{secs:02d}"

    def set_description(self, desc: str) -> None:
        """Update description."""
        self.desc = desc

    def close(self) -> None:
        """Close progress bar."""
        if not self.disable and self.current < self.total:
            sys.stderr.write("\n")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ProgressTracker:
    """
    Unified progress tracking with tqdm or fallback.

    Examples:
    ---------
    >>> with ProgressTracker(1000, desc="Simulating") as pbar:
    ...     for i in range(1000):
    ...         # do work
    ...         pbar.update()
    """

    def __init__(
        self,
        total: int,
        desc: str = "",
        unit: str = "it",
        disable: bool = False,
        leave: bool = True,
        callback: Optional[Callable[[ProgressInfo], None]] = None,
    ):
        """
        Initialize progress tracker.

        Args:
            total: Total iterations
            desc: Description
            unit: Unit of iteration
            disable: Disable progress bar
            leave: Leave progress bar on screen after completion
            callback: Optional callback called on each update
        """
        self.total = total
        self.desc = desc
        self.unit = unit
        self.disable = disable
        self.leave = leave
        self.callback = callback
        self.current = 0
        self.start_time = time.time()

        # Create appropriate progress bar
        if TQDM_AVAILABLE and not disable:
            self._pbar = tqdm_auto(
                total=total, desc=desc, unit=unit, leave=leave, dynamic_ncols=True
            )
        else:
            self._pbar = SimpleProgress(total=total, desc=desc, unit=unit, disable=disable)

    def update(self, n: int = 1, message: str = "") -> None:
        """Update progress by n steps."""
        self.current += n
        self._pbar.update(n)

        if self.callback:
            info = self.get_info()
            info.message = message
            self.callback(info)

    def get_info(self) -> ProgressInfo:
        """Get current progress information."""
        elapsed = time.time() - self.start_time

        # Guard against zero elapsed time on fast systems (Windows)
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate
        else:
            rate = None
            eta = None

        return ProgressInfo(
            current=self.current, total=self.total, elapsed=elapsed, eta=eta, rate=rate
        )

    def set_description(self, desc: str) -> None:
        """Update description."""
        self.desc = desc
        if hasattr(self._pbar, "set_description"):
            self._pbar.set_description(desc)

    def set_postfix(self, **kwargs) -> None:
        """Set postfix values (tqdm only)."""
        if hasattr(self._pbar, "set_postfix"):
            self._pbar.set_postfix(**kwargs)

    def close(self) -> None:
        """Close progress bar."""
        if hasattr(self._pbar, "close"):
            self._pbar.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def progress_iter(
    iterable: Iterator, total: Optional[int] = None, desc: str = "", disable: bool = False
) -> Iterator:
    """
    Wrap an iterable with a progress bar.

    Args:
        iterable: Iterable to wrap
        total: Total count (auto-detected if possible)
        desc: Description
        disable: Disable progress bar

    Yields:
        Items from iterable
    """
    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            total = None

    if TQDM_AVAILABLE and not disable:
        yield from tqdm_auto(iterable, total=total, desc=desc)
    else:
        if total:
            pbar = SimpleProgress(total=total, desc=desc, disable=disable)
            for item in iterable:
                yield item
                pbar.update()
            pbar.close()
        else:
            yield from iterable


class ProgressCallback:
    """
    Callback class for integration with simulators.

    Examples:
    ---------
    >>> callback = ProgressCallback(total_steps=1000)
    >>> sim.simulate(callback=callback.update)
    """

    def __init__(
        self,
        total_steps: int,
        desc: str = "Simulating",
        update_interval: int = 10,
        disable: bool = False,
    ):
        self.total_steps = total_steps
        self.update_interval = update_interval
        self.pbar = ProgressTracker(total_steps, desc=desc, disable=disable)
        self._last_step = 0

    def update(self, step: int, **kwargs) -> None:
        """
        Update callback - call from simulation loop.

        Args:
            step: Current step number
            **kwargs: Additional info to display
        """
        delta = step - self._last_step
        if delta >= self.update_interval:
            self.pbar.update(delta)
            self._last_step = step

            if kwargs:
                self.pbar.set_postfix(**kwargs)

    def finish(self) -> None:
        """Finish progress tracking."""
        remaining = self.total_steps - self._last_step
        if remaining > 0:
            self.pbar.update(remaining)
        self.pbar.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.finish()
