use pyo3::prelude::*;

/// A biquad filter executor using Transposed Direct Form II.
///
/// This type **does not perform filter design**.
/// It executes a second-order IIR filter given already-normalized
/// coefficients (i.e. `a0 == 1.0`).
///
/// Typical use cases:
/// - Executing RBJ cookbook filters
/// - Executing externally designed IIR filters
/// - Time-varying coefficient updates without reallocations
///
/// Difference equation (with `a0 == 1`):
///
/// ```text
/// y[n] = b0 * x[n]
///      + b1 * x[n-1]
///      + b2 * x[n-2]
///      - a1 * y[n-1]
///      - a2 * y[n-2]
/// ```
///
/// Internal structure:
/// - Transposed Direct Form II
/// - Two internal delay states
///
/// Notes:
/// - Stability depends entirely on the provided coefficients.
/// - No parameter smoothing is applied.
#[derive(Clone, Copy, Debug)]
struct BiquadCoefs {
    b0: f32,
    b1: f32,
    b2: f32,
    a1: f32,
    a2: f32,
}

#[derive(Clone, Copy, Debug)]
struct BiquadState {
    z1: f32,
    z2: f32,
}

/// A stateful biquad filter processor.
///
/// This struct exposes a minimal and explicit API:
/// - Construct with normalized coefficients
/// - Process samples one-by-one
/// - Reset or update coefficients explicitly
#[pyclass]
#[derive(Clone, Debug)]
pub struct Biquad {
    coefs: BiquadCoefs,
    state: BiquadState,
}

#[pymethods]
impl Biquad {
    /// Create a biquad filter with normalized coefficients.
    ///
    /// # Parameters
    /// - `b0`, `b1`, `b2`: feedforward coefficients
    /// - `a1`, `a2`: feedback coefficients
    ///
    /// The caller is responsible for ensuring that:
    /// - `a0 == 1.0` in the original filter design
    /// - The filter is stable
    #[new]
    #[pyo3(signature = (b0, b1, b2, a1, a2))]
    pub fn new(b0: f32, b1: f32, b2: f32, a1: f32, a2: f32) -> Self {
        Self {
            coefs: BiquadCoefs { b0, b1, b2, a1, a2 },
            state: BiquadState { z1: 0.0, z2: 0.0 },
        }
    }

    /// Process one input sample and return the output.
    ///
    /// This method performs no allocations and updates
    /// the internal state in-place.
    pub fn process(&mut self, x: f32) -> f32 {
        // Transposed Direct Form II
        let y = self.coefs.b0 * x + self.state.z1;
        self.state.z1 = self.coefs.b1 * x - self.coefs.a1 * y + self.state.z2;
        self.state.z2 = self.coefs.b2 * x - self.coefs.a2 * y;
        y
    }

    /// Reset the internal delay state to zero.
    ///
    /// This clears filter memory but keeps the current coefficients.
    pub fn reset(&mut self) {
        self.state = BiquadState { z1: 0.0, z2: 0.0 };
    }

    /// Update filter coefficients in-place.
    ///
    /// This allows efficient coefficient modulation without
    /// reallocating or recreating the filter object.
    pub fn set_coefs(&mut self, b0: f32, b1: f32, b2: f32, a1: f32, a2: f32) {
        self.coefs = BiquadCoefs { b0, b1, b2, a1, a2 };
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
    fn biquad_identity_passthrough() {
        // y = x
        let mut bq = Biquad::new(1.0, 0.0, 0.0, 0.0, 0.0);
        for i in 0..100 {
            let x = (i as f32) * 0.01 - 0.5;
            let y = bq.process(x);
            approx(y, x, 1e-6);
        }
    }

    #[test]
    fn biquad_dc_stays_dc_for_identity() {
        let mut bq = Biquad::new(1.0, 0.0, 0.0, 0.0, 0.0);
        for _ in 0..100 {
            let y = bq.process(1.0);
            approx(y, 1.0, 1e-6);
        }
    }

    #[test]
    fn biquad_reset_clears_history() {
        // Simple IIR: y[n] = x[n] + 0.5 * y[n-1]
        // Implemented as: y = x - a1*y[-1], with a1 = -0.5
        let mut bq = Biquad::new(1.0, 0.0, 0.0, -0.5, 0.0);

        let y1 = bq.process(1.0);
        let y2 = bq.process(1.0);
        assert!(y2 > y1);

        bq.reset();
        let y1b = bq.process(1.0);
        approx(y1b, y1, 1e-6);
    }

    #[test]
    fn biquad_does_not_produce_nan_or_inf() {
        let mut bq = Biquad::new(0.1, 0.1, 0.0, -0.8, 0.0);
        for _ in 0..10_000 {
            let y = bq.process(0.5);
            assert!(y.is_finite(), "non-finite output: {y}");
        }
    }

    #[test]
    fn biquad_set_coefs_changes_behavior() {
        let mut bq = Biquad::new(1.0, 0.0, 0.0, 0.0, 0.0);
        let y_id = bq.process(1.0);
        approx(y_id, 1.0, 1e-6);

        // Change to a simple FIR attenuator: y = 0.5 * x
        bq.reset();
        bq.set_coefs(0.5, 0.0, 0.0, 0.0, 0.0);
        let y_att = bq.process(1.0);
        approx(y_att, 0.5, 1e-6);
    }
}
