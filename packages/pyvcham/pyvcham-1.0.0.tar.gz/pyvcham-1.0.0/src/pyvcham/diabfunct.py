"""
This module contains the diabatic functions.

New diabatic functions can be added by defining a new function and updating the 
:data:`potential_functions`, :data:`n_var`, :data:`initial_guesses`, and 
:data:`kappa_compatible` dictionaries accordingly.

Available Potential Types
-------------------------
- ``"ho"``: Harmonic oscillator
- ``"morse"``: General Morse potential
- ``"antimorse"``: Anti-Morse potential (uses general_morse with negative alpha)
- ``"quartic"``: General quartic potential

Functions
---------
- :func:`harmonic_oscillator`
- :func:`general_quartic_potential`
- :func:`general_morse`

Variables
---------
- :data:`potential_functions`
- :data:`n_var`
- :data:`initial_guesses`
- :data:`kappa_compatible`
"""

import numpy as np
import tensorflow as tf

@tf.function
def harmonic_oscillator(q: tf.Tensor, omega: tf.Tensor, params: list) -> tf.Tensor:
    """
    Compute the harmonic oscillator potential.

    The potential is given by:

    .. math:: V(q) = \\frac{1}{2} \\omega q^2 + \\frac{1}{2} k_1 q^2

    where:
    - :math:`q` is the displacement along a normal mode.
    - :math:`\\omega` is the frequency of the mode.
    - :math:`k_1` is an additional quadratic coupling constant.

    Parameters
    ----------
    q : tf.Tensor
        Tensor of displacements along a normal mode, with shape suitable for broadcasting. Must be dtype tf.float32.
    omega : tf.Tensor
        Tensor representing the mode frequency, scalar or broadcast-compatible with `q`. Must be dtype tf.float32.
    params : list
        List with one element, `k1`, the quadratic constant, scalar or broadcast-compatible with `q`.

    Returns
    -------
    tf.Tensor
        Tensor of diabatic potential energy values, matching the shape of `q`.
    """
    k1 = params[0]
    q = tf.cast(q, tf.float32)
    omega = tf.cast(omega, tf.float32)
    k1 = tf.cast(k1, tf.float32)
    HALF = tf.constant(0.5, dtype=tf.float32)
    return HALF * omega * tf.math.square(q) + HALF * k1 * tf.math.square(q)

@tf.function
def general_quartic_potential(q: tf.Tensor, omega: tf.Tensor, params: list) -> tf.Tensor:
    """
    Compute the general quartic potential for a diabatic state.

    This function computes a quartic potential with quadratic and quartic terms, ideal for modeling anharmonic vibrational effects, such as bond stretching, in quantum chemistry.

    The potential is defined as:

    .. math:: V(q) = \\frac{1}{2} \\omega^2 q^2 + \\frac{1}{2} k_2 q^2 + \\frac{1}{24} k_3 q^4

    where:
    - :math:`q` is the displacement along a normal mode.
    - :math:`\\omega` is the mode frequency.
    - :math:`k_2` is an additional quadratic coefficient.
    - :math:`k_3` is the quartic coefficient introducing anharmonicity.

    Parameters
    ----------
    q : tf.Tensor
        Tensor of displacements, broadcast-compatible shape, dtype tf.float32.
    omega : tf.Tensor
        Tensor of mode frequency, scalar or broadcast-compatible with `q`, dtype tf.float32.
    params : list
        List with two elements:
        - `k2`: Quadratic coefficient.
        - `k3`: Quartic coefficient.
        Both scalar or broadcast-compatible with `q`.

    Returns
    -------
    tf.Tensor
        Tensor of potential energy values, matching `q`’s shape.

    """
    k2, k3 = params[0], params[1]
    q = tf.cast(q, tf.float32)
    omega = tf.cast(omega, tf.float32)
    k2 = tf.cast(k2, tf.float32)
    k3 = tf.cast(k3, tf.float32)
    HALF = tf.constant(0.5, dtype=tf.float32)
    ONE_OVER_24 = tf.constant(1.0 / 24.0, dtype=tf.float32)
    return (
        HALF * omega * tf.math.square(q)
        + HALF * k2 * tf.math.square(q)
        + ONE_OVER_24 * k3 * tf.math.pow(q, 4)
    )

@tf.function
def general_morse(q: tf.Tensor, params: list, gs: bool = False) -> tf.Tensor:
    """
    Compute the general Morse potential.

    The Morse potential models anharmonic bond stretching in diatomic molecules, widely used in quantum chemistry for potential energy surfaces.

    The potential is:

    .. math:: V(q) = D_e \\left(1 - e^{-\\alpha (q - q_0)}\\right)^2 - D_e \\left(1 - e^{-\\alpha q_0}\\right)^2

    where:
    - :math:`D_e` is the dissociation energy.
    - :math:`\\alpha` is the range parameter (well width).
    - :math:`q_0` is the equilibrium bond distance.
    - The offset ensures :math:`V(0) = 0`.

    Parameters
    ----------
    q : tf.Tensor
        Tensor of displacements (bond lengths), broadcast-compatible shape, dtype tf.float32.
    params : list
        List with three elements:
        - `De`: Dissociation energy, scalar or tensor.
        - `alpha`: Range parameter, scalar or tensor.
        - `q0`: Equilibrium bond distance, scalar or tensor.
        All broadcast-compatible with `q`.

    Returns
    -------
    tf.Tensor
        Tensor of potential energy values, matching `q`’s shape.
    """
    De, alpha, q0 = params[0], params[1], params[2]
    q = tf.cast(q, tf.float32)
    De = tf.cast(De, tf.float32)
    alpha = tf.cast(alpha, tf.float32)
    q0 = tf.cast(q0, tf.float32)
    if gs:
        q0 = tf.cast(0.0, tf.float32)
    ONE = tf.constant(1.0, dtype=tf.float32)

    # Compute the vertical offset at q=0
    offset = De * tf.math.square(tf.exp(alpha * q0) - ONE)

    morse = De * tf.math.square(tf.exp(-alpha * (q - q0)) - ONE)
    return morse - offset


# Potential Functions Dictionary
potential_functions = {
    "ho": harmonic_oscillator,
    "morse": general_morse,
    "antimorse": general_morse,
    "quartic": general_quartic_potential,
}

# Number of Variables for Each Function
n_var = {
    "ho": 1,
    "morse": 3,
    "antimorse": 3,
    "quartic": 2,
}

# Initial Guesses for Each Potential Type
initial_guesses = {
    "ho": np.array([0.5]),
    "morse": np.array([5.0, 0.5, 0.0]),
    "antimorse": np.array([5.0, -0.5, 0.0]),
    "quartic": np.array([0.0, 0.0005]),
}

# Kappa Compatibility (those functions that could be used together with kappa)
kappa_compatible = {
    "ho": True,
    "morse": False,      # Morse potential has in its definition q - q0
    "antimorse": False,  # Morse potential has in its definition q - q0
    "quartic": True,
}