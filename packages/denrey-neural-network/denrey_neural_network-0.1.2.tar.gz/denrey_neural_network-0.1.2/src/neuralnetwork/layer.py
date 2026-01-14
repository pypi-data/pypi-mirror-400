# Neural Network - Layer

# ================================================================================================ #
# Imports

import numpy as np

# ================================================================================================ #

class Layer:
	def __init__(self):
		self.input = None
		self.output = None
	
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

	# computes the output Y of a layer for a given input X
	def forward_propagation(self, input_data: np.ndarray) -> np.ndarray:
		raise NotImplementedError

	# computes dE/dX for a given dE/dY (and update parameters if any)
	def backward_propagation(self, output_error: np.ndarray, learning_rate: float) -> np.ndarray:
		raise NotImplementedError

# ================================================================================================ #