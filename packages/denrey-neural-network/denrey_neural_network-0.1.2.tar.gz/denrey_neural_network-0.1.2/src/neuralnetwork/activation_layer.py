# Neural Network - Activation Layer

# ================================================================================================ #
# Imports

import numpy as np
import numpy.typing as npt

from typing import Callable

from neuralnetwork.layer import Layer

# ================================================================================================ #

class ActivationLayer(Layer):
	def __init__(
		self,
		activation_tuple: tuple[
			Callable[[npt.ArrayLike], npt.NDArray[np.float64]],
			Callable[[npt.ArrayLike], npt.NDArray[np.float64]]
		]
	):
		
		self.activation: Callable[[npt.ArrayLike], npt.NDArray[np.float64]] = activation_tuple[0]
		self.activation_prime: Callable[[npt.ArrayLike], npt.NDArray[np.float64]] = activation_tuple[1]
	
	# ================================================== #
	# Class Methods

	# ================================================== #
	# Dunder Methods

	# ================================================== #
	# Property Methods

	# ================================================== #
	# Set Methods

	# ================================================== #
	# Other Methods

	def forward_propagation(self, input_data: np.ndarray) -> np.ndarray:
		self.input: np.ndarray = input_data
		self.output: np.ndarray = self.activation(self.input)
		return self.output

	def backward_propagation(self, output_error: np.ndarray, learning_rate: float) -> np.ndarray:
		return self.activation_prime(self.input) * output_error

# ================================================================================================ #