#!/usr/bin/env python3
"""aidrac-notify - Send ntfy notifications"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Send ntfy notifications")
    parser.add_argument("message", nargs="?", help="Message (or stdin)")
    parser.add_argument("-t", "--topic", default="aidrac", help="ntfy topic")
    parser.add_argument("-s", "--server", default="https://ntfy.sh", help="ntfy server")
    parser.add_argument("--title", help="Notification title")
    parser.add_argument("-p", "--priority", choices=["min", "low", "default", "high", "urgent"],
                       default="default", help="Priority level")
    parser.add_argument("--tags", help="Comma-separated emoji tags")
    args = parser.parse_args()

    message = args.message or sys.stdin.read().strip()
    if not message:
        print("Error: No message provided", file=sys.stderr)
        return 1

    from ..transports.ntfy import Ntfy, NtfyConfig

    config = NtfyConfig(server=args.server)
    ntfy = Ntfy(topic=args.topic, config=config)

    tags = args.tags.split(",") if args.tags else None
    success = ntfy.send(message, title=args.title, priority=args.priority, tags=tags)

    if success:
        print(f"Sent to {args.server}/{args.topic}")
    else:
        print("Failed to send", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
