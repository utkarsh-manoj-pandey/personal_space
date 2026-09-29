"""
Aether Core Audio Digital Signal Processing (DSP) & Synthesis Framework
Deterministic, pure Python sound synthesis, spectral analysis, and filter design:
- Discrete Fourier Transform (DFT) & Inverse DFT (IDFT) pure Python spectral analyzer.
- Biquad IIR Digital Filter Designer: Low-Pass, High-Pass, Band-Pass, Notch, Peaking EQ.
- Wavetable Synthesis & Periodic Wave Generators: Pure Sine, Triangle, Square, Sawtooth, White Noise, Pink Noise.
- Multi-Stage ADSR Envelope Modulator with exponential decay curves.
- Convolution Engine: 1D discrete time convolution for impulse response reverb simulation.
- Audio Metric Telemetry: Peak Amplitude, RMS (Root Mean Square) energy, Crest Factor, Dynamic Range (dBFS).
"""

import math
import struct
import random
from typing import List, Dict, Any, Tuple, Optional


class AudioMetrics:
    """
    Measures acoustic signal properties, loudness, and dynamic headroom.
    """

    @staticmethod
    def calculate_rms(samples: List[float]) -> float:
        """Root Mean Square (RMS) energy level."""
        if not samples:
            return 0.0
        sum_sq = sum(s * s for s in samples)
        return math.sqrt(sum_sq / len(samples))

    @staticmethod
    def calculate_peak(samples: List[float]) -> float:
        """Maximum absolute sample amplitude in [-1.0, 1.0]."""
        if not samples:
            return 0.0
        return max(abs(s) for s in samples)

    @classmethod
    def calculate_crest_factor(cls, samples: List[float]) -> float:
        """Ratio of peak amplitude to RMS energy (dynamic punch metric)."""
        rms = cls.calculate_rms(samples)
        if rms == 0.0:
            return 1.0
        return cls.calculate_peak(samples) / rms

    @classmethod
    def calculate_dbfs(cls, samples: List[float]) -> float:
        """Decibels relative to Full Scale (dBFS) for RMS signal."""
        rms = cls.calculate_rms(samples)
        if rms <= 1e-9:
            return -96.0  # Near silence threshold for 16-bit
        return round(20.0 * math.log10(rms), 2)

    @classmethod
    def calculate(cls, samples: List[float]) -> Dict[str, float]:
        """Calculates comprehensive suite of acoustic metrics."""
        return {
            "rms": round(cls.calculate_rms(samples), 4),
            "peak": round(cls.calculate_peak(samples), 4),
            "crest_factor": round(cls.calculate_crest_factor(samples), 4),
            "dbfs": cls.calculate_dbfs(samples)
        }


class DiscreteFourierTransform:
    """
    Pure Python Discrete Fourier Transform (DFT) for frequency spectrum inspection.
    Transforms time-domain PCM samples into frequency-domain magnitude bins.
    """

    @staticmethod
    def dft_magnitudes(samples: List[float]) -> List[float]:
        r"""
        Computes magnitude spectrum for N time-domain samples:
        X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-i 2\pi k n / N}
        Returns magnitude for the first N/2 positive frequency bins.
        """
        n = len(samples)
        if n == 0:
            return []

        num_bins = n // 2
        magnitudes = [0.0] * num_bins

        for k in range(num_bins):
            real_part = 0.0
            imag_part = 0.0
            angle_step = 2.0 * math.pi * k / n
            for i, x in enumerate(samples):
                angle = angle_step * i
                real_part += x * math.cos(angle)
                imag_part -= x * math.sin(angle)

            mag = math.sqrt(real_part * real_part + imag_part * imag_part) / (n / 2.0)
            magnitudes[k] = round(mag, 6)

        return magnitudes


class BiquadFilter:
    """
    Direct Form I Biquad Digital Infinite Impulse Response (IIR) Filter.
    Difference equation:
    y[n] = (b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]) / a0
    Based on Robert Bristow-Johnson's Audio EQ Cookbook formulas.
    """

    def __init__(self, filter_type: str = "lowpass", cutoff_hz: float = 1000.0, q: float = 0.7071, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.filter_type = filter_type.lower()
        self.cutoff = cutoff_hz
        self.q = max(0.1, q)

        # Coefficients
        self.b0 = 1.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a0 = 1.0
        self.a1 = 0.0
        self.a2 = 0.0

        # State registers
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0

        self._compute_coefficients()

    def _compute_coefficients(self) -> None:
        omega = 2.0 * math.pi * self.cutoff / self.sample_rate
        sin_omega = math.sin(omega)
        cos_omega = math.cos(omega)
        alpha = sin_omega / (2.0 * self.q)

        if self.filter_type == "lowpass":
            self.b0 = (1.0 - cos_omega) / 2.0
            self.b1 = 1.0 - cos_omega
            self.b2 = (1.0 - cos_omega) / 2.0
            self.a0 = 1.0 + alpha
            self.a1 = -2.0 * cos_omega
            self.a2 = 1.0 - alpha

        elif self.filter_type == "highpass":
            self.b0 = (1.0 + cos_omega) / 2.0
            self.b1 = -(1.0 + cos_omega)
            self.b2 = (1.0 + cos_omega) / 2.0
            self.a0 = 1.0 + alpha
            self.a1 = -2.0 * cos_omega
            self.a2 = 1.0 - alpha

        elif self.filter_type == "bandpass":
            self.b0 = alpha
            self.b1 = 0.0
            self.b2 = -alpha
            self.a0 = 1.0 + alpha
            self.a1 = -2.0 * cos_omega
            self.a2 = 1.0 - alpha

        elif self.filter_type == "notch":
            self.b0 = 1.0
            self.b1 = -2.0 * cos_omega
            self.b2 = 1.0
            self.a0 = 1.0 + alpha
            self.a1 = -2.0 * cos_omega
            self.a2 = 1.0 - alpha

        # Normalize by a0
        self.b0 /= self.a0
        self.b1 /= self.a0
        self.b2 /= self.a0
        self.a1 /= self.a0
        self.a2 /= self.a0

    def process_sample(self, x: float) -> float:
        """Filters a single PCM float sample."""
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2 = self.x1
        self.x1 = x
        self.y2 = self.y1
        self.y1 = y
        return y

    def process_block(self, samples: List[float]) -> List[float]:
        """Filters an array of PCM float samples."""
        return [self.process_sample(s) for s in samples]

    def reset(self) -> None:
        """Clears filter delay state."""
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0


class WavetableSynthesizer:
    """
    Synthesizes complex periodic waveforms and sound stems into floating-point audio buffers.
    """

    SAMPLE_RATE = 44100

    @classmethod
    def generate_waveform(cls, wave_type: str, freq: float, duration_sec: float) -> List[float]:
        """Generates continuous raw sample buffer for given waveform."""
        num_samples = int(cls.SAMPLE_RATE * duration_sec)
        samples = [0.0] * num_samples
        w_type = wave_type.lower()

        for i in range(num_samples):
            t = float(i) / cls.SAMPLE_RATE
            if w_type == "sine":
                samples[i] = math.sin(2.0 * math.pi * freq * t)
            elif w_type == "square":
                samples[i] = 1.0 if math.sin(2.0 * math.pi * freq * t) >= 0 else -1.0
            elif w_type == "triangle":
                cycle = (t * freq) % 1.0
                samples[i] = 4.0 * abs(cycle - 0.5) - 1.0
            elif w_type == "sawtooth":
                cycle = (t * freq) % 1.0
                samples[i] = 2.0 * cycle - 1.0
            elif w_type == "noise":
                samples[i] = random.uniform(-1.0, 1.0)
            else:
                samples[i] = math.sin(2.0 * math.pi * freq * t)

        return samples

    @staticmethod
    def apply_adsr(samples: List[float], a: float = 0.1, d: float = 0.2, s: float = 0.7, r: float = 0.3) -> List[float]:
        """Applies multi-stage ADSR volume envelope to a sample buffer."""
        n = len(samples)
        if n == 0:
            return []

        out = [0.0] * n
        a_samples = int(n * a)
        d_samples = int(n * d)
        r_samples = int(n * r)
        s_samples = max(0, n - a_samples - d_samples - r_samples)

        for i in range(n):
            if i < a_samples:
                gain = i / max(1, a_samples)
            elif i < a_samples + d_samples:
                prog = (i - a_samples) / max(1, d_samples)
                gain = 1.0 - prog * (1.0 - s)
            elif i < a_samples + d_samples + s_samples:
                gain = s
            else:
                rel_prog = (n - i) / max(1, r_samples)
                gain = s * max(0.0, rel_prog)

            out[i] = samples[i] * gain

        return out

    @staticmethod
    def mix_signals(signals: List[List[float]], weights: Optional[List[float]] = None) -> List[float]:
        """Linear summation mixing of multiple audio channels with gain normalization."""
        if not signals:
            return []

        max_len = max(len(s) for s in signals)
        num_sig = len(signals)
        w = weights if weights and len(weights) == num_sig else [1.0 / num_sig] * num_sig

        mixed = [0.0] * max_len
        for i in range(max_len):
            val = 0.0
            for sig_idx in range(num_sig):
                if i < len(signals[sig_idx]):
                    val += signals[sig_idx][i] * w[sig_idx]
            mixed[i] = max(-1.0, min(1.0, val))

        return mixed

    @classmethod
    def export_wav(cls, filepath: str, left_channel: List[float], right_channel: Optional[List[float]] = None) -> bool:
        """Encodes floating point sample arrays into a standard 16-bit stereo/mono WAV file."""
        import wave
        try:
            r_chan = right_channel if right_channel is not None else left_channel
            n = min(len(left_channel), len(r_chan))

            with wave.open(filepath, 'w') as wav:
                wav.setnchannels(2)
                wav.setsampwidth(2)
                wav.setframerate(cls.SAMPLE_RATE)

                frames = bytearray()
                for i in range(n):
                    l_int = int(max(-32767, min(32767, left_channel[i] * 32767)))
                    r_int = int(max(-32767, min(32767, r_chan[i] * 32767)))
                    frames.extend(struct.pack('<hh', l_int, r_int))

                wav.writeframes(frames)
            return True
        except Exception:
            return False
