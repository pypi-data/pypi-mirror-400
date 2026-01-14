"""
This module provides coupling functions for the vibronic coupling Hamiltonian.

Currently, the module supports linear coupling, with a design that allows extension to additional coupling types.

New coupling functions can be added by defining a new function and updating the :data:`COUPLING_TYPES`, :data:`coupling_funct`, :data:`n_var`, and :data:`initial_guesses` dictionaries accordingly.

Functions
---------
- :func:`linear_coupling`: Computes the linear coupling function.

Variables
---------
- :data:`COUPLING_TYPES`: List of supported coupling types.
- :data:`coupling_funct`: Dictionary mapping coupling types to their implementation functions.
- :data:`n_var`: Dictionary specifying the number of parameters per coupling function.
- :data:`initial_guesses`: Dictionary of default initial parameter guesses for each coupling type.
"""

import tensorflow as tf

# Constants
INITIAL_GUESS = 1e-3  # Default initial guess for coupling constants

@tf.function
def linear_coupling(q: tf.Tensor, k1: tf.Tensor) -> tf.Tensor:
    """
    Compute the linear coupling function.

    The linear coupling is defined as:

    .. math:: f(q) = k_1 \cdot q

    where :math:`q` is the displacement along a normal mode, and :math:`k_1` is the linear coupling constant.

    Parameters
    ----------
    q : tf.Tensor
        Tensor of displacements, typically along a normal mode, with dtype tf.float32.
    k1 : tf.Tensor or float
        Coupling constant as a tensor or scalar. If a float is provided, it is converted to a ``tf.Tensor`` with dtype tf.float32.

    Returns
    -------
    tf.Tensor
        Tensor of computed linear coupling values with dtype tf.float32.
    """
    # Ensure inputs are float32
    q = tf.cast(q, tf.float32)
    k1 = tf.cast(k1, tf.float32)
    
    return tf.multiply(q, k1)

# List of types of coupling functions
COUPLING_TYPES = ["linear"]

# Coupling functions dictionary for use in other modules
coupling_funct = {
    "linear": linear_coupling
}

# Number of variables for each coupling function
n_var = {
    "linear": 1
}

# Initial guesses for each coupling type
initial_guesses = {
    "linear": INITIAL_GUESS
}