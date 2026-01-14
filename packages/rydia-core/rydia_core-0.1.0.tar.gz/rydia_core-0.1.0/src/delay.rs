use crate::ring_buffer::{RingBufferL, RingBufferN, RingBufferS};
use pyo3::prelude::*;

/// Compute the feedback coefficient used by SuperCollider-style
/// comb and allpass filters.
///
/// Formula:
///
/// ```text
/// fb = 0.001 ** (delay / abs(decay)) * sign(decay)
/// ```
///
/// - Larger absolute decay values result in feedback closer to 1.0
/// - The sign of `decay` determines the polarity
#[pyfunction]
fn calc_fb(delay: f32, decay: f32) -> f32 {
    0.001_f32.powf(delay / decay.abs()) * decay.signum()
}

/// Integer-sample delay line.
///
/// This delay operates on discrete sample offsets only.
/// Fractional delays are not supported.
#[pyclass]
#[derive(Clone, Debug)]
pub struct DelayS {
    buf: RingBufferS,
}

#[pymethods]
impl DelayS {
    /// Create a new integer-sample delay line.
    ///
    /// `max_delay_samp` specifies the maximum supported delay in samples.
    #[new]
    pub fn new(max_delay_samp: usize) -> Self {
        Self {
            buf: RingBufferS::new(max_delay_samp),
        }
    }

    /// Process one input sample and return the delayed output.
    pub fn process(&mut self, xn: f32, delay_samp: usize) -> f32 {
        let yn = self.buf.read(delay_samp);
        self.buf.write(xn);
        yn
    }
}

/// Time-based delay line without interpolation.
///
/// Fractional delay times are truncated to integer samples.
#[pyclass]
#[derive(Clone, Debug)]
pub struct DelayN {
    buf: RingBufferN,
}

#[pymethods]
impl DelayN {
    /// Create a new time-based delay line.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferN::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one input sample with a time-based delay.
    pub fn process(&mut self, xn: f32, delay_sec: f32) -> f32 {
        let yn = self.buf.read(delay_sec);
        self.buf.write(xn);
        yn
    }
}

/// Time-based delay line with linear interpolation.
///
/// Fractional delays are handled smoothly via linear interpolation.
#[pyclass]
#[derive(Clone, Debug)]
pub struct DelayL {
    buf: RingBufferL,
}

#[pymethods]
impl DelayL {
    /// Create a new interpolating delay line.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferL::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one input sample with a fractional delay.
    pub fn process(&mut self, xn: f32, delay_sec: f32) -> f32 {
        let yn = self.buf.read(delay_sec);
        self.buf.write(xn);
        yn
    }
}

/// Integer-sample comb filter.
///
/// This is a feedback delay line using a SuperCollider-style
/// decay parameter.
#[pyclass]
#[derive(Clone, Debug)]
pub struct CombS {
    buf: RingBufferS,
}

#[pymethods]
impl CombS {
    /// Create a new integer-sample comb filter.
    #[new]
    pub fn new(max_delay_samp: usize) -> Self {
        Self {
            buf: RingBufferS::new(max_delay_samp),
        }
    }

    /// Process one sample through the comb filter.
    pub fn process(&mut self, xn: f32, delay_samp: usize, decay_samp: usize) -> f32 {
        let yn = self.buf.read(delay_samp);
        let fb = calc_fb(delay_samp as f32, decay_samp as f32);
        self.buf.write(xn + yn * fb);
        yn
    }
}

/// Time-based comb filter without interpolation.
#[pyclass]
#[derive(Clone, Debug)]
pub struct CombN {
    buf: RingBufferN,
}

#[pymethods]
impl CombN {
    /// Create a new time-based comb filter.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferN::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one sample through the comb filter.
    pub fn process(&mut self, xn: f32, delay_sec: f32, decay_sec: f32) -> f32 {
        let yn = self.buf.read(delay_sec);
        let fb = calc_fb(delay_sec, decay_sec);
        self.buf.write(xn + yn * fb);
        yn
    }
}

/// Time-based comb filter with linear interpolation.
#[pyclass]
#[derive(Clone, Debug)]
pub struct CombL {
    buf: RingBufferL,
}

#[pymethods]
impl CombL {
    /// Create a new interpolating comb filter.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferL::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one sample through the comb filter.
    pub fn process(&mut self, xn: f32, delay_sec: f32, decay_sec: f32) -> f32 {
        let yn = self.buf.read(delay_sec);
        let fb = calc_fb(delay_sec, decay_sec);
        self.buf.write(xn + yn * fb);
        yn
    }
}

/// Integer-sample allpass filter.
#[pyclass]
#[derive(Clone, Debug)]
pub struct AllpassS {
    buf: RingBufferS,
}

#[pymethods]
impl AllpassS {
    /// Create a new integer-sample allpass filter.
    #[new]
    pub fn new(max_delay_samp: usize) -> Self {
        Self {
            buf: RingBufferS::new(max_delay_samp),
        }
    }

    /// Process one sample through the allpass filter.
    pub fn process(&mut self, xn: f32, delay_samp: usize, decay_samp: usize) -> f32 {
        let k = calc_fb(delay_samp as f32, decay_samp as f32);
        let s_delay = self.buf.read(delay_samp);

        let sn = xn + k * s_delay;
        let yn = -k * sn + s_delay;

        self.buf.write(sn);
        yn
    }
}

/// Time-based allpass filter without interpolation.
#[pyclass]
#[derive(Clone, Debug)]
pub struct AllpassN {
    buf: RingBufferN,
}

#[pymethods]
impl AllpassN {
    /// Create a new time-based allpass filter.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferN::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one sample through the allpass filter.
    pub fn process(&mut self, xn: f32, delay_sec: f32, decay_sec: f32) -> f32 {
        let k = calc_fb(delay_sec, decay_sec);
        let s_delay = self.buf.read(delay_sec);

        let sn = xn + k * s_delay;
        let yn = -k * sn + s_delay;

        self.buf.write(sn);
        yn
    }
}

/// Time-based allpass filter with linear interpolation.
#[pyclass]
#[derive(Clone, Debug)]
pub struct AllpassL {
    buf: RingBufferL,
}

#[pymethods]
impl AllpassL {
    /// Create a new interpolating allpass filter.
    #[new]
    pub fn new(sample_rate: f32, max_delay_sec: f32) -> Self {
        Self {
            buf: RingBufferL::new(sample_rate, max_delay_sec),
        }
    }

    /// Process one sample through the allpass filter.
    pub fn process(&mut self, xn: f32, delay_sec: f32, decay_sec: f32) -> f32 {
        let k = calc_fb(delay_sec, decay_sec);
        let s_delay = self.buf.read(delay_sec);

        let sn = xn + k * s_delay;
        let yn = -k * sn + s_delay;

        self.buf.write(sn);
        yn
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx(a: f32, b: f32, eps: f32) {
        assert!(
            (a - b).abs() <= eps,
            "not approximately equal: a={a}, b={b}, |a-b|={}",
            (a - b).abs()
        );
    }

    #[test]
    fn test_calc_fb_monotonicity() {
        let delay = 1.0;

        let fb_short = calc_fb(delay, 10.0);
        let fb_mid = calc_fb(delay, 100.0);
        let fb_long = calc_fb(delay, 1000.0);

        // Longer decay times produce feedback closer to 1.0
        assert!(fb_short < fb_mid);
        assert!(fb_mid < fb_long);
        assert!(fb_long < 1.0);
    }

    #[test]
    fn test_delay_s_basic_behavior() {
        let mut d = DelayS::new(4);

        // Initial outputs must be zero
        approx(d.process(10.0, 2), 0.0, 1e-6);
        approx(d.process(11.0, 2), 0.0, 1e-6);

        // Input appears after the specified delay
        approx(d.process(12.0, 2), 10.0, 1e-6);
        approx(d.process(13.0, 2), 11.0, 1e-6);
    }

    #[test]
    fn test_delay_n_truncates_fractional_delay() {
        let mut d = DelayN::new(1.0, 4.0);

        approx(d.process(10.0, 2.1), 0.0, 1e-6);
        approx(d.process(11.0, 2.1), 0.0, 1e-6);

        // floor(delay_sec * sample_rate) is used
        approx(d.process(12.0, 2.1), 10.0, 1e-6);
        approx(d.process(13.0, 2.1), 11.0, 1e-6);
    }

    #[test]
    fn test_delay_l_interpolates_smoothly() {
        let mut d = DelayL::new(1.0, 4.0);

        let y0 = d.process(10.0, 1.8);
        let y1 = d.process(11.0, 1.8);
        let y2 = d.process(12.0, 1.8);

        // First output must be zero
        approx(y0, 0.0, 1e-6);

        // Interpolated output rises smoothly
        assert!(y1 > 0.0);
        assert!(y2 > y1);
    }

    #[test]
    fn test_comb_s_energy_builds_up() {
        let mut c = CombS::new(4);

        let mut prev = 0.0;
        for i in 0..10 {
            let y = c.process(1.0, 2, 10);
            if i > 2 {
                // Feedback causes energy accumulation
                assert!(y >= prev);
            }
            prev = y;
        }
    }

    #[test]
    fn test_comb_n_and_l_do_not_produce_nan_or_inf() {
        let mut c_n = CombN::new(1.0, 4.0);
        let mut c_l = CombL::new(1.0, 4.0);

        for _ in 0..1000 {
            let y_n = c_n.process(1.0, 2.3, 5.0);
            let y_l = c_l.process(1.0, 2.3, 5.0);

            assert!(y_n.is_finite(), "CombN produced non-finite value");
            assert!(y_l.is_finite(), "CombL produced non-finite value");
        }
    }

    #[test]
    fn test_allpass_preserves_energy_distribution() {
        let mut ap = AllpassL::new(1.0, 4.0);

        // Unit impulse
        let y0 = ap.process(1.0, 2.0, 10.0);
        let y1 = ap.process(0.0, 2.0, 10.0);
        let y2 = ap.process(0.0, 2.0, 10.0);

        // Allpass redistributes energy but does not remove it
        assert!(y0.abs() > 0.0);
        assert!(y1.abs() > 0.0 || y2.abs() > 0.0);
    }

    #[test]
    fn test_allpass_does_not_produce_nan_or_inf() {
        let mut ap = AllpassN::new(1.0, 4.0);

        for _ in 0..1000 {
            let y = ap.process(0.5, 2.0, 5.0);
            assert!(y.is_finite(), "Allpass produced non-finite value");
        }
    }
}
