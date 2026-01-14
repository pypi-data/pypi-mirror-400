#!/usr/bin/env python3
"""Token Usage Graph Visualizer for Claude Code.

Displays ASCII graphs of token consumption over time.

Usage:
    token-graph [session_id] [options]

Options:
    --type <cumulative|delta|io|both|all>  Graph type to display (default: both)
    --watch, -w [interval]                  Real-time monitoring mode (default: 2s)
    --no-color                              Disable color output
    --help                                  Show this help
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

from claude_statusline import __version__
from claude_statusline.core.colors import ColorManager
from claude_statusline.core.config import Config
from claude_statusline.core.state import StateFile
from claude_statusline.graphs.renderer import GraphRenderer, GraphDimensions
from claude_statusline.graphs.statistics import calculate_deltas


# Cursor control sequences
CURSOR_HOME = "\033[H"
CLEAR_SCREEN = "\033[2J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_TO_END = "\033[J"


def show_help() -> None:
    """Show help message."""
    print(
        """Token Usage Graph Visualizer for Claude Code

USAGE:
    token-graph [session_id] [options]

ARGUMENTS:
    session_id    Optional session ID. If not provided, uses the latest session.

OPTIONS:
    --type <type>  Graph type to display:
                   - cumulative: Total tokens over time
                   - delta: Token consumption per interval
                   - io: Input/output tokens over time
                   - both: Show cumulative and delta graphs (default)
                   - all: Show all graphs including I/O
    --watch, -w [interval]
                   Enable real-time monitoring mode.
                   Refreshes the graph every [interval] seconds (default: 2).
                   Press Ctrl+C to exit.
    --no-color     Disable color output
    --help         Show this help message

EXAMPLES:
    # Show graphs for latest session
    token-graph

    # Show graphs for specific session
    token-graph abc123def

    # Show only cumulative graph
    token-graph --type cumulative

    # Show input/output token graphs
    token-graph --type io

    # Real-time monitoring (refresh every 2 seconds)
    token-graph --watch

    # Real-time monitoring with custom interval
    token-graph -w 5

    # Combine options
    token-graph abc123 --type cumulative --watch 3

    # Disable colors for piping to file
    token-graph --no-color > output.txt

DATA SOURCE:
    Reads token history from ~/.claude/statusline/statusline.<session_id>.state
"""
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Token Usage Graph Visualizer for Claude Code",
        add_help=False,
    )
    parser.add_argument("session_id", nargs="?", default=None, help="Session ID")
    parser.add_argument(
        "--type",
        choices=["cumulative", "delta", "io", "both", "all"],
        default="both",
        help="Graph type to display",
    )
    parser.add_argument(
        "--watch",
        "-w",
        nargs="?",
        const=2,
        type=int,
        default=None,
        help="Watch mode interval in seconds",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable color output",
    )
    parser.add_argument(
        "--help",
        "-h",
        action="store_true",
        help="Show help message",
    )

    args = parser.parse_args()

    if args.help:
        show_help()
        sys.exit(0)

    return args


def render_once(
    state_file: StateFile,
    graph_type: str,
    renderer: GraphRenderer,
    colors: ColorManager,
    watch_mode: bool = False,
) -> bool:
    """Render graphs once.

    Args:
        state_file: StateFile instance
        graph_type: Type of graphs to render
        renderer: GraphRenderer instance
        colors: ColorManager instance
        watch_mode: Whether running in watch mode

    Returns:
        True if rendering was successful, False if not enough data
    """
    entries = state_file.read_history()

    if len(entries) < 2:
        print(
            f"\n{colors.yellow}Need at least 2 data points to generate graphs.{colors.reset}"
        )
        print(
            f"{colors.dim}Found: {len(entries)} entry. Use Claude Code to accumulate more data.{colors.reset}"
        )
        return False

    # Extract data for graphs
    timestamps = [e.timestamp for e in entries]
    tokens = [e.total_tokens for e in entries]
    input_tokens = [e.total_input_tokens for e in entries]
    output_tokens = [e.total_output_tokens for e in entries]
    deltas = calculate_deltas(tokens)
    delta_times = timestamps[1:]  # Deltas start from second entry

    # Get session name from file path
    file_path = state_file.find_latest_state_file()
    session_name = file_path.stem.replace("statusline.", "") if file_path else "unknown"

    # Header
    if not watch_mode:
        print()
    print(
        f"{colors.bold}{colors.magenta}Token Usage Graphs{colors.reset} "
        f"{colors.dim}(Session: {session_name}){colors.reset}"
    )

    # Render requested graphs
    if graph_type in ("cumulative", "both", "all"):
        renderer.render_timeseries(tokens, timestamps, "Cumulative Token Usage", colors.green)

    if graph_type in ("delta", "both", "all"):
        renderer.render_timeseries(deltas, delta_times, "Token Delta Per Interval", colors.cyan)

    if graph_type in ("io", "all"):
        renderer.render_timeseries(input_tokens, timestamps, "Input Tokens (↓)", colors.blue)
        renderer.render_timeseries(output_tokens, timestamps, "Output Tokens (↑)", colors.magenta)

    # Summary and footer
    renderer.render_summary(entries, deltas)
    renderer.render_footer(__version__)

    return True


def run_watch_mode(
    state_file: StateFile,
    graph_type: str,
    interval: int,
    renderer: GraphRenderer,
    colors: ColorManager,
) -> None:
    """Run in watch mode with continuous refresh.

    Args:
        state_file: StateFile instance
        graph_type: Type of graphs to render
        interval: Refresh interval in seconds
        renderer: GraphRenderer instance
        colors: ColorManager instance
    """
    # Signal handler for clean exit
    def handle_signal(signum: int, frame: object) -> None:
        print(f"{SHOW_CURSOR}")
        print(f"\n{colors.dim}Watch mode stopped.{colors.reset}")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Hide cursor
    print(HIDE_CURSOR, end="", flush=True)

    # Initial clear
    print(f"{CLEAR_SCREEN}{CURSOR_HOME}", end="", flush=True)

    try:
        while True:
            # Move cursor to home
            print(CURSOR_HOME, end="", flush=True)

            # Update dimensions in case of terminal resize
            renderer.dimensions = GraphDimensions.detect()

            # Watch mode indicator
            current_time = time.strftime("%H:%M:%S")
            print(
                f"{colors.dim}[LIVE {current_time}] Refresh: {interval}s | Ctrl+C to exit{colors.reset}"
            )

            # Render
            render_once(state_file, graph_type, renderer, colors, watch_mode=True)

            # Clear any remaining content
            print(CLEAR_TO_END, end="", flush=True)

            time.sleep(interval)
    finally:
        print(SHOW_CURSOR, end="", flush=True)


def main() -> None:
    """Main entry point for token-graph CLI."""
    args = parse_args()

    # Load config for token_detail setting
    config = Config.load()

    # Setup colors
    color_enabled = not args.no_color and sys.stdout.isatty()
    colors = ColorManager(enabled=color_enabled)

    # Setup state file
    state_file = StateFile(args.session_id)

    # Find state file
    file_path = state_file.find_latest_state_file()
    if not file_path:
        print(f"{colors.red}Error:{colors.reset} No state files found in ~/.claude/statusline/")
        print(f"{colors.dim}Run Claude Code to generate token usage data.{colors.reset}")
        sys.exit(1)

    if not file_path.exists():
        print(f"{colors.red}Error:{colors.reset} State file not found: {file_path}")
        sys.exit(1)

    # Setup renderer
    renderer = GraphRenderer(
        colors=colors,
        token_detail=config.token_detail,
    )

    # Run
    if args.watch is not None:
        run_watch_mode(state_file, args.type, args.watch, renderer, colors)
    else:
        success = render_once(state_file, args.type, renderer, colors)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
