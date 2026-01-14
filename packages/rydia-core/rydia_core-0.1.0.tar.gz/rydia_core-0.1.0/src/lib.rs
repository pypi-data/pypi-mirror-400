//! rydia-core
//!
//! A minimal, low-level DSP primitive library.
//!
//! `rydia-core` provides small, explicit, stateful DSP building blocks inspired by
//! SuperCollider UGens and classic audio DSP literature.
//!
//! The crate is intentionally designed as a *core layer*: it focuses on
//! numerically stable, sample-by-sample DSP execution, while leaving higher-level
//! concerns (graph construction, parameter automation, oversampling strategies,
//! and UI integration) to other libraries.
//!
//! # Design philosophy
//!
//! - **Sample-by-sample processing**
//!   All DSP units operate on a single sample at a time.
//!   Block-based APIs are intentionally avoided to keep semantics explicit.
//!
//! - **Explicit state**
//!   Every DSP unit owns its internal state and exposes reset behavior where appropriate.
//!
//! - **No hidden allocation**
//!   There are no heap allocations on the audio path after construction.
//!
//! - **Numerical predictability**
//!   Implementations favor stable, well-known structures
//!   (e.g. Transposed Direct Form II for biquads).
//!
//! - **Minimal abstraction**
//!   This crate does not provide synthesis graphs, schedulers, or signal routing layers.
//!
//! # Non-goals
//!
//! The following are *explicitly out of scope* for `rydia-core`:
//!
//! - DSP graph frameworks or node networks
//! - Automatic parameter smoothing or modulation systems
//! - Oversampling, resampling, or polyphase SRC frameworks
//! - FIR filter design utilities or windowing toolkits
//!
//! These features are intentionally deferred to higher-level libraries
//! (e.g. `polaris-audio`) or external DSP toolkits.
//!
//! # Provided components
//!
//! - Oscillators (`SinOsc`, `Lfo`, `WhiteNoise`)
//! - Delay-based primitives (`Delay`, `Comb`, `Allpass` variants)
//! - A generic biquad executor (`Biquad`)
//! - DC offset removal (`LeakDc`)
//! - Ring buffers with multiple interpolation strategies
//!
//! Each component is designed to be composable and reusable without enforcing
//! a specific synthesis or processing model.
//!
//! # Python bindings
//!
//! `rydia-core` exposes its API to Python via PyO3.
//! The Python interface mirrors the Rust API closely and is intended for
//! experimentation, prototyping, and offline signal processing rather than
//! real-time audio callback usage.
//!
//! # Stability notes
//!
//! `rydia-core` is currently in the `0.x` development phase.
//! While the public API is intentionally kept small, breaking changes may occur
//! until `1.0.0`.
//!
//! However, semantic meaning and design boundaries established in this crate
//! are considered stable starting from `v0.1.0`.

pub mod delay;
pub mod iir_filter;
pub mod leak_dc;
pub mod lfo;
pub mod osc;
pub mod pan;
pub mod ring_buffer;

use pyo3::prelude::*;

// -----------------------------------------------------------------------------
// Oscillators & noise
// -----------------------------------------------------------------------------
use crate::osc::{SinOsc, WhiteNoise};

// -----------------------------------------------------------------------------
// Modulation
// -----------------------------------------------------------------------------
use crate::lfo::Lfo;

// -----------------------------------------------------------------------------
// Filters
// -----------------------------------------------------------------------------
use crate::iir_filter::Biquad;
use crate::leak_dc::LeakDc;

// -----------------------------------------------------------------------------
// Delay-based effects
// -----------------------------------------------------------------------------
use crate::delay::{AllpassL, AllpassN, AllpassS, CombL, CombN, CombS, DelayL, DelayN, DelayS};

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------
use crate::pan::pan2;
use crate::ring_buffer::{RingBufferL, RingBufferN, RingBufferS};

#[pymodule]
fn rydia(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // -------------------------------------------------------------------------
    // Oscillators & noise
    // -------------------------------------------------------------------------
    m.add_class::<SinOsc>()?;
    m.add_class::<WhiteNoise>()?;

    // -------------------------------------------------------------------------
    // Modulation
    // -------------------------------------------------------------------------
    m.add_class::<Lfo>()?;

    // -------------------------------------------------------------------------
    // Filters
    // -------------------------------------------------------------------------
    m.add_class::<Biquad>()?;
    m.add_class::<LeakDc>()?;

    // -------------------------------------------------------------------------
    // Delay-based effects
    // -------------------------------------------------------------------------
    m.add_class::<DelayS>()?;
    m.add_class::<DelayN>()?;
    m.add_class::<DelayL>()?;

    m.add_class::<CombS>()?;
    m.add_class::<CombN>()?;
    m.add_class::<CombL>()?;

    m.add_class::<AllpassS>()?;
    m.add_class::<AllpassN>()?;
    m.add_class::<AllpassL>()?;

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------
    m.add_function(wrap_pyfunction!(pan2, m)?)?;

    m.add_class::<RingBufferS>()?;
    m.add_class::<RingBufferN>()?;
    m.add_class::<RingBufferL>()?;

    Ok(())
}
