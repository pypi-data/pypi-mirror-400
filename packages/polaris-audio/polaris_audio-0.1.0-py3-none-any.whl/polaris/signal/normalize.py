import numpy as np


def normalize(x: np.ndarray, headroom_db: float = 1.0) -> np.ndarray:
    """
    Peak-normalize a signal with specified headroom.

    This function is intended as a safety utility for numerical
    experiments, not as a perceptual loudness normalizer.

    Parameters
    ----------
    x : np.ndarray
        Input signal (typically 1D)
    headroom_db : float
        Headroom in decibels below full scale

    Returns
    -------
    np.ndarray
        Normalized signal
    """
    x = np.asarray(x, dtype=float)

    if x.size == 0:
        return x

    peak = np.max(np.abs(x))

    if peak < 1e-12:
        return x

    gain = 10.0 ** (-headroom_db / 20.0)
    return x * (gain / peak)
