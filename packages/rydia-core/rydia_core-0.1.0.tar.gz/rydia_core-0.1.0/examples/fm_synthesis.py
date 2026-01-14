"""
FM synthesis example using rydia-core.

This example demonstrates:
- Sample-by-sample DSP processing
- Frequency modulation using SinOsc
- Offline (non-realtime) audio rendering in Python

rydia-core is intentionally low-level: there is no signal graph or block processing.
Each oscillator is advanced explicitly per sample.
"""

import numpy as np
import soundfile as sf

import rydia


def main():
    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    sample_rate = 48_000.0
    duration_sec = 5.0

    carrier_freq = 440.0
    modulator_freq = 220.0
    modulation_index = 200.0

    n_samples = int(sample_rate * duration_sec)

    # ------------------------------------------------------------------
    # DSP objects
    # ------------------------------------------------------------------

    carrier = rydia.SinOsc(sample_rate)
    modulator = rydia.SinOsc(sample_rate)

    # Output buffer
    y = np.zeros(n_samples, dtype=np.float32)

    # ------------------------------------------------------------------
    # Sample-by-sample synthesis
    # ------------------------------------------------------------------

    for n in range(n_samples):
        # Modulator output
        mod = modulator.process(modulator_freq)

        # Instantaneous frequency modulation
        freq = carrier_freq + modulation_index * mod

        # Carrier output
        y[n] = carrier.process(freq)

    # ------------------------------------------------------------------
    # Normalize and write output
    # ------------------------------------------------------------------

    y /= np.max(np.abs(y) + 1e-12)

    sf.write("fm_synthesis.wav", y, int(sample_rate))
    print("Wrote fm_synthesis.wav")


if __name__ == "__main__":
    main()
