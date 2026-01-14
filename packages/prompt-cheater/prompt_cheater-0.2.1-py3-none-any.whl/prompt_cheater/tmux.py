"""Tmux integration module for pane discovery and text injection."""

import os
import subprocess
import time

import libtmux
from libtmux.pane import Pane


class TmuxError(Exception):
    """Base exception for Tmux-related errors."""

    pass


class NotInTmuxError(TmuxError):
    """Raised when not running inside a Tmux session."""

    pass


class NoPaneFoundError(TmuxError):
    """Raised when no target pane can be found."""

    pass


def get_current_pane_id() -> str:
    """Get the current pane ID from environment.

    Returns:
        Current pane ID (e.g., '%0', '%1').

    Raises:
        NotInTmuxError: If not running inside Tmux.
    """
    pane_id = os.getenv("TMUX_PANE")
    if not pane_id:
        raise NotInTmuxError(
            "Not running inside a Tmux session. "
            "Please run this command from within Tmux."
        )
    return pane_id


def get_server() -> libtmux.Server:
    """Get the Tmux server instance.

    Returns:
        libtmux Server object.
    """
    return libtmux.Server()


def get_current_window() -> libtmux.Window:
    """Get the current Tmux window.

    Returns:
        Current Window object.

    Raises:
        NotInTmuxError: If not running inside Tmux.
        TmuxError: If window cannot be found.
    """
    current_pane_id = get_current_pane_id()
    server = get_server()

    # Find the pane and its window
    for session in server.sessions:
        for window in session.windows:
            for pane in window.panes:
                if pane.pane_id == current_pane_id:
                    return window

    raise TmuxError(f"Could not find window for pane {current_pane_id}")


def get_target_pane(explicit_pane_id: str | None = None) -> Pane:
    """Find the target pane to send text to.

    Args:
        explicit_pane_id: If provided, use this pane ID directly.

    Returns:
        Target Pane object.

    Raises:
        NotInTmuxError: If not running inside Tmux.
        NoPaneFoundError: If no suitable target pane is found.
    """
    # Check for explicit pane ID from env or argument
    target_id = explicit_pane_id or os.getenv("CHEATER_TARGET_PANE")

    if target_id:
        server = get_server()
        for session in server.sessions:
            for window in session.windows:
                for pane in window.panes:
                    if pane.pane_id == target_id:
                        return pane
        raise NoPaneFoundError(f"Explicit target pane {target_id} not found")

    # Auto-discovery: find another pane in the same window
    current_pane_id = get_current_pane_id()
    window = get_current_window()
    panes = window.panes

    if len(panes) < 2:
        raise NoPaneFoundError(
            "Only one pane in current window. "
            "Please split the window (Ctrl+B %) to create another pane."
        )

    # Find a pane that is not the current one
    for pane in panes:
        if pane.pane_id != current_pane_id:
            return pane

    raise NoPaneFoundError("Could not find a target pane")


def send_to_pane(pane: Pane, text: str, enter: bool = True) -> None:
    """Send text to a Tmux pane using send-keys for direct input.

    Uses send-keys -l (literal mode) instead of paste-buffer to avoid
    Claude Code detecting the input as pasted text.

    Args:
        pane: Target Pane object.
        text: Text to send.
        enter: Whether to send Enter key after text (default: True).

    Raises:
        TmuxError: If text transmission fails.
    """
    pane_id = pane.pane_id or ""

    # Chunk size for send-keys (avoid buffer limits)
    chunk_size = 500

    # Send text in chunks using send-keys -l (literal mode)
    # This is recognized as typing, not pasting
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        result = subprocess.run(
            ["tmux", "send-keys", "-t", pane_id, "-l", chunk],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise TmuxError(f"Failed to send keys: {result.stderr}")
        # Small delay between chunks for stability
        if i + chunk_size < len(text):
            time.sleep(0.01)

    # Send Enter if requested
    if enter:
        time.sleep(0.05)
        pane.send_keys("", enter=True)


def send_text_to_other_pane(text: str, enter: bool = True) -> str:
    """Convenience function to send text to the other pane.

    Args:
        text: Text to send.
        enter: Whether to send Enter key after text (default: True).

    Returns:
        Target pane ID for confirmation.

    Raises:
        NotInTmuxError: If not running inside Tmux.
        NoPaneFoundError: If no target pane found.
    """
    pane = get_target_pane()
    send_to_pane(pane, text, enter=enter)
    return pane.pane_id or ""
