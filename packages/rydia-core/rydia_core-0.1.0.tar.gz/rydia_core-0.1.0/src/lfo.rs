use pyo3::prelude::*;
use std::f32::consts::PI;

/// Constants used for the parabolic sine approximation.
///
/// This approximation is commonly used in audio DSP to
/// generate sine-like waveforms efficiently.
const B: f32 = 4.0 / PI;
const C: f32 = -4.0 / (PI * PI);
const P: f32 = 0.225;

/// Fast parabolic sine approximation.
///
/// This function approximates `sin(x)` with low computational cost.
/// The output may slightly exceed the range [-1.0, 1.0].
fn parabolic_sine(x: f32) -> f32 {
    let y1 = B * x + C * x * x.abs();
    P * (y1 * y1.abs() - y1) + y1
}

/// Convert a unipolar phase value [0, 1) into bipolar range [-1, 1).
fn unipolar_to_bipolar(x: f32) -> f32 {
    x * 2.0 - 1.0
}

/// Supported LFO waveform types.
#[derive(Clone, Copy)]
enum LfoWaveform {
    Sine,
    Triangle,
    Saw,
}

impl From<usize> for LfoWaveform {
    fn from(v: usize) -> Self {
        match v {
            0 => LfoWaveform::Sine,
            1 => LfoWaveform::Triangle,
            _ => LfoWaveform::Saw,
        }
    }
}

/// Low-frequency oscillator (LFO).
///
/// This LFO produces a main output and a quarter-phase-shifted output.
/// It is designed for modulation purposes rather than audio-rate synthesis.
///
/// Characteristics:
/// - Stateless per-sample API (explicit state inside the object)
/// - Deterministic phase accumulation
/// - Multiple waveform types
///
/// Outputs:
/// - Main phase output
/// - Quarter-phase (90°) advanced output
///
/// Notes:
/// - The sine waveform uses a fast approximation and may slightly exceed ±1.0
/// - Phase is always normalized to [0, 1)
#[pyclass]
pub struct Lfo {
    sample_rate: f32,
    waveform: LfoWaveform,
    phase: f32,
    phase_qp: f32,
}

#[pymethods]
impl Lfo {
    /// Create a new LFO.
    ///
    /// # Parameters
    /// - `sample_rate`: sampling rate in Hz (must be positive)
    /// - `waveform`: waveform selector
    ///     - 0: sine
    ///     - 1: triangle
    ///     - otherwise: saw
    #[new]
    #[pyo3(signature = (sample_rate, waveform = 0))]
    pub fn new(sample_rate: f32, waveform: usize) -> Self {
        assert!(sample_rate > 0.0);
        Self {
            sample_rate,
            waveform: waveform.into(),
            phase: 0.0,
            phase_qp: 0.25, // quarter-cycle offset
        }
    }

    /// Process one sample step of the LFO.
    ///
    /// # Parameters
    /// - `frequency`: LFO frequency in Hz
    ///
    /// # Returns
    /// A tuple `(y, y_qp)` where:
    /// - `y` is the main phase output
    /// - `y_qp` is the quarter-phase-shifted output
    pub fn process(&mut self, frequency: f32) -> (f32, f32) {
        let phase_inc = frequency / self.sample_rate;

        let tmp = unipolar_to_bipolar(self.phase);
        let tmp_qp = unipolar_to_bipolar(self.phase_qp);

        let (y, y_qp) = match self.waveform {
            LfoWaveform::Sine => {
                let angle = tmp * PI;
                let angle_qp = tmp_qp * PI;
                (parabolic_sine(-angle), parabolic_sine(-angle_qp))
            }
            LfoWaveform::Triangle => (2.0 * tmp.abs() - 1.0, 2.0 * tmp_qp.abs() - 1.0),
            LfoWaveform::Saw => (tmp, tmp_qp),
        };

        // Advance and normalize phases
        self.phase += phase_inc;
        self.phase -= self.phase.floor();

        self.phase_qp += phase_inc;
        self.phase_qp -= self.phase_qp.floor();

        (y, y_qp)
    }

    /// Reset the internal phase state.
    ///
    /// After reset:
    /// - main phase = 0.0
    /// - quarter phase = 0.25
    pub fn reset(&mut self) {
        self.phase = 0.0;
        self.phase_qp = 0.25;
    }

    /// Get the current sample rate.
    #[getter]
    fn sample_rate(&self) -> f32 {
        self.sample_rate
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SR: f32 = 48_000.0;

    #[test]
    fn lfo_output_is_bounded_for_all_waveforms() {
        let freqs = [0.1, 1.0, 5.0, 10.0];

        for waveform in 0..3 {
            let mut lfo = Lfo::new(SR, waveform);

            for &f in &freqs {
                for _ in 0..10_000 {
                    let (y, y_qp) = lfo.process(f);
                    // The parabolic sine approximation may slightly exceed [-1, 1].
                    assert!(y.abs() <= 1.01, "y out of range: {y}");
                    assert!(y_qp.abs() <= 1.01, "y_qp out of range: {y_qp}");
                }
            }
        }
    }

    #[test]
    fn lfo_phase_is_always_normalized() {
        let mut lfo = Lfo::new(SR, 0);

        for _ in 0..1_000 {
            lfo.process(SR * 10.0); // extremely high frequency
            assert!(lfo.phase >= 0.0 && lfo.phase < 1.0);
            assert!(lfo.phase_qp >= 0.0 && lfo.phase_qp < 1.0);
        }
    }

    #[test]
    fn lfo_is_periodic_for_integer_period() {
        let freq = 5.0;
        let samples_per_period = (SR / freq) as usize;

        let mut lfo = Lfo::new(SR, 0); // sine

        let (y0, y0_qp) = lfo.process(freq);

        // Advance exactly one full period
        for _ in 0..(samples_per_period - 1) {
            lfo.process(freq);
        }

        let (y1, y1_qp) = lfo.process(freq);

        assert!(
            (y0 - y1).abs() < 1e-3,
            "main phase not periodic: y0={y0}, y1={y1}"
        );
        assert!(
            (y0_qp - y1_qp).abs() < 1e-3,
            "quarter phase not periodic: y0_qp={y0_qp}, y1_qp={y1_qp}"
        );
    }

    #[test]
    fn lfo_reset_restores_initial_phases() {
        let mut lfo = Lfo::new(SR, 1); // triangle

        // Advance the phase
        lfo.process(2.0);
        assert!(lfo.phase != 0.0);
        assert!(lfo.phase_qp != 0.25);

        // Reset
        lfo.reset();

        assert!(
            (lfo.phase - 0.0).abs() < f32::EPSILON,
            "phase not reset: {}",
            lfo.phase
        );
        assert!(
            (lfo.phase_qp - 0.25).abs() < f32::EPSILON,
            "quarter phase not reset: {}",
            lfo.phase_qp
        );
    }

    #[test]
    fn lfo_quarter_phase_matches_main_phase_advanced_by_quarter_period() {
        let freq = 1.0;
        let samples_per_period = (SR / freq) as usize;
        let quarter_period = samples_per_period / 4;

        let mut lfo_main = Lfo::new(SR, 0); // sine
        let mut lfo_advanced = Lfo::new(SR, 0); // sine

        // Advance the second LFO by exactly one quarter period
        for _ in 0..quarter_period {
            lfo_advanced.process(freq);
        }

        // Compare outputs at the same logical time
        for _ in 0..1000 {
            let (_, y_qp) = lfo_main.process(freq);
            let (y_adv, _) = lfo_advanced.process(freq);

            assert!(
                (y_qp - y_adv).abs() < 1e-3,
                "quarter-phase mismatch: y_qp={y_qp}, y_adv={y_adv}"
            );
        }
    }

    #[test]
    fn lfo_does_not_produce_nan_or_inf() {
        let mut lfo = Lfo::new(SR, 0);

        let freqs = [0.0, 0.1, 1.0, 10.0, SR, SR * 10.0];

        for &f in &freqs {
            for _ in 0..100 {
                let (y, y_qp) = lfo.process(f);
                assert!(y.is_finite(), "non-finite y: {y}");
                assert!(y_qp.is_finite(), "non-finite y_qp: {y_qp}");
            }
        }
    }
}
