use pyo3::prelude::*;
use std::f32::consts::TAU;

use rand::rngs::SmallRng;
use rand::{Rng, SeedableRng};

/// A simple phase-accumulating sine oscillator.
///
/// This oscillator generates a continuous sine waveform
/// using normalized phase accumulation.
///
/// Characteristics:
/// - Audio-rate oscillator
/// - Stateless API with internal phase state
/// - Deterministic and reproducible given the same inputs
///
/// Phase model:
/// - Phase is normalized to the range [0, 1)
/// - Output is computed as `sin(phase * TAU)`
///
/// Notes:
/// - No band-limiting is applied
/// - High frequencies may produce aliasing
#[pyclass]
pub struct SinOsc {
    sample_rate: f32,
    phase: f32,
}

#[pymethods]
impl SinOsc {
    /// Create a new sine oscillator.
    ///
    /// # Parameters
    /// - `sample_rate`: sampling rate in Hz (must be positive)
    /// - `phase`: initial phase in the range [0, 1)
    #[new]
    #[pyo3(signature = (sample_rate, phase = 0.0))]
    pub fn new(sample_rate: f32, phase: f32) -> Self {
        assert!(sample_rate > 0.0);
        Self { sample_rate, phase }
    }

    /// Process one sample of the oscillator.
    ///
    /// # Parameters
    /// - `frequency`: oscillator frequency in Hz
    ///
    /// # Returns
    /// The current sine output sample.
    pub fn process(&mut self, frequency: f32) -> f32 {
        // Output at current phase
        let y = (self.phase * TAU).sin();

        // Advance and wrap phase
        self.phase += frequency / self.sample_rate;
        self.phase -= self.phase.floor();

        y
    }

    /// Reset the internal phase to zero.
    ///
    /// After reset, the next output will be `sin(0) = 0`.
    pub fn reset(&mut self) {
        self.phase = 0.0;
    }

    /// Get the current sample rate.
    #[getter]
    fn sample_rate(&self) -> f32 {
        self.sample_rate
    }

    /// Get the current normalized phase.
    #[getter]
    fn phase(&self) -> f32 {
        self.phase
    }
}

/// White noise signal generator.
///
/// This generator produces independent, uniformly distributed
/// random samples in the range [-1.0, 1.0].
///
/// Characteristics:
/// - Stateless from the user's perspective
/// - Internally uses a fast, small RNG
/// - Suitable for noise sources, modulation, and testing
///
/// Notes:
/// - The distribution is uniform, not Gaussian
/// - The RNG is seeded from the operating system
#[pyclass]
pub struct WhiteNoise {
    rng: SmallRng,
}

#[pymethods]
impl WhiteNoise {
    /// Create a new white noise generator.
    ///
    /// The internal RNG is seeded from the operating system.
    #[new]
    #[pyo3(signature = (seed = None))]
    pub fn new(seed: Option<u64>) -> Self {
        let rng = match seed {
            Some(s) => SmallRng::seed_from_u64(s),
            None => SmallRng::from_os_rng(),
        };
        Self { rng }
    }

    /// Generate one white noise sample.
    ///
    /// # Returns
    /// A random value uniformly distributed in [-1.0, 1.0].
    pub fn process(&mut self) -> f32 {
        self.rng.random_range(-1.0..1.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SR: f32 = 48_000.0;

    #[test]
    fn sinosc_output_is_bounded() {
        let mut osc = SinOsc::new(SR, 0.0);
        for _ in 0..10_000 {
            let y = osc.process(440.0);
            assert!(y >= -1.0 && y <= 1.0, "output out of range: {y}");
        }
    }

    #[test]
    fn sinosc_phase_is_always_normalized() {
        let mut osc = SinOsc::new(SR, 0.0);

        // Extremely high frequencies should not break phase normalization
        for _ in 0..1_000 {
            osc.process(SR * 10.0);
            assert!(
                osc.phase >= 0.0 && osc.phase < 1.0,
                "phase not normalized: {}",
                osc.phase
            );
        }
    }

    #[test]
    fn sinosc_is_periodic_for_integer_period() {
        let freq = 1_000.0;
        let samples_per_period = (SR / freq) as usize;

        let mut osc = SinOsc::new(SR, 0.0);

        let y0 = osc.process(freq);

        // Advance exactly one full period
        for _ in 0..(samples_per_period - 1) {
            osc.process(freq);
        }

        let y1 = osc.process(freq);

        // Periodicity (with numerical tolerance)
        assert!(
            (y0 - y1).abs() < 1e-4,
            "periodicity broken: y0={y0}, y1={y1}"
        );
    }

    #[test]
    fn sinosc_reset_sets_phase_to_zero() {
        let mut osc = SinOsc::new(SR, 0.3);

        // Advance once
        osc.process(440.0);
        assert!(osc.phase != 0.0);

        // Reset
        osc.reset();
        assert!(
            (osc.phase - 0.0).abs() < f32::EPSILON,
            "phase not reset: {}",
            osc.phase
        );

        // First output after reset must be sin(0) = 0
        let y = osc.process(440.0);
        assert!(y.abs() < 1e-6, "output after reset not zero: {y}");
    }

    #[test]
    fn sinosc_does_not_produce_nan_or_inf() {
        let mut osc = SinOsc::new(SR, 0.0);

        let freqs = [0.0, 1.0, 440.0, SR / 2.0, SR, SR * 10.0];

        for &f in &freqs {
            for _ in 0..100 {
                let y = osc.process(f);
                assert!(y.is_finite(), "non-finite output: {y}");
            }
        }
    }

    #[test]
    fn white_noise_is_bounded_and_mean_is_near_zero() {
        let mut noise = WhiteNoise::new(None);

        let mut sum = 0.0;
        let n = 100_000;

        for _ in 0..n {
            let x = noise.process();
            assert!(x >= -1.0 && x <= 1.0, "noise out of range: {x}");
            sum += x;
        }

        let mean = sum / n as f32;
        assert!(mean.abs() < 0.02, "noise mean too far from zero: {mean}");
    }

    #[test]
    fn white_noise_is_reproducible_with_seed() {
        let mut a = WhiteNoise::new(Some(123));
        let mut b = WhiteNoise::new(Some(123));

        for _ in 0..100 {
            assert_eq!(a.process(), b.process());
        }
    }
}
