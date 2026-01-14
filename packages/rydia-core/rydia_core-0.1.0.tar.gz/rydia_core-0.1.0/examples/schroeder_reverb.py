"""
Schroeder reverb example using rydia-core.

This example demonstrates:
- Classic Schroeder reverb structure
- Parallel comb filters + series allpass filters
- How rydia-core provides DSP primitives, not effect abstractions

This is an offline, sample-by-sample rendering example.
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

    input_freq = 440.0
    input_amp = 0.5

    n_samples = int(sample_rate * duration_sec)

    # ------------------------------------------------------------------
    # Input signal (simple sine)
    # ------------------------------------------------------------------

    osc = rydia.SinOsc(sample_rate)
    x = np.zeros(n_samples, dtype=np.float32)

    for n in range(n_samples):
        x[n] = input_amp * osc.process(input_freq)

    # ------------------------------------------------------------------
    # Schroeder reverb design
    # ------------------------------------------------------------------
    # Parallel comb filters
    #
    # Delay times are chosen to be mutually prime-ish
    # (classic Schroeder design principle)
    # ------------------------------------------------------------------

    comb_delays_sec = [0.0297, 0.0371, 0.0411, 0.0437]
    comb_decay_sec = 3.0

    combs = [rydia.CombN(sample_rate, max_delay_sec=0.1) for _ in comb_delays_sec]

    # ------------------------------------------------------------------
    # Series allpass filters
    # ------------------------------------------------------------------

    allpass_delays_sec = [0.005, 0.0017]
    allpass_decay_sec = 0.7

    allpasses = [rydia.AllpassN(sample_rate, max_delay_sec=0.02) for _ in allpass_delays_sec]

    # ------------------------------------------------------------------
    # Output buffer
    # ------------------------------------------------------------------

    y = np.zeros(n_samples, dtype=np.float32)

    # ------------------------------------------------------------------
    # Sample-by-sample processing
    # ------------------------------------------------------------------

    for n in range(n_samples):
        xn = x[n]

        # Parallel comb section
        comb_sum = 0.0
        for comb, delay in zip(combs, comb_delays_sec):
            comb_sum += comb.process(xn, delay, comb_decay_sec)

        comb_out = comb_sum / len(combs)

        # Series allpass section
        ap_out = comb_out
        for ap, delay in zip(allpasses, allpass_delays_sec):
            ap_out = ap.process(ap_out, delay, allpass_decay_sec)

        y[n] = ap_out

    # ------------------------------------------------------------------
    # Normalize and write output
    # ------------------------------------------------------------------

    y /= np.max(np.abs(y) + 1e-12)

    sf.write("schroeder_reverb.wav", y, int(sample_rate))
    print("Wrote schroeder_reverb.wav")


if __name__ == "__main__":
    main()
