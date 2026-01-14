"""
HerecoBot CLI - Chat with AI from your terminal
"""

import argparse
import sys

from .client import Hereco
from . import __version__


def print_banner():
    """Print HerecoBot banner"""
    print("""
╔═══════════════════════════════════════╗
║  🤖 Hereco AI - Chat Terminal         ║
║     Type 'quit' or 'exit' to leave    ║
║     Type 'clear' to reset             ║
╚═══════════════════════════════════════╝
""")


def chat_command(args):
    """Interactive chat mode"""
    try:
        client = Hereco(
            space_url=args.space if args.space else None,
            timeout=args.timeout,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nSet HERECO_SPACE environment variable or use --space flag", file=sys.stderr)
        sys.exit(1)

    if args.message:
        # Single message mode
        try:
            response = client.chat.create(args.message)
            print(response.output_text)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Interactive mode
    print_banner()
    print(f"Connected to: {client.space_url}\n")
    history = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "clear":
                history.clear()
                print("🗑️  History cleared\n")
                continue

            if user_input.lower() == "history":
                if not history:
                    print("📜 No history yet\n")
                else:
                    print("\n📜 Conversation History:")
                    for msg in history:
                        role = "You" if msg["role"] == "user" else "Bot"
                        print(f"  {role}: {msg['content'][:100]}...")
                    print()
                continue

            print("Bot: ", end="", flush=True)
            response = client.chat.create(user_input)
            print(response.output_text)
            print()

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response.output_text})

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        except EOFError:
            print("\n👋 Goodbye!")
            break


def ping_command(args):
    """Check if HF Space is alive"""
    try:
        client = Hereco(space_url=args.space if args.space else None)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nSet HERECO_SPACE environment variable or use --space flag", file=sys.stderr)
        sys.exit(1)

    print(f"Pinging {client.space_url}...", end=" ", flush=True)

    if client.ping():
        print("✅ Online!")
        sys.exit(0)
    else:
        print("❌ Offline or unreachable")
        sys.exit(1)


def test_key_command(args):
    """Test if API key is valid"""
    client = Hereco(
        api_key=args.key if args.key else None,
        api_base=args.api_base if args.api_base else None,
    )
    
    key_to_test = args.key or client.api_key
    if not key_to_test:
        print("Error: No API key provided", file=sys.stderr)
        print("\nSet HERECO_API_KEY environment variable or use --key flag", file=sys.stderr)
        sys.exit(1)
    
    print(f"Testing API key: {key_to_test[:12]}...", end=" ", flush=True)
    
    result = client.test_key(key_to_test)
    
    if result.valid:
        print("✅ Valid!")
        print(f"\n  Key ID:      {result.key_id}")
        print(f"  Permissions: {', '.join(result.permissions or [])}")
        print(f"  Rate Limit:  {result.rate_limit}/min")
        print(f"  Remaining:   {result.remaining}")
        if result.error:
            print(f"  Warning:     {result.error}")
        sys.exit(0)
    else:
        print("❌ Invalid!")
        print(f"\n  Error: {result.error}")
        sys.exit(1)


def ask_command(args):
    """Send a single question and get response"""
    try:
        client = Hereco(
            space_url=args.space if args.space else None,
            timeout=args.timeout,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nSet HERECO_SPACE environment variable or use --space flag", file=sys.stderr)
        sys.exit(1)

    try:
        print(client.ask(args.question))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="herecobot",
        description="🤖 Hereco AI - Chat with AI from your terminal",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument(
        "-m",
        "--message",
        help="Send a single message (non-interactive)",
    )
    chat_parser.add_argument(
        "-s",
        "--space",
        help="HF Space URL (or set HERECO_SPACE env var)",
    )
    chat_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    chat_parser.set_defaults(func=chat_command)

    # Ping command
    ping_parser = subparsers.add_parser("ping", help="Check if HF Space is online")
    ping_parser.add_argument(
        "-s",
        "--space",
        help="HF Space URL (or set HERECO_SPACE env var)",
    )
    ping_parser.set_defaults(func=ping_command)

    # Test key command
    test_parser = subparsers.add_parser("test-key", help="Test if API key is valid")
    test_parser.add_argument(
        "-k",
        "--key",
        help="API key to test (or set HERECO_API_KEY env var)",
    )
    test_parser.add_argument(
        "--api-base",
        help="API base URL (default: https://hereco.xyz)",
    )
    test_parser.set_defaults(func=test_key_command)

    # Ask command (shortcut for single question)
    ask_parser = subparsers.add_parser("ask", help="Ask a single question")
    ask_parser.add_argument(
        "question",
        help="Question to ask",
    )
    ask_parser.add_argument(
        "-s",
        "--space",
        help="HF Space URL (or set HERECO_SPACE env var)",
    )
    ask_parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    ask_parser.set_defaults(func=ask_command)

    # Parse args
    args = parser.parse_args()

    if args.command is None:
        # Default to interactive chat
        args.message = None
        args.space = None
        args.timeout = 30.0
        chat_command(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
