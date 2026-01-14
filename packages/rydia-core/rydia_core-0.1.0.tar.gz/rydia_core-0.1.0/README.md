# rydia-core

**rydia-core** is a Rust-based DSP library providing small, composable UGens for offline audio experimentation, with Python bindings via PyO3.  
The library focuses on explicit state, sample-by-sample processing, and numerically robust building blocks inspired by SuperCollider UGens and classic DSP literature.

rydia-core is designed for experimentation, analysis, and algorithmic sound construction rather than real-time audio I/O or plugin development.

---

## Minimal example

### 1. Sine oscillator

```python
import rydia

osc = rydia.SinOsc(48000.0)

samples = []
for _ in range(48000):
    samples.append(osc.process(440.0))
```

This produces one second of a 440 Hz sine wave at 48 kHz.

### 2. LFO-driven auto pan

```python
import rydia

lfo = rydia.Lfo(48000.0, waveform=0)  # sine LFO
signal = 0.5

for _ in range(10):
    mod, _ = lfo.process(0.25)
    left, right = rydia.pan2(signal, mod)
    print(left, right)
```

The LFO output is used as a stereo pan modulation signal.

### 3. Delay line

```python
import rydia

delay = rydia.DelayL(48000.0, 1.0)

for i in range(10):
    y = delay.process(float(i), 0.1)
    print(y)
```

This applies a fractional delay using linear interpolation.

For more advanced usage and complete examples, see the `examples/` directory.

---

## Provided UGens

### Oscillators

- `SinOsc`  
  Phase-accumulating sine oscillator.

- `WhiteNoise`  
  Uniform white noise generator in the range [-1, 1].

### Low-frequency modulation

- `Lfo`  
  Sine / triangle / saw LFO with an additional quarter-phase output.

### Delay-based primitives

- `DelayS`, `DelayN`, `DelayL`  
  Sample, nearest-neighbor, and linearly interpolated delays.

- `CombS`, `CombN`, `CombL`  
  Feedback comb filters.

- `AllpassS`, `AllpassN`, `AllpassL`  
  Allpass filters based on SuperCollider-style formulations.

### Filters and utilities

- `Biquad`  
  Transposed Direct Form II biquad executor.  
  Accepts already-normalized coefficients (RBJ-compatible).

- `LeakDc`  
  DC-blocking filter (high-pass) useful after rectifiers and nonlinearities.

- `RingBufferS`, `RingBufferN`, `RingBufferL`  
  Power-of-two ring buffers for delay-based structures.

- `pan2`  
  Equal-power stereo panner.

---

## Design principles

- Explicit state, no hidden global context
- Sample-by-sample processing
- Deterministic behavior
- Defensive testing against numerical instability
- Rust as the source of truth for DSP logic

Python is treated as a thin orchestration and experimentation layer.

---

## Non-goals

rydia-core intentionally does not provide:

- Real-time audio I/O
- Plugin formats (VST, AU, AAX)
- High-level synthesis graphs, schedulers, or DAW-like workflows
- Automatic filter design helpers or large DSP toolkits

Those concerns are expected to live in higher-level systems.

---

## Project status

- Python >= 3.10
- Rust core with Python bindings
- Offline / non-realtime oriented
- Experimental / research-focused
- API may evolve within 0.1.x

rydia-core favors clarity and composability over completeness or convenience.
