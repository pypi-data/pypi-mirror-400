"""
Chorus example using rydia-core.

This example demonstrates:
- A simple chorus built from a modulated fractional delay
- Using LFO to modulate delay time
- Explicit, sample-by-sample DSP composition

This is intentionally a minimal chorus implementation.
It is not meant to be a production-ready effect, but a clear example
of how rydia-core primitives can be combined.
"""

import numpy as np
import soundfile as sf

import rydia


def main():
    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    sample_rate = 48_000.0
    duration_sec = 6.0

    carrier_freq = 440.0
    amp = 0.7

    # Chorus parameters
    base_delay_sec = 0.02  # 20 ms
    depth_sec = 0.005  # ±5 ms modulation
    lfo_freq = 0.3  # slow modulation

    n_samples = int(sample_rate * duration_sec)

    # ------------------------------------------------------------------
    # DSP objects
    # ------------------------------------------------------------------

    osc = rydia.SinOsc(sample_rate)
    lfo = rydia.Lfo(sample_rate, waveform=0)  # sine LFO

    # Fractional delay line
    delay = rydia.DelayL(sample_rate, max_delay_sec=0.05)

    # Output buffer (mono)
    y = np.zeros(n_samples, dtype=np.float32)

    # ------------------------------------------------------------------
    # Sample-by-sample processing
    # ------------------------------------------------------------------

    for n in range(n_samples):
        # Dry signal
        x = amp * osc.process(carrier_freq)

        # LFO output in [-1, 1]
        mod, _ = lfo.process(lfo_freq)

        # Modulated delay time
        delay_time = base_delay_sec + depth_sec * mod

        # Chorus output (simple wet-only)
        y[n] = delay.process(x, delay_time)

    # ------------------------------------------------------------------
    # Normalize and write output
    # ------------------------------------------------------------------

    y /= np.max(np.abs(y) + 1e-12)

    sf.write("chorus.wav", y, int(sample_rate))
    print("Wrote chorus.wav")


if __name__ == "__main__":
    main()
