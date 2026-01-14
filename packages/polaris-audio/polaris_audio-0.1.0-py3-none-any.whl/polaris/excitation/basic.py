from typing import Literal

import numpy as np

ExcitationKind = Literal["impulse", "noise", "pluck"]


def make_excitation(
    n: int,
    fs: float,
    kind: ExcitationKind = "pluck",
    seed: int = 0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Generate an excitation signal u[n] for state-space / ARMA-based synthesis.

    Excitation represents an external force applied to a resonant system,
    not a finished sound.

    Kinds
    -----
    impulse:
        Single-sample impulse (e.g. striking)
    noise:
        White noise excitation (e.g. blowing / bowing)
    pluck:
        Short noise burst with decay (e.g. plucking a string)

    Parameters
    ----------
    n : int
        Number of samples
    fs : float
        Sampling rate [Hz] (used for time scaling of pluck excitation)
    kind : str
        Type of excitation
    seed : int
        Random seed (used only if rng is None)
    rng : np.random.Generator or None
        Optional external RNG for reproducibility

    Returns
    -------
    np.ndarray
        Excitation signal u[n]
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if fs <= 0.0:
        raise ValueError("fs must be positive")

    if rng is None:
        rng = np.random.default_rng(seed)

    if kind == "impulse":
        x = np.zeros(n, dtype=np.float64)
        x[0] = 1.0
        return x

    if kind == "noise":
        return rng.standard_normal(n).astype(np.float64)

    if kind == "pluck":
        x = np.zeros(n, dtype=np.float64)
        burst_len = max(1, int(0.01 * fs))  # ~10 ms burst
        burst_len = min(burst_len, n)

        noise = rng.standard_normal(burst_len)
        envelope = np.linspace(1.0, 0.0, burst_len, endpoint=False)

        x[:burst_len] = noise * envelope
        return x

    raise ValueError(f"Unknown excitation kind: {kind}")
