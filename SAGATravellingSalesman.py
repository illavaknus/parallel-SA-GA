import SAGAProblem
import math
import random
import numpy as np
import copy

"""
Class for defining the Travelling Salesman Problem
to be solved by SAGASolver using parallel SAGASolver
"""

class SAGATravellingSalesman(SAGAProblem):
	"""
	Instantiate a new SAGAProblem object
	"""
	def __init__(self, cities_list, dist_mat):
		self.route = cities_list
		self.distance_matrix = dist_mat
		self.num_cities = len(cities_list)
		self.energy = 0
		self.max_iterations = 20 * num_cities

	"""
	Calculates the energy of the SAGAProblem
	"""
	def get_energy(self):
		total_distance = 0
		for i in range(self.num_cities):
			# print self.dist_matrix[route[i]][route[(i+1)%self.num_cities]]
			if i == len(route) - 1:
				total_distance += self.dist_matrix[route[i]][route[0]]
			else:
				total_distance += self.dist_matrix[route[i]][route[(i+1)]]
		self.energy = total_distance
		return self.energy
	
	"""
	Creates a new candidate by performing up to
	L different swaps on the SAGAProblem
	"""
	def generate_candidates(self, L):
		new_route = copy.deepcopy(self.route)
		new_dist_mat = copy.deepcopy(self.dist_matrix)

		if(L == None):
			new_route = np.random.shuffle(new_route)
		else:
			assert(L <= self.num_cities)
			i = 0
			while i < L:
				index_one = np.random.randint(0,self.num_cities)
				index_two = np.random.randint(0,self.num_cities)
				if index_two == index_one:
					i -= 1
				else:
					new_route[index_one], new_route[index_two] = new_route[index_two], new_route[index_one]
					i += 1
		
		return SAGATravellingSalesman(np.random.shuffle(new_route), new_dist_mat)
	
	"""
	Returns true if the criteria for solving the
	SAGAProblem has been met 
	"""
	def criteria_fullfilled(self, iteration, energy):
		return (iteration >= self.max_iterations)
