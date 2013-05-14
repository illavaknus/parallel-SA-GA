"""
SAGASolver : A class for solving SAGAProblems using SAGA. 
"""
from mpi4py import MPI
from random import randint, random, shuffle
from copy import deepcopy
from math import sqrt, exp, floor, log, ceil
from scipy.stats import mode
from saga_utils import accumulate
import numpy as numpy
import sys
import SAGAProblem

"""
Defines for configurations
"""
__TEMP_CODING__ = 1 	# 0 : 10^X, 1 : exponential
__PARALLEL__ = 1 		# 1 : parallel with GA, 0 : serial without GA

class SAGASolver :
	def __init__(self) :
		"""TODO: Set better default values """
		# set default values
		self.config_size = 0
		self.min_temp =  0.01
		self.max_temp = 10000
		self.init_temp = self.min_temp + random() * self.max_temp
		self.reannealing_count = 100
		self.cur_temp = self.init_temp
		self.cur_energy = 0
		self.best_solution = None
		self.total_steps = 1
		self.all_energies = None
		self.fitness = 0
		self.max_generations = 1
		self.prob_mutation = 0.1
		self.prob_crossover = 0.1

	def set_shuffle_count(self):
		self.shuffle_count = int(ceil(sqrt(self.cur_temp)))

	def initialize(self, problem_object):
		self.problem = deepcopy(problem_object)
		self.config_size = self.problem.get_size()
		
		self.max_temp = self.config_size ** 2
		self.init_temp = self.min_temp + random() * (self.max_temp - self.min_temp)
		self.cur_temp = self.init_temp

		self.reannealing_count = self.config_size * 2
		self.all_energies = []

	def binary_to_temp(self, binary):
		# If using 10^X bit encoding
		if __TEMP_CODING__ == 0 :
			x_max = log(self.max_temp, 10)
			x_min = log(self.min_temp, 10)
		# else using exponential
		else :
			x_max = log(self.max_temp)
			x_min = log(self.min_temp)

		x_integer = sum([b*(2**(9-i)) for i,b in enumerate(binary)])
		x = (x_integer/1023.0) * (x_max - x_min) + x_min
		
		# If using 10^X bit encoding
		if __TEMP_CODING__ == 0:
			temp = 10**x
		else:
			temp = exp(x)
		return temp

	def temp_to_binary(self, temp):
		max_temp = 10000
		min_temp = 0.01

		# If using 10^X bit encoding
		if __TEMP_CODING__ == 0 :
			x_max = log(self.max_temp, 10)
			x_min = log(self.min_temp, 10)
			x = log(temp, 10)
		else :
			x_max = log(self.max_temp)
			x_min = log(self.min_temp)
			x = log(temp)

		x_integer = int(((x-x_min)/(x_max-x_min)) * 1023)
		x_binary = [int(x) for x in list('{0:0b}'.format(x_integer))]
		while len(x_binary) != 10:
			x_binary.insert(0,0)

		return x_binary

	def crossover(self, temp1, temp2):
		x1_binary = self.temp_to_binary(temp1)
		x2_binary = self.temp_to_binary(temp2)

		# print "Before crossover"
		# print x1_binary
		# print x2_binary

		ind = randint(0, 9)
		# print "Crossing over index %d" % ind

		x1_end = x1_binary[ind:][0]
		x2_end = x2_binary[ind:][0]

		x1_binary[ind] = x2_end
		x2_binary[ind] = x1_end

		# print "After crossover"
		# print x1_binary
		# print x2_binary
		return self.binary_to_temp(x1_binary)

	def mutate(self, temp):
		x_binary = self.temp_to_binary(temp)
		
		ind = randint(0, 9)
		# print x_binary
		# print "Mutating index %d" % ind

		if x_binary[ind] == 0:
			x_binary[ind] = 1
		else:
			x_binary[ind] = 0

		# print "After mutation"
		# print x_binary

		return self.binary_to_temp(x_binary)

	def reanneal(self, temp_values, fitness_values):
		size = len(temp_values)

		current_pop = range(size)

		#print temp_values
		#print fitness_values
		#print current_fitness, scaled_fitness, incremental_fitness

		cur_generation = 0
		while(cur_generation < self.max_generations):
			current_fitness = sum([fitness_values[x] for x in current_pop])
			if current_fitness == 0 : current_fitness = 1
			scaled_fitness = [fitness_values[x]/current_fitness for x in current_pop]
			incremental_fitness = list(accumulate(scaled_fitness))
		
			new_pop = []

			for i in current_pop :
				rand = random()
				for i in range(len(incremental_fitness)):
					if rand < incremental_fitness[i]: break
				new_pop.append(current_pop[i-1])

			cur_generation += 1

		new_index = int(mode(new_pop)[0][0])
		new_temp = temp_values[new_index]

		if random() < self.prob_crossover :
			crossed_index = randint(0,len(new_pop)-1)
			while crossed_index == new_index:
				crossed_index = randint(0,len(new_pop)-1)
			crossed_temp = temp_values[crossed_index]
			newcrossed_temp = self.crossover(new_temp,crossed_temp)
			# print "Temperature crossed over from %.5f to %.5f" % (new_temp, newcrossed_temp)
		

		# mutation
		if random() < self.prob_mutation :
			mutated_temp = self.mutate(new_temp)
			# print "Temperature mutated from %.5f to %.5f" % (new_temp, mutated_temp)
			new_temp = mutated_temp
		# 	mutation = (-1 + random() * 2) * (self.mutation_delta * new_temp)
		# 	# rand_index = random.randint(0,size)
		# 	if mutation+new_temp < 0 :
		# 		print self.mutation_delta, mutation, new_temp
		# 	new_temp += mutation

		# print new_temp
		return new_temp


	def solve(self, comm, start, root = 0):
		rank = comm.Get_rank()
		size = comm.Get_size()

		# if run with only 1 process, switch to serial version
		if size == 1 : 
			__PARALLEL__ = 0
			self.reannealing_count = 10
		else:
			__PARALLEL__ = 1

		self.cur_energy = self.problem.get_energy()
		self.all_energies.append(self.cur_energy)

		self.best_solution = deepcopy(self.problem)

		while(not self.problem.criteria_fulfilled(self.total_steps, self.cur_energy)):
			self.set_shuffle_count()
			new_candidate = self.problem.generate_candidate(self.shuffle_count)

			delta_energy = new_candidate.get_energy() - self.cur_energy

			if (delta_energy < 0 or random() < exp(-delta_energy/self.cur_temp)):
				# update current problem if new problem is accepted
				self.cur_energy = new_candidate.get_energy()
				self.problem = deepcopy(new_candidate)				

				# update best solution, if new energy is lower
				if new_candidate.get_energy() < self.best_solution.get_energy() :
					self.best_solution = deepcopy(new_candidate)
			
			self.all_energies.append(self.cur_energy)

			# reanneal to get new temperature
			if self.total_steps % self.reannealing_count == 0:
				if __PARALLEL__ == 1 :

					all_energy_sums = comm.gather(sum(self.all_energies), root)
					all_energy_counts = comm.gather(len(self.all_energies), root)
					baseline_energy = 0
					if rank == 0:
						baseline_energy = sum(all_energy_sums)/sum(all_energy_counts)
					baseline_energy = comm.bcast(baseline_energy, root)

					fitness = 0
					eks = [(baseline_energy - x) for x in self.all_energies if x < baseline_energy]
					fitness = float(sum(eks))
					
					all_temps = [0] * size
					all_fitness = [0] * size

					comm.barrier()

					all_fitness = comm.gather(fitness, root)
					all_temps = comm.gather(self.cur_temp, root)

					# if rank == 0:
					# 	for i in range(len(all_fitness)):
					# 		print "Temp %.2f has fitness-> %.2f |" % (all_temps[i], all_fitness[i])

					all_temps = comm.bcast(all_temps, root)
					all_fitness = comm.bcast(all_fitness, root)

					self.cur_temp = self.reanneal(all_temps, all_fitness)

					# reset all energies for the next set of annealings
					self.all_energies = []

				# if running with only 1 process, switch to a serial verion
				else:
					self.cur_temp *= 0.9
					if self.cur_temp < 1 : self.cur_temp = sqrt(self.max_temp)

			# update counter
			self.total_steps += 1

		# Print the results and exit if one process 
		# exited loop before others
		if self.best_solution.get_energy() == 0: 
			# print "[",rank,"]: Got best energy of 0!"
			self.best_solution.print_results()
			stop = MPI.Wtime()
			print "Running time: %.5f" % (stop - start)
			print "EXITING! Don't worry!"
			comm.Abort()

		# Else choose the best solution and exit
		else : 
			if rank == 0:
				solutions = []
				solutions.append(self.best_solution)

				# Get results from all other processes
				for i in range(size-1):
					status = MPI.Status()
					solution = comm.recv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG,status=status)
					solutions.append(solution)

				# Print the best solution
				best_energy = solutions[0].get_energy()
				best_solution = deepcopy(solutions[0])
				for solution in solutions:
					if best_energy > solution.get_energy():
						best_energy = solution.get_energy()
						best_solution = deepcopy(solution)

				best_solution.print_results()
				stop = MPI.Wtime()
				print "Running time: %.5f" % (stop - start)
			else :
				comm.send(self.best_solution, dest = 0)
				return
