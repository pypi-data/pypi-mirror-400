# Neural Network - Neural Network

# ================================================================================================ #
# Imports

import numpy as np
import numpy.typing as npt
import pickle

from random	import randint
from time	import time
from typing	import Callable, Optional

from neuralnetwork.activation_functions	import activation_functions
from neuralnetwork.activation_layer		import ActivationLayer
from neuralnetwork.fully_connected_layer	import FullyConnectedLayer
from neuralnetwork.layer					import Layer
from neuralnetwork.loss_functions			import loss_functions

# ================================================================================================ #
# Generate New Neural Network Structure Helper Functions

def biased_randint(lower_bound: int, upper_bound: int, direction: str, bias_level: int = 1) -> int:
	# Base Case
	if bias_level == 0:
		return randint(lower_bound, upper_bound)
	
	# Recursion
	if direction == 'center':
		center = round(sum([lower_bound, upper_bound]) / 2)
		return randint(
			biased_randint(lower_bound, center, direction, bias_level - 1),
			biased_randint(center, upper_bound, direction, bias_level - 1),
		)

	elif direction == 'right':
		return randint(
			biased_randint(lower_bound, upper_bound, direction, bias_level - 1),
			upper_bound
		)
	else:
		return randint(
			lower_bound,
			biased_randint(lower_bound, upper_bound, direction, bias_level - 1)
		)

def mutate(structure: list[int]) -> list[int]:
	index = randint(1, len(structure) - 2)
	number = structure[index]
	distance = biased_randint(-10, 10, 'center', 3)
	new_number = max(number + distance, 1) # Keep the layer size above 0
	structure[index] = new_number
	return structure

def insert_layer(structure: list[int]) -> list[int]:
	index = randint(1, len(structure) - 1)
	minimum_size = min(structure[index - 1], structure[index])
	maximum_size = max(structure[index - 1], structure[index])
	layer_size = randint(minimum_size, maximum_size)
	result = structure[ : index] + [layer_size] + structure[index : ]
	return result

def remove_layer(structure: list[int]) -> list[int]:
	# Can't go any shorter than two layers (input / output)
	if len(structure) <= 2:
		return structure
	
	index = randint(1, len(structure) - 2)
	result = structure[ : index] + structure[index + 1 : ]
	return result

# ================================================================================================ #

def print_progress_function(i: int, epochs: int, err: float, start_time: float) -> None:
	elapsed_time = time() - start_time
	hours = round(elapsed_time // (60.0 * 60.0))
	minutes = round((elapsed_time % (60.0 * 60.0)) // 60.0)
	seconds = round(elapsed_time % 60.0)

	result: list[str] = []
	result.append(f'epoch {i + 1} / {epochs}')
	result.append('\t')
	result.append(f'error = {round(err, 4)}')
	result.append('\t')
	result.append(f'training time = {hours:02d}:{minutes:02d}:{seconds:02d}')
	print(''.join(result))

# ================================================================================================ #

class NeuralNetwork:
	def __init__(
		self,
		structure: list[int],
		loss_tuple: tuple[
			Callable[[npt.ArrayLike, npt.ArrayLike], np.float64],
			Callable[[npt.ArrayLike, npt.ArrayLike], npt.NDArray[np.float64]]
		] = loss_functions['mse']
	):
		
		self.__structure = structure
		# TODO: Make dunder method
		self.layers: list[Layer] = []
		for i in range(len(structure) - 1):
			self.add_layer(FullyConnectedLayer(structure[i], structure[i + 1]))
			self.add_layer(ActivationLayer(activation_functions['tanh']))

		self.__set_loss_function(loss_tuple)

		self.__current_error_rate: Optional[float] = None
		self.__total_training_time: float = 0.0
		self.__error_rate_by_5_minutes: Optional[float] = None

		# TODO: Error rate by epochs
		self.__total_training_epochs: int = 0
		self.__error_rate_by_10_000_epochs: Optional[float] = None
	
	# ================================================== #
	# Class Methods
	
	@classmethod
	def load(cls, filename: str) -> 'NeuralNetwork':
		if '.pkl' not in filename:
			filename = filename + '.pkl'
		
		with open(filename, 'rb') as file:
			unpickled_instance = pickle.load(file)
		
		return unpickled_instance
	
	@classmethod
	def new(cls, structure: list[int]) -> 'NeuralNetwork':
		return cls(structure)

	# ================================================== #
	# Dunder Methods

	# ================================================== #
	# Property Methods

	@property
	def current_error_rate(self) -> Optional[float]:
		return self.__current_error_rate

	@property
	def error_rate_by_5_minutes(self):
		return self.__error_rate_by_5_minutes
	
	@property
	def structure(self):
		return self.__structure
	
	@property
	def total_training_time(self):
		return self.__total_training_time

	# ================================================== #
	# Set Methods

	# ================================================== #
	# Other Methods

	def add_layer(self, layer: Layer):
		self.layers.append(layer)
	
	def create_related_network(self) -> 'NeuralNetwork':
		new_structure = self.structure.copy()

		number_of_alterations = biased_randint(1, sum(self.structure), 'left', 3)
		for _ in range(number_of_alterations):
			index = biased_randint(0, 2, 'left', 1)
			alteration_function = [mutate, insert_layer, remove_layer][index]
			new_structure = alteration_function(new_structure)

		return self.new(new_structure)
	
	def save(self, filename: str) -> None:
		filename = filename + '.pkl'
		with open(filename, 'wb') as file:
			pickle.dump(self, file)
	
	def predict(self, input_data: np.ndarray) -> list[np.ndarray]:
		samples = len(input_data)
		result: list[np.ndarray] = []

		for i in range(samples):
			output = input_data[i]
			for layer in self.layers:
				output = layer.forward_propagation(output)
			result.append(output)

		return result

	def __set_loss_function(
		self,
		loss_tuple: tuple[
			Callable[[npt.ArrayLike, npt.ArrayLike], np.float64],
			Callable[[npt.ArrayLike, npt.ArrayLike], npt.NDArray[np.float64]]
		]
	):
	
		self.loss = loss_tuple[0]
		self.loss_prime = loss_tuple[1]

	def train(self, x_train: np.ndarray, y_train: np.ndarray, epochs: int = 10_000, learning_rate: float = .01,
		max_time_in_seconds: Optional[float] = None, error_threshold: Optional[float] = None,
		print_progress: bool = False, print_progress_time_interval: float = 1.0):
		
		start_time = time()
		last_print_time = None
		samples = len(x_train)

		err = 0

		# For each epoch
		for i in range(epochs):
			# Check elapsed time
			if max_time_in_seconds is not None:
				if time() > (start_time + max_time_in_seconds):
					break

			err = 0

			# For each sample
			for j in range(samples):
				output = x_train[j]
				for layer in self.layers:
					output = layer.forward_propagation(output)

				err += self.loss(y_train[j], output)
				error = self.loss_prime(y_train[j], output)

				for layer in reversed(self.layers):
					error = layer.backward_propagation(error, learning_rate)

			# calculate average error on all samples
			err /= samples
			if self.__error_rate_by_5_minutes is None:
				if (self.__total_training_time + time() - start_time) >= (5 * 60.0):
					self.__error_rate_by_5_minutes = err

			# Print Progress
			if print_progress:
				if last_print_time is None:
					print_progress_function(i, epochs, err, start_time)
					last_print_time = time()
				else:
					if time() > (last_print_time + print_progress_time_interval):
						print_progress_function(i, epochs, err, start_time)
						last_print_time = time()
			
			# Break if error threshold is reached
			if error_threshold is not None:
				if err <= error_threshold:
					break
			
			self.__current_error_rate = err
	
		self.__total_training_time += time() - start_time

# ================================================================================================ #