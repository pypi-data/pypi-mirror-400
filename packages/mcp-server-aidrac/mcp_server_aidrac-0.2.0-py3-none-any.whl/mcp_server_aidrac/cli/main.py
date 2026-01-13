#!/usr/bin/env python3
"""
aidrac - Main AIdrac command interface

Usage:
    aidrac send <message> --transport <dtmf|ultrasonic|ntfy|ipoll>
    aidrac listen --transport <transport>
    aidrac status
    aidrac encode <text> --format <dtmf|morse|braille>
    aidrac decode <encoded> --format <format>

Examples:
    echo "reboot" | aidrac send --transport ntfy --topic myserver
    aidrac listen --transport dtmf | aidrac --execute
    aidrac encode "HELLO" --format morse
"""

import sys
import argparse
from typing import Optional


def main():
    parser = argparse.ArgumentParser(
        prog="aidrac",
        description="AIdrac - AI Out-of-Band Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aidrac send "reboot" --transport ntfy --topic myserver
  aidrac listen --transport ultrasonic
  aidrac encode "SOS" --format morse
  aidrac status

Transports:
  dtmf        Telephone DTMF tones
  ultrasonic  Inaudible ggwave audio
  ntfy        Push notifications (ntfy.sh)
  ipoll       AInternet I-Poll messaging

Formats:
  dtmf        Phone keypad tones
  morse       Morse code (.- format)
  braille     Unicode braille

Part of HumoticaOS - One love, one fAmIly!
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # send command
    send_parser = subparsers.add_parser("send", help="Send a command")
    send_parser.add_argument("message", nargs="?", help="Message to send (or stdin)")
    send_parser.add_argument("-t", "--transport", choices=["dtmf", "ultrasonic", "ntfy", "ipoll"],
                            default="ntfy", help="Transport method")
    send_parser.add_argument("--topic", help="ntfy topic or agent ID")
    send_parser.add_argument("--mode", choices=["audible", "ultrasonic", "stealth"],
                            default="ultrasonic", help="Ultrasonic mode")

    # listen command
    listen_parser = subparsers.add_parser("listen", help="Listen for commands")
    listen_parser.add_argument("-t", "--transport", choices=["dtmf", "ultrasonic", "ntfy", "ipoll"],
                              default="ntfy", help="Transport method")
    listen_parser.add_argument("--topic", help="ntfy topic or agent ID")
    listen_parser.add_argument("--execute", action="store_true", help="Execute received commands")

    # encode command
    encode_parser = subparsers.add_parser("encode", help="Encode text")
    encode_parser.add_argument("text", nargs="?", help="Text to encode (or stdin)")
    encode_parser.add_argument("-f", "--format", choices=["dtmf", "morse", "braille", "morse_visual"],
                              default="morse", help="Output format")

    # decode command
    decode_parser = subparsers.add_parser("decode", help="Decode encoded text")
    decode_parser.add_argument("encoded", nargs="?", help="Encoded text (or stdin)")
    decode_parser.add_argument("-f", "--format", choices=["dtmf", "morse", "braille"],
                              default="morse", help="Input format")

    # status command
    subparsers.add_parser("status", help="Show AIdrac status")

    # version
    parser.add_argument("-v", "--version", action="version", version="aidrac 0.1.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Read from stdin if no message provided
    if args.command in ["send", "encode", "decode"]:
        text_arg = getattr(args, "message", None) or getattr(args, "text", None) or getattr(args, "encoded", None)
        if not text_arg and not sys.stdin.isatty():
            text_arg = sys.stdin.read().strip()

    if args.command == "send":
        return cmd_send(text_arg, args)
    elif args.command == "listen":
        return cmd_listen(args)
    elif args.command == "encode":
        return cmd_encode(text_arg, args)
    elif args.command == "decode":
        return cmd_decode(text_arg, args)
    elif args.command == "status":
        return cmd_status()

    return 0


def cmd_send(message: str, args) -> int:
    """Send command via specified transport."""
    if not message:
        print("Error: No message provided", file=sys.stderr)
        return 1

    if args.transport == "ntfy":
        from ..transports.ntfy import Ntfy
        topic = args.topic or "aidrac"
        ntfy = Ntfy(topic=topic)
        success = ntfy.send(message, title="AIdrac Command")
        print(f"Sent via ntfy/{topic}: {success}")
        return 0 if success else 1

    elif args.transport == "ipoll":
        from ..transports.ipoll_bridge import IPollBridge
        agent = args.topic or "aidrac"
        bridge = IPollBridge(agent_id="aidrac_cli")
        success = bridge.send(agent, message)
        print(f"Sent via I-Poll to {agent}: {success}")
        return 0 if success else 1

    elif args.transport == "ultrasonic":
        from ..protocols.ultrasonic import Ultrasonic, UltrasonicMode
        mode = UltrasonicMode(args.mode)
        ultra = Ultrasonic(mode=mode)
        audio = ultra.encode(message.encode())
        # Output raw audio to stdout for piping
        sys.stdout.buffer.write(audio.tobytes())
        return 0

    elif args.transport == "dtmf":
        from ..protocols.dtmf import DTMF
        dtmf = DTMF()
        audio = dtmf.generate(message)
        sys.stdout.buffer.write(audio.tobytes())
        return 0

    return 1


def cmd_listen(args) -> int:
    """Listen for commands."""
    if args.transport == "ntfy":
        from ..transports.ntfy import Ntfy
        topic = args.topic or "aidrac"
        ntfy = Ntfy(topic=topic)
        print(f"Listening on ntfy/{topic}...", file=sys.stderr)
        for msg in ntfy.listen():
            print(msg.message)
            if args.execute:
                import os
                os.system(msg.message)

    elif args.transport == "ipoll":
        from ..transports.ipoll_bridge import IPollBridge
        agent = args.topic or "aidrac"
        bridge = IPollBridge(agent_id=agent)
        print(f"Listening on I-Poll as {agent}...", file=sys.stderr)
        for msg in bridge.listen():
            print(msg.content)
            if args.execute:
                import os
                os.system(msg.content)

    return 0


def cmd_encode(text: str, args) -> int:
    """Encode text to specified format."""
    if not text:
        print("Error: No text provided", file=sys.stderr)
        return 1

    if args.format == "morse":
        from mcp_server_sensory.encoders.morse import encode
        print(encode(text))
    elif args.format == "morse_visual":
        from mcp_server_sensory.encoders.morse import encode, MorseFormat
        print(encode(text, MorseFormat.VISUAL))
    elif args.format == "braille":
        from mcp_server_sensory.encoders.braille import encode
        print(encode(text))
    elif args.format == "dtmf":
        from ..protocols.dtmf import DTMF
        print(DTMF.from_text(text))

    return 0


def cmd_decode(encoded: str, args) -> int:
    """Decode from specified format."""
    if not encoded:
        print("Error: No encoded text provided", file=sys.stderr)
        return 1

    if args.format == "morse":
        from mcp_server_sensory.encoders.morse import decode
        print(decode(encoded))
    elif args.format == "braille":
        from mcp_server_sensory.encoders.braille import decode
        print(decode(encoded))
    elif args.format == "dtmf":
        from ..protocols.dtmf import DTMF
        print(DTMF().to_text(encoded))

    return 0


def cmd_status() -> int:
    """Show AIdrac status."""
    print("AIdrac v0.1.0 - AI Out-of-Band Management")
    print("=" * 40)
    print("\nTransports:")
    print("  ntfy:       Available")
    print("  I-Poll:     Available")
    print("  DTMF:       Available")
    print("  Ultrasonic: Available")
    print("\nFormats:")
    print("  Morse:      Available")
    print("  Braille:    Available")
    print("\nPart of HumoticaOS McMurdo Off-Grid Layer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
