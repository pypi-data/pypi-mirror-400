"""
RBJ Audio EQ Cookbook reference implementations.

This module provides direct implementations of the well-known
RBJ biquad filter formulas.

Notes
-----
- This module is provided for reference and interoperability.
- polaris-audio does NOT treat RBJ filters as a primary design method.
- Users are encouraged to convert these coefficients into
  state-space or pole/zero representations.
"""

import math


def _check_params(fs: float, f0: float, Q: float) -> None:
    if fs <= 0.0:
        raise ValueError("fs must be positive")
    if not (0.0 < f0 < fs * 0.5):
        raise ValueError("f0 must be in (0, fs/2)")
    if Q <= 0.0:
        raise ValueError("Q must be positive")


def rbj_lowpass(fs: float, f0: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """
    RBJ low-pass biquad filter.
    """
    _check_params(fs, f0, Q)

    w0 = 2.0 * math.pi * (f0 / fs)
    cosw0 = math.cos(w0)
    sinw0 = math.sin(w0)
    alpha = sinw0 / (2.0 * Q)

    b0 = (1.0 - cosw0) / 2.0
    b1 = 1.0 - cosw0
    b2 = (1.0 - cosw0) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw0
    a2 = 1.0 - alpha

    return b0, b1, b2, a0, a1, a2


def rbj_highpass(fs: float, f0: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """
    RBJ high-pass biquad filter.
    """
    _check_params(fs, f0, Q)

    w0 = 2.0 * math.pi * (f0 / fs)
    cosw0 = math.cos(w0)
    sinw0 = math.sin(w0)
    alpha = sinw0 / (2.0 * Q)

    b0 = (1.0 + cosw0) / 2.0
    b1 = -(1.0 + cosw0)
    b2 = (1.0 + cosw0) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw0
    a2 = 1.0 - alpha

    return b0, b1, b2, a0, a1, a2


def rbj_bandpass_constant_skirt(fs: float, f0: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """
    RBJ band-pass biquad (constant skirt gain, peak gain = Q).
    """
    _check_params(fs, f0, Q)

    w0 = 2.0 * math.pi * (f0 / fs)
    cosw0 = math.cos(w0)
    sinw0 = math.sin(w0)
    alpha = sinw0 / (2.0 * Q)

    b0 = sinw0 / 2.0
    b1 = 0.0
    b2 = -sinw0 / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw0
    a2 = 1.0 - alpha

    return b0, b1, b2, a0, a1, a2


def rbj_notch(fs: float, f0: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """
    RBJ notch (band-stop) biquad filter.
    """
    _check_params(fs, f0, Q)

    w0 = 2.0 * math.pi * (f0 / fs)
    cosw0 = math.cos(w0)
    sinw0 = math.sin(w0)
    alpha = sinw0 / (2.0 * Q)

    b0 = 1.0
    b1 = -2.0 * cosw0
    b2 = 1.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cosw0
    a2 = 1.0 - alpha

    return b0, b1, b2, a0, a1, a2


def rbj_peaking_eq(fs: float, f0: float, Q: float, gain_db: float) -> tuple[float, float, float, float, float, float]:
    """
    RBJ peaking EQ (bell) biquad filter.
    """
    _check_params(fs, f0, Q)

    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * (f0 / fs)
    cosw0 = math.cos(w0)
    sinw0 = math.sin(w0)
    alpha = sinw0 / (2.0 * Q)

    b0 = 1.0 + alpha * A
    b1 = -2.0 * cosw0
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * cosw0
    a2 = 1.0 - alpha / A

    return b0, b1, b2, a0, a1, a2
