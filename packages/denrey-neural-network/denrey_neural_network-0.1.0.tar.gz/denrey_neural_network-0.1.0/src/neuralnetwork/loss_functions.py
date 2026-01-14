# Neural Network - Loss Functions

# ================================================================================================ #
# Imports

import numpy as np
import numpy.typing as npt

from typing import cast

# ================================================================================================ #

def mse(y_true: npt.ArrayLike, y_pred: npt.ArrayLike) -> np.float64:
	result = np.mean(np.power(np.subtract(y_true, y_pred), 2))
	return cast(np.float64, result)

def mse_prime(y_true: npt.ArrayLike, y_pred: npt.ArrayLike) -> npt.NDArray[np.float64]:
	y_t = np.asarray(y_true)
	y_p = np.asarray(y_pred)
	return 2 * (y_p - y_t) / y_t.size

# ================================================================================================ #

# {'name': (function, derivative)}
loss_functions = {
	'mse': (mse, mse_prime)
}