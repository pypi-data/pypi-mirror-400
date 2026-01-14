use pyo3::prelude::*;
use std::f32::consts::FRAC_PI_4;

/// Equal-power mono-to-stereo panner.
///
/// This function maps a mono signal into stereo using an
/// equal-power panning law. The perceived loudness remains
/// approximately constant across the stereo field.
///
/// Panning model:
/// - `pos` ∈ [-1.0, 1.0]
///     - -1.0: full left
///     -  0.0: center
///     -  1.0: full right
///
/// Internally, `pos` is mapped to an angle θ ∈ [0, π/2]:
///
/// ```text
/// θ = (pos + 1) * (π / 4)
/// left  = x * cos(θ)
/// right = x * sin(θ)
/// ```
///
/// Properties:
/// - Power-preserving: `left^2 + right^2 ≈ x^2`
/// - Stateless and deterministic
///
/// Notes:
/// - This is intended as a lightweight utility, not a full spatialization model.
/// - Input values outside [-1, 1] are clamped.
#[pyfunction]
#[pyo3(signature = (x, pos = 0.0))]
pub fn pan2(x: f32, pos: f32) -> (f32, f32) {
    // Clamp position to the valid range
    let pos = pos.clamp(-1.0, 1.0);

    // Map pos ∈ [-1, 1] to angle ∈ [0, π/2]
    let angle = (pos + 1.0) * FRAC_PI_4;

    let left = x * angle.cos();
    let right = x * angle.sin();

    (left, right)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx(a: f32, b: f32, eps: f32) {
        assert!(
            (a - b).abs() <= eps,
            "not approximately equal: a={a}, b={b}"
        );
    }

    #[test]
    fn pan2_center_is_balanced() {
        let (l, r) = pan2(1.0, 0.0);
        approx(l, r, 1e-6);

        // Equal-power condition: l^2 + r^2 == x^2
        approx(l * l + r * r, 1.0, 1e-6);
    }

    #[test]
    fn pan2_full_left() {
        let (l, r) = pan2(1.0, -1.0);
        approx(l, 1.0, 1e-6);
        approx(r, 0.0, 1e-6);
    }

    #[test]
    fn pan2_full_right() {
        let (l, r) = pan2(1.0, 1.0);
        approx(l, 0.0, 1e-6);
        approx(r, 1.0, 1e-6);
    }

    #[test]
    fn pan2_preserves_power_for_various_positions() {
        let x = 0.8;
        for pos in [-1.0, -0.5, 0.0, 0.5, 1.0] {
            let (l, r) = pan2(x, pos);
            approx(l * l + r * r, x * x, 1e-6);
        }
    }
}
