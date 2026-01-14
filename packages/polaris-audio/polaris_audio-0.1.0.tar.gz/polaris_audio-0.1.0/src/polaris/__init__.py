"""
polaris-audio

A research-oriented DSP library for sound synthesis and analysis
based on poles, transfer functions, and state-space representations.

polaris focuses on *designing sound in the z-plane* rather than
using fixed filter recipes.
"""

# --- core: poles / transfer / state-space ---

from .core.poles import (
    omega_from_f0,
    r_from_T60,
    pole_from_f0_T60,
    conjugate_poles_from_f0_T60,
)

from .core.transfer import (
    ar2_from_poles,
    ar2_from_parameters,
    ma2_from_zeros,
    ma2_from_parameters,
    ma2_from_attack_exp3,
    ma2_from_click_diff,
)

from .core.statespace import (
    arma22_controllable_canonical_ss,
    ss_step,
    apply_ss_filter,
)

# --- excitation ---

from .excitation.basic import make_excitation

# --- signal utilities ---

from .signal.normalize import normalize

__all__ = [
    # poles
    "omega_from_f0",
    "r_from_T60",
    "pole_from_f0_T60",
    "conjugate_poles_from_f0_T60",

    # transfer
    "ar2_from_poles",
    "ar2_from_parameters",
    "ma2_from_zeros",
    "ma2_from_parameters",
    "ma2_from_attack_exp3",
    "ma2_from_click_diff",

    # state-space
    "arma22_controllable_canonical_ss",
    "ss_step",
    "apply_ss_filter",

    # excitation
    "make_excitation",

    # signal
    "normalize",
]
