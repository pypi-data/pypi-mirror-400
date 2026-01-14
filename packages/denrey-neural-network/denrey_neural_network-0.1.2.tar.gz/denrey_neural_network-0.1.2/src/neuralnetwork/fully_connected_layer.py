# Neural Network - Fully Connected Layer

# ================================================================================================ #
# Imports

import numpy as np

from neuralnetwork.layer import Layer

# ================================================================================================ #

class FullyConnectedLayer(Layer):
	def __init__(self, input_size: int, output_size: int):
		self.weights = np.random.rand(input_size, output_size) - 0.5
		self.bias = np.random.rand(1, output_size) - 0.5
	
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

	def forward_propagation(self, input_data: np.ndarray):
		self.input = input_data
		self.output = np.dot(self.input, self.weights) + self.bias
		return self.output

	def backward_propagation(self, output_error: np.ndarray, learning_rate: float):
		input_error = np.dot(output_error, self.weights.T)
		weights_error = np.dot(self.input.T, output_error)

		self.weights -= learning_rate * weights_error
		self.bias -= learning_rate * output_error
		return input_error

# ================================================================================================ #