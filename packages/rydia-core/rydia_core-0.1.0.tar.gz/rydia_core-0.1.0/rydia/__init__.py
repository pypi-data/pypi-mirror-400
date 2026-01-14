"""
rydia-core
==========

rydia-core is a minimal, stateful DSP building-block library.

This package provides low-level, sample-by-sample DSP primitives
implemented in Rust and exposed to Python via PyO3. It is designed
for experimentation, prototyping, and offline signal processing,
rather than real-time audio callback usage from Python.

Design goals
------------

- Provide **stateful DSP primitives** (UGen-like objects)
- Keep the public API **small, explicit, and stable**
- Separate **signal execution** from **filter or system design**
- Favor clarity and correctness over feature completeness

Out of scope
------------

rydia-core intentionally does NOT include:

- Filter design utilities (e.g. RBJ coefficient generation)
- FFT / STFT / block-based processing
- High-level synthesis graphs or schedulers
- Real-time audio I/O abstractions

These concerns are expected to live in companion libraries
(e.g. polaris-audio) or in user code.

Public API
----------

The symbols exported via ``__all__`` constitute the stable public API
for rydia-core v0.1.x. Any symbol not listed there should be considered
internal and subject to change without notice.

Overview of provided primitives
--------------------------------

Oscillators and signal sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``SinOsc``      : Phase-accumulating sine oscillator
- ``Lfo``         : Low-frequency oscillator with multiple waveforms
- ``WhiteNoise``  : Stateless white noise generator producing
                    uniformly distributed random samples in [-1, 1]

Buffers and delays
~~~~~~~~~~~~~~~~~~
- ``RingBufferS`` : Sample-based ring buffer
- ``RingBufferN`` : Time-based ring buffer (seconds)
- ``RingBufferL`` : Time-based ring buffer with linear interpolation

- ``DelayS``      : Integer-sample delay
- ``DelayN``      : Time-based delay (no interpolation)
- ``DelayL``      : Time-based delay with linear interpolation

- ``CombS`` / ``CombN`` / ``CombL``          : Comb filters
- ``AllpassS`` / ``AllpassN`` / ``AllpassL`` : Allpass filters

Filters
~~~~~~~
- ``Biquad``      : Generic biquad filter executor (no design logic)

Utilities
~~~~~~~~~
- ``LeakDc``      : DC blocker for removing DC offset after nonlinear processing
- ``pan2``        : Equal-power mono-to-stereo panner

Notes
-----

rydia-core focuses on *how signals are processed*, not *how systems are designed*.
For filter design, state-space models, control-theoretic DSP, or coefficient
generation, see companion projects such as ``polaris-audio``.
"""

from .rydia import (
    AllpassL,
    AllpassN,
    AllpassS,
    Biquad,
    CombL,
    CombN,
    CombS,
    DelayL,
    DelayN,
    DelayS,
    LeakDc,
    Lfo,
    RingBufferL,
    RingBufferN,
    RingBufferS,
    SinOsc,
    WhiteNoise,
    pan2,
)

__all__ = [
    "AllpassL",
    "AllpassN",
    "AllpassS",
    "Biquad",
    "CombL",
    "CombN",
    "CombS",
    "DelayL",
    "DelayN",
    "DelayS",
    "LeakDc",
    "Lfo",
    "RingBufferL",
    "RingBufferN",
    "RingBufferS",
    "SinOsc",
    "WhiteNoise",
    "pan2",
]
