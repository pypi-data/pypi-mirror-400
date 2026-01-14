import math


def omega_from_f0(fs: float, f0: float) -> float:
    """
    Convert frequency (Hz) to normalized angular frequency (rad/sample).

    ω = 2π f0 / fs

    Parameters
    ----------
    fs : float
        Sampling rate [Hz], fs > 0
    f0 : float
        Frequency [Hz], f0 >= 0

    Returns
    -------
    float
        Angular frequency ω [rad/sample]
    """
    if fs <= 0.0:
        raise ValueError("fs must be positive")
    if f0 < 0.0:
        raise ValueError("f0 must be non-negative")

    return 2.0 * math.pi * f0 / fs


def r_from_T60(fs: float, T60: float) -> float:
    """
    Compute pole radius r from T60 decay time.

    The radius r is defined such that the amplitude decays by 60 dB
    after T60 seconds.

        r = 10^(-3 / (fs * T60))

    Parameters
    ----------
    fs : float
        Sampling rate [Hz], fs > 0
    T60 : float
        Decay time [s], T60 > 0

    Returns
    -------
    float
        Pole radius r (0 < r < 1)
    """
    if fs <= 0.0:
        raise ValueError("fs must be positive")
    if T60 <= 0.0:
        raise ValueError("T60 must be positive")

    return 10.0 ** (-3.0 / (fs * T60))


def pole_from_f0_T60(fs: float, f0: float, T60: float) -> complex:
    """
    Compute a single complex pole from frequency and T60.

        z = r * exp(j ω)

    This represents a discrete-time resonant mode with
    frequency f0 and decay time T60.

    Parameters
    ----------
    fs : float
        Sampling rate [Hz]
    f0 : float
        Frequency [Hz]
    T60 : float
        Decay time [s]

    Returns
    -------
    complex
        Complex pole z
    """
    omega = omega_from_f0(fs, f0)
    r = r_from_T60(fs, T60)

    return r * complex(math.cos(omega), math.sin(omega))


def conjugate_poles_from_f0_T60(fs: float, f0: float, T60: float) -> tuple[complex, complex]:
    """
    Compute a complex-conjugate pole pair from frequency and T60.

    Returns (z, z*), suitable for real-valued filters and state-space models.
    """
    z = pole_from_f0_T60(fs, f0, T60)
    return z, z.conjugate()
