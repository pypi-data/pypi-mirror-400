#!/usr/bin/env python3
"""aidrac-dtmf - DTMF encoder/decoder"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="DTMF encode/decode")
    parser.add_argument("action", choices=["encode", "decode", "generate"])
    parser.add_argument("input", nargs="?")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()

    from ..protocols.dtmf import DTMF
    dtmf = DTMF()

    text = args.input or sys.stdin.read().strip()

    if args.action == "encode":
        print(DTMF.from_text(text))
    elif args.action == "decode":
        print(dtmf.to_text(text))
    elif args.action == "generate":
        audio = dtmf.generate(text)
        if args.output:
            audio.tofile(args.output)
        else:
            sys.stdout.buffer.write(audio.tobytes())

if __name__ == "__main__":
    sys.exit(main())
