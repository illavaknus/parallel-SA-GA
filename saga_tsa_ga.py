import random
from scipy.stats import mode
from copy import deepcopy

def accumulate(list_):
	sum_ = 0
	for x in list_:
		sum_ += x
		yield sum_

# def ga_next_pop(pop, fitness):


def ga_temp(temp, fitness):
	max_gen = 20
	prob_mutation = 0.2
	prob_crossover = 0.95
	mutation_delta = 0.01

	size = len(temp)

	current_pop = range(size)

	current_fitness = sum([fitness[x] for x in current_pop])
	scaled_fitness = [fitness[x]/current_fitness for x in current_pop]
	incremental_fitness = list(accumulate(scaled_fitness))

	cur_gen = 0

	while (cur_gen < max_gen) : 
		new_pop = []
		# print current_pop, new_pop
		# selection
		for i in current_pop :
			rand = random.random()
			# print rand
			new_pop.append(next(x[0] for x in enumerate(incremental_fitness) if x[1] > rand))
			# print new_pop
		
		# update variables
		current_pop = deepcopy(new_pop)
		current_fitness = sum([fitness[x] for x in current_pop])
		scaled_fitness = [fitness[x]/current_fitness for x in current_pop]
		incremental_fitness = list(accumulate(scaled_fitness))
		cur_gen += 1

	print new_pop
	new_temp = temp[int(mode(new_pop)[0][0])]

	# crossover
	'''if random.random() < prob_crossover :
	'''

	# mutation
	if random.random() < prob_mutation :
		mutation = (-1 + random.random() * 2) * (mutation_delta * new_temp)
		# rand_index = random.randint(0,size)
		if mutation+new_temp < 0 :
			print mutation_delta, mutation, new_temp
		new_temp += mutation

	# print new_temp

	return new_temp
