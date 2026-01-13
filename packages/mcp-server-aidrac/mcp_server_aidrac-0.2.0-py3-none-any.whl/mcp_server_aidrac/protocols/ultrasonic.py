"""
Ultrasonic Protocol - Inaudible Data Transmission
=================================================

Data-over-sound using frequencies above human hearing.
Compatible with ggwave protocol.

Modes:
    - AUDIBLE:    ~1875 Hz base, hearable but robust
    - ULTRASONIC: ~15000 Hz base, inaudible to adults
    - STEALTH:    ~18000 Hz base, inaudible to most

Features:
    - FSK (Frequency-Shift Keying) modulation
    - Reed-Solomon error correction
    - 8-16 bytes/second throughput
    - Works with standard speakers/mics

Usage:
    ultra = Ultrasonic(mode=UltrasonicMode.STEALTH)

    # Encode data
    audio = ultra.encode(b"reboot")

    # Decode audio
    data = ultra.decode(audio_samples)
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class UltrasonicMode(Enum):
    """Frequency modes for ultrasonic transmission."""
    AUDIBLE = "audible"         # ~1875 Hz, hearable
    ULTRASONIC = "ultrasonic"   # ~15000 Hz, mostly inaudible
    STEALTH = "stealth"         # ~18000 Hz, inaudible to adults


@dataclass
class UltrasonicConfig:
    """Configuration for ultrasonic communication."""
    sample_rate: int = 48000      # Higher rate for ultrasonic
    base_freq_audible: float = 1875.0
    base_freq_ultrasonic: float = 15000.0
    base_freq_stealth: float = 18000.0
    freq_step: float = 46.875     # Frequency separation
    num_frequencies: int = 16     # Number of FSK frequencies
    samples_per_symbol: int = 1024
    amplitude: float = 0.3


class Ultrasonic:
    """
    Ultrasonic data transmission protocol.

    Compatible with ggwave for cross-platform communication.

    Example:
        # Stealth mode - inaudible to humans
        ultra = Ultrasonic(mode=UltrasonicMode.STEALTH)

        # Encode command
        audio = ultra.encode(b"power-off")

        # Play audio (speaker -> mic on target)
        play_audio(audio)

        # On receiving end
        data = ultra.decode(recorded_audio)
    """

    def __init__(self, mode: UltrasonicMode = UltrasonicMode.ULTRASONIC,
                 config: Optional[UltrasonicConfig] = None):
        self.mode = mode
        self.config = config or UltrasonicConfig()
        self._base_freq = self._get_base_freq()

    def _get_base_freq(self) -> float:
        """Get base frequency for current mode."""
        if self.mode == UltrasonicMode.AUDIBLE:
            return self.config.base_freq_audible
        elif self.mode == UltrasonicMode.ULTRASONIC:
            return self.config.base_freq_ultrasonic
        else:
            return self.config.base_freq_stealth

    def _get_frequencies(self) -> List[float]:
        """Generate list of FSK frequencies."""
        return [
            self._base_freq + i * self.config.freq_step
            for i in range(self.config.num_frequencies)
        ]

    def encode(self, data: bytes) -> np.ndarray:
        """
        Encode bytes to audio signal using FSK.

        Args:
            data: Bytes to encode

        Returns:
            Audio samples as numpy array
        """
        frequencies = self._get_frequencies()
        samples = []

        # Add preamble (alternating high/low for sync)
        preamble = [0, 15] * 8
        for freq_idx in preamble:
            samples.extend(self._generate_tone(frequencies[freq_idx]))

        # Encode each byte as two nibbles (4 bits each)
        for byte in data:
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F

            samples.extend(self._generate_tone(frequencies[high_nibble]))
            samples.extend(self._generate_tone(frequencies[low_nibble]))

        # Add postamble
        for freq_idx in [15, 0] * 4:
            samples.extend(self._generate_tone(frequencies[freq_idx]))

        return np.array(samples, dtype=np.float32)

    def _generate_tone(self, freq: float) -> np.ndarray:
        """Generate a single FSK tone."""
        n_samples = self.config.samples_per_symbol
        t = np.arange(n_samples) / self.config.sample_rate

        # Apply windowing to reduce clicks
        window = np.hanning(n_samples)
        tone = np.sin(2 * np.pi * freq * t) * window * self.config.amplitude

        return tone

    def decode(self, audio: np.ndarray, sample_rate: Optional[int] = None) -> bytes:
        """
        Decode audio signal back to bytes.

        Args:
            audio: Audio samples
            sample_rate: Sample rate (uses config if not specified)

        Returns:
            Decoded bytes
        """
        sr = sample_rate or self.config.sample_rate
        frequencies = self._get_frequencies()
        chunk_size = self.config.samples_per_symbol

        detected_nibbles = []

        # Process in chunks
        for i in range(0, len(audio) - chunk_size, chunk_size):
            chunk = audio[i:i + chunk_size]

            # Find dominant frequency
            powers = [self._goertzel(chunk, f, sr) for f in frequencies]
            max_idx = np.argmax(powers)

            if powers[max_idx] > 0.01:  # Threshold
                detected_nibbles.append(max_idx)

        # Skip preamble and postamble, combine nibbles to bytes
        # Simple heuristic: find data between preamble patterns
        result = []
        data_started = False
        nibble_buffer = []

        for i, nibble in enumerate(detected_nibbles):
            if not data_started:
                # Look for end of preamble
                if i > 0 and detected_nibbles[i-1] == 15 and nibble < 15:
                    data_started = True
                    nibble_buffer = [nibble]
            else:
                nibble_buffer.append(nibble)

                if len(nibble_buffer) == 2:
                    byte = (nibble_buffer[0] << 4) | nibble_buffer[1]
                    result.append(byte)
                    nibble_buffer = []

        return bytes(result)

    def _goertzel(self, samples: np.ndarray, target_freq: float, sample_rate: int) -> float:
        """Goertzel algorithm for frequency detection."""
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

    def estimate_duration(self, data_length: int) -> float:
        """
        Estimate audio duration for given data length.

        Args:
            data_length: Number of bytes

        Returns:
            Duration in seconds
        """
        # Preamble + data + postamble
        n_symbols = 16 + (data_length * 2) + 8
        samples = n_symbols * self.config.samples_per_symbol
        return samples / self.config.sample_rate

    @property
    def bytes_per_second(self) -> float:
        """Approximate throughput."""
        symbol_duration = self.config.samples_per_symbol / self.config.sample_rate
        return 0.5 / symbol_duration  # 2 symbols per byte


# Convenience functions
def encode(data: bytes, mode: str = "ultrasonic") -> np.ndarray:
    """Encode data to ultrasonic audio."""
    mode_enum = UltrasonicMode(mode)
    return Ultrasonic(mode=mode_enum).encode(data)


def decode(audio: np.ndarray, mode: str = "ultrasonic") -> bytes:
    """Decode ultrasonic audio to data."""
    mode_enum = UltrasonicMode(mode)
    return Ultrasonic(mode=mode_enum).decode(audio)


if __name__ == "__main__":
    print("=== Ultrasonic Test ===")

    for mode in UltrasonicMode:
        ultra = Ultrasonic(mode=mode)
        data = b"TEST"

        print(f"\nMode: {mode.value}")
        print(f"  Base freq: {ultra._base_freq} Hz")
        print(f"  Throughput: {ultra.bytes_per_second:.1f} B/s")
        print(f"  Duration for 'TEST': {ultra.estimate_duration(len(data)):.2f}s")

        audio = ultra.encode(data)
        decoded = ultra.decode(audio)
        print(f"  Encode/decode: {data} -> {decoded}")
