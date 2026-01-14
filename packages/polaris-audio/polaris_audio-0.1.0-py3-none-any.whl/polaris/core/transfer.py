import math

from .poles import omega_from_f0, r_from_T60


def ar2_from_poles(omega: float, r: float) -> tuple[float, float, float]:
    """
    Construct a 2nd-order AR denominator from a complex-conjugate pole pair.

        A(z) = 1 + a1 z^{-1} + a2 z^{-2}

    with poles at:
        z = r * exp(±j ω)

    Coefficients:
        a1 = -2 r cos(ω)
        a2 = r^2
    """
    if not (0.0 < r < 1.0):
        raise ValueError("r must be in (0, 1) for stability")

    a0 = 1.0
    a1 = -2.0 * r * math.cos(omega)
    a2 = r * r
    return a0, a1, a2


def ar2_from_parameters(fs: float, f0: float, T60: float) -> tuple[float, float, float]:
    """
    Convenience wrapper: (fs, f0, T60) → AR(2) coefficients.
    """
    omega = omega_from_f0(fs, f0)
    r = r_from_T60(fs, T60)
    return ar2_from_poles(omega, r)


def ma2_from_zeros(
    omega_z: float,
    r_z: float,
    gain: float = 1.0,
) -> tuple[float, float, float]:
    """
    Construct a 2nd-order MA numerator from a complex-conjugate zero pair.

        B(z) = b0 + b1 z^{-1} + b2 z^{-2}

    with zeros at:
        z = r_z * exp(±j ω_z)
    """
    b0 = gain
    b1 = -2.0 * gain * r_z * math.cos(omega_z)
    b2 = gain * r_z * r_z
    return b0, b1, b2


def ma2_from_parameters(
    fs: float,
    fz: float,
    T60_z: float,
    gain: float = 1.0,
) -> tuple[float, float, float]:
    """
    Convenience wrapper: (fs, fz, T60_z) → MA(2) coefficients.
    """
    omega_z = omega_from_f0(fs, fz)
    r_z = r_from_T60(fs, T60_z)
    return ma2_from_zeros(omega_z, r_z, gain)


def ma2_from_attack_exp3(
    fs: float,
    attack_s: float,
    gain: float = 1.0,
) -> tuple[float, float, float, float]:
    """
    MA(2) coefficients approximating a 3-tap exponential attack envelope.

    This is useful as an excitation signal rather than a filter.

    Returns (b0, b1, b2, alpha)
    """
    if attack_s <= 0.0:
        raise ValueError("attack_s must be > 0")

    alpha = math.exp(-1.0 / (fs * attack_s))

    b0 = gain * (1.0 - alpha)
    b1 = gain * (1.0 - alpha) * alpha
    b2 = gain * (1.0 - alpha) * alpha * alpha

    return b0, b1, b2, alpha


def ma2_from_click_diff(
    fs: float,
    attack_s: float,
    gain: float = 1.0,
) -> tuple[float, float, float, float]:
    """
    MA(2) differentiator-like excitation (click / impulse shaping).

    This emphasizes transients and is useful for percussive excitation.
    """
    if attack_s <= 0.0:
        raise ValueError("attack_s must be > 0")

    alpha = math.exp(-1.0 / (fs * attack_s))

    b0 = gain
    b1 = -gain * alpha
    b2 = 0.0

    return b0, b1, b2, alpha
