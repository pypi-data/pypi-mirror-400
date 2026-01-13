#!/usr/bin/env python3
"""aidrac-tone - Generate/detect audio tones"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Audio tone generation/detection")
    parser.add_argument("action", choices=["generate", "detect"])
    parser.add_argument("-f", "--freq", type=float, default=1000, help="Frequency in Hz")
    parser.add_argument("-d", "--duration", type=float, default=1.0, help="Duration in seconds")
    parser.add_argument("-m", "--mode", choices=["audible", "ultrasonic", "stealth"], default="audible")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()

    import numpy as np

    if args.action == "generate":
        sample_rate = 48000
        t = np.linspace(0, args.duration, int(sample_rate * args.duration), False)
        tone = (np.sin(2 * np.pi * args.freq * t) * 0.5).astype(np.float32)

        if args.output:
            tone.tofile(args.output)
        else:
            sys.stdout.buffer.write(tone.tobytes())

    print(f"Generated {args.freq}Hz tone for {args.duration}s", file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
