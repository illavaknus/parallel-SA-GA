from SAGAProblem import SAGAProblem
import math
import random
import numpy as np
from copy import deepcopy

"""
Class for defining the Travelling Salesman Problem
to be solved by SAGASolver using parallel SAGASolver
"""

class SAGATravellingSalesman(SAGAProblem):

	def __init__(self, route, dist_mat):
		"""
		Instantiate a new SAGAProblem object
		"""
		assert (route != None)
		assert(dist_mat != None)

		self._dist_mat = deepcopy(dist_mat)
		self._num_cities = len(dist_mat)
		self._route = deepcopy(route)
		self._energy = 0
		self._max_iterations = 160 * 2 * self._num_cities

	def get_energy(self):
		"""
		Calculates the energy of the SAGAProblem
		"""
		total_distance = 0
		for i in range(self._num_cities):
			# print self.dist_matrix[self._route[i]][self._route[(i+1)%self._num_cities]]
			if i == self._num_cities - 1:
				total_distance += self._dist_mat[self._route[i]][self._route[0]]
			else:
				total_distance += self._dist_mat[self._route[i]][self._route[(i+1)]]
		self._energy = total_distance
		return self._energy

	def generate_candidate(self, L):	
		"""
		Creates a new candidate by performing up to
		L different swaps on the SAGAProblem
		"""
		new_route = deepcopy(self._route)
		new_dist_mat = deepcopy(self._dist_mat)

		if(L == None):
			new_route = np.random.shuffle(new_route)
		else:
			assert(L <= self._num_cities)
			i = 0
			while i < L:
				index_one = np.random.randint(0,self._num_cities)
				index_two = np.random.randint(0,self._num_cities)
				if index_two == index_one:
					i -= 1
				else:
					new_route[index_one], new_route[index_two] = new_route[index_two], new_route[index_one]
					i += 1
		
		return SAGATravellingSalesman(new_route, new_dist_mat)
	
	def criteria_fulfilled(self, iteration, energy):
		"""
		Returns true if the criteria for solving the
		SAGAProblem has been met 
		"""
		return (iteration >= self._max_iterations)

	def get_size(self):	
		"""
		Returns hte size of the SAGAProblem, in
		this case the number of cities
		"""
		return self._num_cities

	def get_state(self):
		"""
		Returns the state of the SAGAProblem in 
		this case the route
		"""
		return self._route


	def print_results(self):
		"""
		Print out the contents of the Sudoku
		"""
		print "Solution : ", self._route, " with energy = ", self._energy

