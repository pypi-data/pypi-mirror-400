"""
DTMF - Dual-Tone Multi-Frequency Protocol
==========================================

Telephone signaling for remote system control.
Used by every phone since the 1960s.

DTMF Frequencies:
        1209 Hz  1336 Hz  1477 Hz  1633 Hz
697 Hz    1        2        3        A
770 Hz    4        5        6        B
852 Hz    7        8        9        C
941 Hz    *        0        #        D

Features:
- Generate DTMF tones for transmission
- Decode DTMF from audio input
- Command mapping (e.g., "1" = boot linux)
- Timing control for reliable detection

Usage:
    dtmf = DTMF()

    # Generate tones
    audio = dtmf.generate("123#")

    # Decode from audio
    digits = dtmf.decode(audio_samples)

    # Map to commands
    dtmf.register_command("1", "grub-select linux")
    dtmf.register_command("2", "grub-select recovery")
    dtmf.register_command("*0#", "power-cycle")
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Dict, List, Tuple

class DTMFTone(Enum):
    """DTMF digit enumeration with frequencies."""
    D1 = ("1", 697, 1209)
    D2 = ("2", 697, 1336)
    D3 = ("3", 697, 1477)
    DA = ("A", 697, 1633)
    D4 = ("4", 770, 1209)
    D5 = ("5", 770, 1336)
    D6 = ("6", 770, 1477)
    DB = ("B", 770, 1633)
    D7 = ("7", 852, 1209)
    D8 = ("8", 852, 1336)
    D9 = ("9", 852, 1477)
    DC = ("C", 852, 1633)
    DSTAR = ("*", 941, 1209)
    D0 = ("0", 941, 1336)
    DHASH = ("#", 941, 1477)
    DD = ("D", 941, 1633)

    def __init__(self, digit: str, low_freq: int, high_freq: int):
        self.digit = digit
        self.low_freq = low_freq
        self.high_freq = high_freq


# Frequency lookup tables
LOW_FREQS = [697, 770, 852, 941]
HIGH_FREQS = [1209, 1336, 1477, 1633]

DTMF_MAP = {
    (697, 1209): "1", (697, 1336): "2", (697, 1477): "3", (697, 1633): "A",
    (770, 1209): "4", (770, 1336): "5", (770, 1477): "6", (770, 1633): "B",
    (852, 1209): "7", (852, 1336): "8", (852, 1477): "9", (852, 1633): "C",
    (941, 1209): "*", (941, 1336): "0", (941, 1477): "#", (941, 1633): "D",
}

CHAR_TO_FREQS = {v: k for k, v in DTMF_MAP.items()}


@dataclass
class DTMFConfig:
    """DTMF timing and audio configuration."""
    sample_rate: int = 44100
    tone_duration_ms: int = 100      # Duration of each tone
    silence_duration_ms: int = 50    # Gap between tones
    amplitude: float = 0.5           # 0.0 to 1.0
    detection_threshold: float = 0.1  # Minimum amplitude for detection


class DTMF:
    """
    DTMF encoder/decoder for telephone-based remote control.

    Example:
        dtmf = DTMF()

        # Generate audio for transmission
        audio = dtmf.generate("123*#")

        # Decode received audio
        digits = dtmf.decode(received_audio)

        # Execute mapped command
        dtmf.register_command("*1#", lambda: os.system("reboot"))
        dtmf.process(digits)
    """

    def __init__(self, config: Optional[DTMFConfig] = None):
        self.config = config or DTMFConfig()
        self.commands: Dict[str, Callable] = {}
        self._buffer: str = ""

    def generate(self, digits: str) -> np.ndarray:
        """
        Generate DTMF audio for a sequence of digits.

        Args:
            digits: String of DTMF digits (0-9, A-D, *, #)

        Returns:
            numpy array of audio samples
        """
        samples = []

        tone_samples = int(self.config.sample_rate * self.config.tone_duration_ms / 1000)
        silence_samples = int(self.config.sample_rate * self.config.silence_duration_ms / 1000)

        t = np.linspace(0, self.config.tone_duration_ms / 1000, tone_samples, False)
        silence = np.zeros(silence_samples)

        for digit in digits.upper():
            if digit in CHAR_TO_FREQS:
                low_freq, high_freq = CHAR_TO_FREQS[digit]

                # Generate dual-tone
                tone = (
                    np.sin(2 * np.pi * low_freq * t) +
                    np.sin(2 * np.pi * high_freq * t)
                ) * self.config.amplitude / 2

                samples.extend(tone)
                samples.extend(silence)
            elif digit == " ":
                # Extra pause for spaces
                samples.extend(np.zeros(silence_samples * 3))

        return np.array(samples, dtype=np.float32)

    def decode(self, audio: np.ndarray, sample_rate: Optional[int] = None) -> str:
        """
        Decode DTMF digits from audio samples.

        Uses Goertzel algorithm for efficient frequency detection.

        Args:
            audio: numpy array of audio samples
            sample_rate: Sample rate (uses config if not specified)

        Returns:
            String of detected digits
        """
        sr = sample_rate or self.config.sample_rate
        detected = []

        # Process in chunks
        chunk_size = int(sr * self.config.tone_duration_ms / 1000)

        for i in range(0, len(audio) - chunk_size, chunk_size // 2):
            chunk = audio[i:i + chunk_size]

            # Detect frequencies using Goertzel
            low_powers = [self._goertzel(chunk, f, sr) for f in LOW_FREQS]
            high_powers = [self._goertzel(chunk, f, sr) for f in HIGH_FREQS]

            # Find dominant frequencies
            max_low_idx = np.argmax(low_powers)
            max_high_idx = np.argmax(high_powers)

            # Check if signal is strong enough
            if (low_powers[max_low_idx] > self.config.detection_threshold and
                high_powers[max_high_idx] > self.config.detection_threshold):

                freq_pair = (LOW_FREQS[max_low_idx], HIGH_FREQS[max_high_idx])
                if freq_pair in DTMF_MAP:
                    digit = DTMF_MAP[freq_pair]

                    # Avoid duplicate detection
                    if not detected or detected[-1] != digit:
                        detected.append(digit)

        return "".join(detected)

    def _goertzel(self, samples: np.ndarray, target_freq: float, sample_rate: int) -> float:
        """
        Goertzel algorithm for efficient single-frequency detection.
        More efficient than FFT for detecting specific frequencies.
        """
        n = len(samples)
        k = int(0.5 + n * target_freq / sample_rate)
        w = 2 * np.pi * k / n
        coeff = 2 * np.cos(w)

        s_prev = 0.0
        s_prev2 = 0.0

        for sample in samples:
            s = sample + coeff * s_prev - s_prev2
            s_prev2 = s_prev
            s_prev = s

        power = s_prev2**2 + s_prev**2 - coeff * s_prev * s_prev2
        return np.sqrt(abs(power)) / n

    def register_command(self, sequence: str, handler: Callable) -> None:
        """
        Register a command handler for a DTMF sequence.

        Args:
            sequence: DTMF digit sequence (e.g., "*1#")
            handler: Function to call when sequence is detected
        """
        self.commands[sequence.upper()] = handler

    def process(self, digits: str) -> Optional[str]:
        """
        Process detected digits and execute matching commands.

        Args:
            digits: Detected DTMF digits

        Returns:
            Command name if executed, None otherwise
        """
        self._buffer += digits.upper()

        # Check for matching commands
        for seq, handler in self.commands.items():
            if self._buffer.endswith(seq):
                handler()
                self._buffer = ""
                return seq

        # Prevent buffer overflow
        if len(self._buffer) > 50:
            self._buffer = self._buffer[-20:]

        return None

    def to_text(self, digits: str) -> str:
        """
        Convert DTMF digits to text using phone keypad mapping.

        2=ABC, 3=DEF, 4=GHI, 5=JKL, 6=MNO, 7=PQRS, 8=TUV, 9=WXYZ
        Multiple presses select different letters.
        """
        keypad = {
            "2": "ABC", "3": "DEF", "4": "GHI", "5": "JKL",
            "6": "MNO", "7": "PQRS", "8": "TUV", "9": "WXYZ",
            "0": " ", "1": ".,!?", "*": "*", "#": "#"
        }

        result = []
        i = 0
        while i < len(digits):
            digit = digits[i]
            if digit in keypad:
                # Count consecutive same digits
                count = 1
                while i + count < len(digits) and digits[i + count] == digit:
                    count += 1

                chars = keypad[digit]
                char_idx = (count - 1) % len(chars)
                result.append(chars[char_idx])
                i += count
            else:
                i += 1

        return "".join(result)

    @staticmethod
    def from_text(text: str) -> str:
        """
        Convert text to DTMF sequence using phone keypad mapping.
        """
        keypad_reverse = {}
        keypad = {
            "2": "ABC", "3": "DEF", "4": "GHI", "5": "JKL",
            "6": "MNO", "7": "PQRS", "8": "TUV", "9": "WXYZ",
            "0": " ", "1": ".,!?"
        }

        for digit, chars in keypad.items():
            for i, char in enumerate(chars):
                keypad_reverse[char] = digit * (i + 1)

        result = []
        for char in text.upper():
            if char in keypad_reverse:
                result.append(keypad_reverse[char])
                result.append(" ")  # Pause between chars

        return "".join(result).strip()


# Convenience functions for CLI
def encode(digits: str) -> np.ndarray:
    """Generate DTMF audio."""
    return DTMF().generate(digits)


def decode(audio: np.ndarray, sample_rate: int = 44100) -> str:
    """Decode DTMF from audio."""
    return DTMF().decode(audio, sample_rate)


# Quick test
if __name__ == "__main__":
    dtmf = DTMF()

    print("=== DTMF Test ===")
    print(f"Generating: 123*#")
    audio = dtmf.generate("123*#")
    print(f"Audio samples: {len(audio)}")

    decoded = dtmf.decode(audio)
    print(f"Decoded: {decoded}")

    print(f"\nText 'HELLO' as DTMF: {DTMF.from_text('HELLO')}")
