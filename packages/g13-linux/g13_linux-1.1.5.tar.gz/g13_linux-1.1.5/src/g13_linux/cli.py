import argparse
import sys

from .device import open_g13, read_event
from .mapper import G13Mapper


def run_daemon():
    """Run the G13 input daemon."""
    print("Opening Logitech G13…")
    try:
        h = open_g13()
    except Exception as e:
        print(f"Error: Could not open G13 device: {e}", file=sys.stderr)
        print("Make sure the G13 is connected and udev rules are installed.", file=sys.stderr)
        sys.exit(1)

    mapper = G13Mapper()
    print("G13 opened. Press keys; Ctrl+C to exit.")

    try:
        while True:
            data = read_event(h)
            if data:
                mapper.handle_raw_report(data)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        h.close()
        mapper.close()


def main():
    parser = argparse.ArgumentParser(
        prog="g13-linux",
        description="Logitech G13 Linux driver with macro support, RGB control, and LCD display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  g13-linux              Run the input daemon
  g13-linux --version    Show version
  g13-linux-gui          Launch the GUI application

For more information, see: https://github.com/AreteDriver/G13_Linux
""",
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version and exit"
    )
    parser.add_argument(
        "--run", "-r", action="store_true", help="Run the input daemon (default)"
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"g13-linux {__version__}")
        sys.exit(0)

    # Default action: run daemon
    run_daemon()


if __name__ == "__main__":
    main()
