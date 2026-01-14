"""Main CLI entry point for Prompt Cheater."""

import argparse
import sys
import time

from . import __version__
from .ai import GeminiClient
from .tmux import (
    NoPaneFoundError,
    NotInTmuxError,
    TmuxError,
    send_text_to_other_pane,
)
from .ui import (
    COLORS,
    confirm,
    console,
    get_multiline_input,
    get_single_line_input,
    print_api_key_guide,
    print_banner,
    print_error,
    print_info,
    print_separator,
    print_success,
    print_warning,
    show_xml_preview,
    spinner,
)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="cheater",
        description="Convert natural language to Claude-friendly XML prompts and inject into Tmux",
    )
    parser.add_argument(
        "-m",
        "--multiline",
        action="store_true",
        default=False,
        dest="multiline",
        help="Use multiline input mode (default is single-line)",
    )
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        default=False,
        help="Preview the generated XML before sending",
    )
    parser.add_argument(
        "-n",
        "--no-send",
        action="store_true",
        default=False,
        dest="no_send",
        help="Generate XML but don't send to Tmux (dry run)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Prompt Cheater v{__version__}",
    )

    args = parser.parse_args()

    print_banner()

    # Check Tmux environment early (unless dry run)
    if not args.no_send:
        try:
            from .tmux import get_current_pane_id

            get_current_pane_id()
        except NotInTmuxError as e:
            print_error(str(e))
            sys.exit(1)

    # Initialize Gemini client once
    try:
        client = GeminiClient()
    except ValueError:
        print_api_key_guide()
        sys.exit(1)

    console.print(f"[{COLORS['dim']}]Ctrl+C to exit[/{COLORS['dim']}]")
    console.print()

    first_iteration = True

    # Main loop - keep running until Ctrl+C
    while True:
        # Print separator between iterations (except first)
        if not first_iteration:
            print_separator()
        first_iteration = False

        # Get user input
        try:
            if args.multiline:
                user_input = get_multiline_input()
            else:
                user_input = get_single_line_input()
        except KeyboardInterrupt:
            console.print()
            print_info("Goodbye!")
            sys.exit(0)

        if not user_input.strip():
            print_warning("Empty input. Try again.")
            console.print()
            continue

        # Generate XML prompt using Gemini
        start_time = time.time()
        try:
            with spinner("Gemini is crafting your prompt..."):
                xml_prompt = client.generate_xml_prompt(user_input)
        except Exception as e:
            print_error(f"Failed to generate prompt: {e}")
            console.print()
            continue

        # Preview if requested
        if args.preview or args.no_send:
            show_xml_preview(xml_prompt)

        # Confirm before sending if preview is enabled
        if (
            args.preview
            and not args.no_send
            and not confirm("Send this prompt to Claude Code?")
        ):
            print_warning("Cancelled.")
            console.print()
            continue

        # Send to Tmux
        if not args.no_send:
            try:
                with spinner("Delivering to Tmux..."):
                    target_pane = send_text_to_other_pane(xml_prompt, enter=True)
                elapsed = time.time() - start_time
                print_success(f"Sent to pane {target_pane}", elapsed=elapsed)
            except NoPaneFoundError as e:
                print_error(str(e))
            except TmuxError as e:
                print_error(f"Tmux error: {e}")
            except Exception as e:
                print_error(f"Failed to send to Tmux: {e}")
        else:
            print_info("Dry run mode - prompt was not sent.")

        console.print()


def app():
    """Wrapper for entry point compatibility."""
    main()


if __name__ == "__main__":
    main()
