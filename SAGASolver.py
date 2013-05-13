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

class SAGASolver :
	def __init__(self) :
		"""TODO: Set better default values """
		# set default values
		self.config_size = 0
		self.min_temp =  0.1
		self.max_temp = 10000
		self.init_temp = self.min_temp + random() * self.max_temp
		self.reannealing_count = 100
		self.cur_temp = self.init_temp
		self.cur_energy = 0
		self.best_state = None
		self.best_energy = 0
		self.total_steps = 1
		self.all_energies = None
		self.fitness = 0
		self.max_generations = 1
		self.prob_mutation = 0.01
		self.prob_crossover = 0.1

	def set_shuffle_count(self):
		self.shuffle_count = ceil(sqrt(self.cur_temp))

	def initialize(self, problem_object):
		self.problem = deepcopy(problem_object)
		self.config_size = self.problem.get_size()
		
		self.max_temp = self.config_size ** 2
		self.init_temp = self.min_temp + random() * self.max_temp
		self.cur_temp = self.init_temp

		self.reannealing_count = self.config_size * 20
		self.all_energies = []

	def binary_to_temp(self, binary):
		# If using 10^X bit encoding
		# x_max = math.log(max_temp, 10)
		# x_min = math.log(min_temp, 10)
		# else
		x_max = log(self.max_temp)
		x_min = log(self.min_temp)

		x_integer = sum([b*(2**(9-i)) for i,b in enumerate(binary)])
		x = (x_integer/1023.0) * (x_max - x_min) + x_min
		
		# If using 10^X bit encoding
		# temp = 10**x
		# else
		temp = exp(x)
		return temp

	def temp_to_binary(self, temp):
		max_temp = 10000
		min_temp = 0.01

		# If using 10^X bit encoding
		# x_max = math.log(max_temp, 10)
		# x_min = math.log(min_temp, 10)
		# else
		x_max = log(self.max_temp)
		x_min = log(self.min_temp)

		x = log(temp)

		x_integer = int(((x-x_min)/(x_max-x_min)) * 1023)
		x_binary = [int(x) for x in list('{0:0b}'.format(x_integer))]
		while len(x_binary) != 10:
			x_binary.insert(0,0)

		return x_binary

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

		current_fitness = sum([fitness_values[x] for x in current_pop])
		scaled_fitness = [fitness_values[x]/current_fitness for x in current_pop]
		incremental_fitness = list(accumulate(scaled_fitness))

		# print current_fitness, scaled_fitness, incremental_fitness

		cur_generation = 0
		while(cur_generation < self.max_generations):
			new_pop = []
			# print current_pop, new_pop
			# selection
			for i in current_pop :
				rand = random()
				# print rand
				for i in range(len(incremental_fitness)):
					if rand < incremental_fitness[i]: break
				new_pop.append(current_pop[i-1])
				# print new_pop
			
			# update variables
			current_pop = deepcopy(new_pop)
			current_fitness = sum([fitness_values[x] for x in current_pop])

			scaled_fitness = [fitness_values[x]/current_fitness for x in current_pop]
			incremental_fitness = list(accumulate(scaled_fitness))
			cur_generation += 1

		# print new_pop
		#print fitness_values
		#print scaled_fitness
		new_temp = temp_values[int(mode(new_pop)[0][0])]

		# crossover
		# if random() < self.prob_crossover :
		

		# mutation
		if random() < self.prob_mutation :
			mutated_temp = self.mutate(new_temp)
			print "Temperature mutated from %.5f to %.5f" % (new_temp, mutated_temp)
			new_temp = mutated_temp
		# 	mutation = (-1 + random() * 2) * (self.mutation_delta * new_temp)
		# 	# rand_index = random.randint(0,size)
		# 	if mutation+new_temp < 0 :
		# 		print self.mutation_delta, mutation, new_temp
		# 	new_temp += mutation

		# print new_temp
		return new_temp


	def run_annealing(self, comm, root = 0):
		rank = comm.Get_rank()
		size = comm.Get_size()

		self.cur_energy = self.problem.get_energy()
		self.all_energies.append(self.cur_energy)

		self.best_energy = self.cur_energy
		self.best_state = self.problem.get_state()

		while(not self.problem.criteria_fullfilled(self.total_steps, self.cur_energy)):
			self.set_shuffle_count()
			new_candidate = self.problem.generate_candidates(self.shuffle_count)

			delta_energy = new_candidate.get_energy() - self.cur_energy

			if (delta_energy < 0 or random() < exp(-delta_energy/self.cur_temp)):
				# update current problem if new problem is accepted
				self.cur_energy = new_candidate.get_energy()
				self.problem = deepcopy(new_candidate)
				

				# update best state, if new energy is lower
				if new_candidate.get_energy() < self.best_energy :
					self.best_energy = self.cur_energy
					self.best_state = self.problem.get_state()
					#self.all_energies.append(self.cur_energy)
			
			self.all_energies.append(self.cur_energy)

			# reanneal to get new temperature
			if self.total_steps % self.reannealing_count == 0:
				#print "[",str(rank),"]: all_energies : ", self.all_energies

				all_energy_sums = comm.gather(sum(self.all_energies), root)
				all_energy_counts = comm.gather(len(self.all_energies), root)
				baseline_energy = 0
				if rank == 0:
					baseline_energy = sum(all_energy_sums)/sum(all_energy_counts)
					print "Baseline Energy: %.5f" % baseline_energy
				baseline_energy = comm.bcast(baseline_energy, root)

				fitness = 0
				eks = [(baseline_energy - x) for x in self.all_energies if x < baseline_energy]
				fitness = sum(eks)
				# fitness = sum([(baseline_energy - x) for x in self.all_energies if x < baseline_energy])
				print "[",str(rank),"]: Temperature = %.5f Fitness = %.5f Best Energy %.5f EK-length %d" % (self.cur_temp, fitness, self.best_energy, len(eks))
				#print "[",str(rank),"]: Energies: ", self.all_energies

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

			# update varaibles
			self.total_steps += 1

		print "[",str(rank),"]: Final Energy : ", self.best_energy

