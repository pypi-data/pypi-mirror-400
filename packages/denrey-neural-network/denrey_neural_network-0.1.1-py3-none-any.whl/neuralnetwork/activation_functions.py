# Neural Network - Activation Functions

# ================================================================================================ #
# Imports

import numpy as np
import numpy.typing as npt

from typing import Callable

# ================================================================================================ #

def tanh(x: npt.ArrayLike) -> npt.NDArray[np.float64]:
	return np.tanh(x)

def tanh_prime(x: npt.ArrayLike) -> npt.NDArray[np.float64]:
	return 1 - np.tanh(x)**2

# ================================================================================================ #

# {'name': (function, derivative)}
activation_functions: dict[
	str,
	tuple[
		Callable[[npt.ArrayLike], npt.NDArray[np.float64]],
		Callable[[npt.ArrayLike], npt.NDArray[np.float64]]]
] = {
	'tanh': (tanh, tanh_prime),
}