"""Rich TUI helpers for terminal user interface."""

from collections.abc import Generator
from contextlib import contextmanager

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.syntax import Syntax
from rich.text import Text

# Global console instance
console = Console()

# Nord color palette (pastel, eye-friendly)
COLORS = {
    "banner": "#B48EAD",  # Pastel purple
    "success": "#A3BE8C",  # Pastel green
    "error": "#BF616A",  # Pastel red
    "info": "#88C0D0",  # Pastel blue
    "warning": "#EBCB8B",  # Pastel yellow
    "dim": "#4C566A",  # Gray
    "border": "#5E81AC",  # Muted blue
}

# prompt_toolkit style using Nord palette
PROMPT_STYLE = Style.from_dict(
    {
        "prompt": "#88C0D0",  # Info color for main prompt
        "continuation": "#4C566A",  # Dim color for continuation
        "confirm": "#88C0D0",  # Info color for confirm prompt
    }
)

# Global prompt session state (for history persistence)
_history = InMemoryHistory()
_session: PromptSession[str] | None = None


def _create_key_bindings() -> KeyBindings:
    """Create custom key bindings for the prompt."""
    kb = KeyBindings()

    @kb.add(Keys.Escape, Keys.Escape)
    def clear_input(event: KeyPressEvent) -> None:
        """Clear current input buffer on double ESC."""
        event.app.current_buffer.reset()

    return kb


def _get_session() -> PromptSession[str]:
    """Get or create the global PromptSession with history and key bindings."""
    global _session  # noqa: PLW0603
    if _session is None:
        _session = PromptSession(
            style=PROMPT_STYLE,
            history=_history,
            key_bindings=_create_key_bindings(),
        )
    return _session


def print_banner() -> None:
    """Print the application banner."""
    title = Text()
    title.append("⚡ ", style=f"bold {COLORS['warning']}")
    title.append("Prompt Cheater", style=f"bold {COLORS['banner']}")

    subtitle = Text("Natural Language → XML → Claude Code", style=COLORS["dim"])

    content = Text()
    content.append_text(title)
    content.append("\n")
    content.append_text(subtitle)

    console.print()
    console.print(
        Panel(content, border_style=COLORS["banner"], width=50, padding=(0, 1))
    )
    console.print()


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[{COLORS['info']}]›[/{COLORS['info']}] {message}")


def print_success(message: str, elapsed: float | None = None) -> None:
    """Print a success message with optional timing."""
    msg = f"[{COLORS['success']}]✓[/{COLORS['success']}] {message}"
    if elapsed is not None:
        msg += f" [{COLORS['dim']}][{elapsed:.1f}s][/{COLORS['dim']}]"
    console.print(msg)


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[{COLORS['error']}]✗[/{COLORS['error']}] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[{COLORS['warning']}]![/{COLORS['warning']}] {message}")


def get_multiline_input() -> str:
    """Get multiline input from user using prompt_toolkit.

    User can type multiple lines. Empty line (Enter twice) to send.
    Press Ctrl+C to cancel.

    Returns:
        The complete input string.

    Note:
        - Use up/down arrows to navigate history
        - Press ESC twice to clear input
    """
    console.print(
        f"[{COLORS['dim']}]Enter twice to send • Ctrl+C to cancel[/{COLORS['dim']}]"
    )

    session = _get_session()
    lines: list[str] = []

    try:
        while True:
            if not lines:
                prompt_text = HTML("<prompt>❯</prompt> ")
            else:
                prompt_text = HTML("<continuation>│</continuation> ")

            line = session.prompt(prompt_text)
            if line == "" and lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)
    except (KeyboardInterrupt, EOFError):
        console.print()
        raise KeyboardInterrupt from None

    return "\n".join(lines)


def get_single_line_input(prompt: str = "Enter your instruction") -> str:
    """Get single line input from user using prompt_toolkit.

    Args:
        prompt: The prompt to display.

    Returns:
        The input string.

    Note:
        - Use up/down arrows to navigate history
        - Press ESC twice to clear input
    """
    session = _get_session()
    prompt_text = HTML(f"<prompt>{prompt}:</prompt> ")
    return session.prompt(prompt_text)


@contextmanager
def spinner(message: str) -> Generator[Status, None, None]:
    """Context manager for showing a spinner.

    Args:
        message: Message to display with the spinner.

    Yields:
        The Status object for updating if needed.
    """
    with console.status(
        f"[bold {COLORS['info']}]{message}[/bold {COLORS['info']}]"
    ) as status:
        yield status


def show_xml_preview(xml_text: str) -> None:
    """Display XML preview with syntax highlighting.

    Args:
        xml_text: The XML text to display.
    """
    console.print()
    console.print(f"[{COLORS['dim']}]Generated XML prompt:[/{COLORS['dim']}]")
    syntax = Syntax(xml_text, "xml", theme="nord", line_numbers=False)
    console.print(Panel(syntax, border_style=COLORS["success"], padding=(0, 1)))
    console.print()


def confirm(message: str, default: bool = True) -> bool:
    """Ask for confirmation using prompt_toolkit.

    Args:
        message: The question to ask.
        default: Default value if user just presses Enter.

    Returns:
        True if confirmed, False otherwise.
    """
    suffix = "[Y/n]" if default else "[y/N]"
    session: PromptSession[str] = PromptSession(style=PROMPT_STYLE)
    prompt_text = HTML(f"<confirm>{message}</confirm> {suffix} ")

    try:
        response = session.prompt(prompt_text).strip().lower()
    except (KeyboardInterrupt, EOFError):
        console.print()
        return False

    if not response:
        return default

    return response in ("y", "yes")


def print_separator() -> None:
    """Print a visual separator line."""
    console.print(f"[{COLORS['dim']}]{'─' * 50}[/{COLORS['dim']}]")
    console.print()


def print_api_key_guide() -> None:
    """Print API key setup guide for new users."""
    guide = Text()
    guide.append("Gemini API Key Required\n\n", style=f"bold {COLORS['warning']}")

    guide.append("1. ", style=f"bold {COLORS['info']}")
    guide.append("Get your API key:\n", style="bold")
    guide.append("   https://aistudio.google.com/apikey\n\n", style=COLORS["info"])

    guide.append("2. ", style=f"bold {COLORS['info']}")
    guide.append("Set the environment variable:\n\n", style="bold")
    guide.append("   # Add to ~/.zshrc or ~/.bashrc\n", style=COLORS["dim"])
    guide.append(
        '   export GEMINI_API_KEY="your_key_here"\n\n', style=COLORS["success"]
    )
    guide.append("   # Or create .env file in current directory\n", style=COLORS["dim"])
    guide.append(
        "   echo 'GEMINI_API_KEY=your_key' > .env\n\n", style=COLORS["success"]
    )

    guide.append("3. ", style=f"bold {COLORS['info']}")
    guide.append("Restart terminal and run:\n", style="bold")
    guide.append("   cheater", style=COLORS["success"])

    console.print()
    console.print(
        Panel(guide, border_style=COLORS["warning"], width=55, padding=(1, 2))
    )
