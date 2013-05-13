"""
Abstract class for problems that can be solved
using SAGA. All the methods below must be implemented
for use with the SAGASolver class
"""
class SAGAProblem(object):

		def __init__(self):
			"""
			Instantiate a new SAGAProblem object
			"""

		def get_energy(self):
			"""
			Calculates the energy of the SAGAProblem
			"""

		def generate_candidate(self, L):
			"""
			Creates a new candidate by performing up to
			L different swaps on the SAGAProblem
			"""

		def criteria_fulfilled(self, iteration, energy):
			"""
			Returns true if the criteria for solving the
			SAGAProblem has been met 
			"""
