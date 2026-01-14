"""
Auto-pan example using rydia-core.

This example demonstrates:
- Using LFO as a control signal (not an audio generator)
- Equal-power stereo panning with pan2
- Explicit sample-by-sample parameter modulation

rydia-core does not distinguish between audio-rate and control-rate.
An LFO is simply another signal generator whose output is used as a parameter.
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
    lfo_freq = 0.25  # slow auto-pan
    amp = 0.8

    n_samples = int(sample_rate * duration_sec)

    # ------------------------------------------------------------------
    # DSP objects
    # ------------------------------------------------------------------

    osc = rydia.SinOsc(sample_rate)
    lfo = rydia.Lfo(sample_rate, waveform=0)  # sine LFO

    # Stereo output buffer
    y = np.zeros((n_samples, 2), dtype=np.float32)

    # ------------------------------------------------------------------
    # Sample-by-sample processing
    # ------------------------------------------------------------------

    for n in range(n_samples):
        # Mono source signal
        x = amp * osc.process(carrier_freq)

        # LFO output in [-1, 1]
        pos, _ = lfo.process(lfo_freq)

        # Equal-power stereo panning
        left, right = rydia.pan2(x, pos)

        y[n, 0] = left
        y[n, 1] = right

    # ------------------------------------------------------------------
    # Normalize and write output
    # ------------------------------------------------------------------

    peak = np.max(np.abs(y)) + 1e-12
    y /= peak

    sf.write("auto_pan.wav", y, int(sample_rate))
    print("Wrote auto_pan.wav")


if __name__ == "__main__":
    main()
