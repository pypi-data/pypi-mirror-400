import numpy as np


def arma22_controllable_canonical_ss(
    b0: float,
    b1: float,
    b2: float,
    a0: float,
    a1: float,
    a2: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Construct a discrete-time ARMA(2,2) system in controllable canonical form.

    Transfer function:
        H(z) = (b0 + b1 z^{-1} + b2 z^{-2}) /
               (a0 + a1 z^{-1} + a2 z^{-2})

    After normalization (a0 = 1), the state-space realization is:

        x[n+1] = A x[n] + B u[n]
        y[n]   = C x[n] + D u[n]

    This representation is suitable for:
    - biquad filters
    - modal resonators
    - ARMA-based sound synthesis

    Notes
    -----
    - This is a 2nd-order system (state dimension = 2)
    - Stability depends on the poles of the denominator polynomial

    Parameters
    ----------
    b0, b1, b2 : float
        Numerator coefficients
    a0, a1, a2 : float
        Denominator coefficients (a0 must be nonzero)

    Returns
    -------
    A, B, C, D : np.ndarray
        State-space matrices with shapes:
        A: (2, 2), B: (2, 1), C: (1, 2), D: (1, 1)
    """
    if a0 == 0.0:
        raise ValueError("a0 must be nonzero")

    # normalize coefficients so that a0 = 1
    b0n, b1n, b2n = b0 / a0, b1 / a0, b2 / a0
    a1n, a2n = a1 / a0, a2 / a0

    A = np.array([[-a1n, -a2n], [1.0, 0.0]], dtype=float)
    B = np.array([[1.0], [0.0]], dtype=float)
    C = np.array([[b1n - a1n * b0n, b2n - a2n * b0n]], dtype=float)
    D = np.array([[b0n]], dtype=float)

    return A, B, C, D


def ss_step(
    x: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    D: np.ndarray,
    u: float,
) -> tuple[np.ndarray, float]:
    """
    Advance a discrete-time state-space system by one sample.

        x[n+1] = A x[n] + B u[n]
        y[n]   = C x[n] + D u[n]

    Parameters
    ----------
    x : np.ndarray, shape (2, 1)
        Current state
    u : float
        Input sample

    Returns
    -------
    x_next : np.ndarray
        Next state
    y : float
        Output sample
    """
    y = float((C @ x)[0, 0] + (D[0, 0] * u))
    x_next = A @ x + B * u
    return x_next, y


def apply_ss_filter(
    u: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    C: np.ndarray,
    D: np.ndarray,
    x0: np.ndarray | None = None,
) -> np.ndarray:
    """
    Apply a discrete-time state-space system to a 1D signal.

    Parameters
    ----------
    u : np.ndarray
        Input signal
    x0 : np.ndarray or None
        Initial state (shape (2, 1)); zero state if None

    Returns
    -------
    np.ndarray
        Output signal
    """
    u = np.asarray(u, dtype=float)

    if x0 is None:
        x = np.zeros((2, 1), dtype=float)
    else:
        x = np.asarray(x0, dtype=float).reshape(2, 1)

    y = np.empty_like(u, dtype=float)

    for n in range(len(u)):
        x, y[n] = ss_step(x, A, B, C, D, float(u[n]))

    return y
