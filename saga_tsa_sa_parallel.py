from mpi4py import MPI
import numpy as np
import time
import sys
import random
import math
import copy
import saga_utils
import tsa_data_create
import saga_tsa_ga
import SAGATravellingSalesman


def parallel_sa(dist_matrix,comm, p_root=0):
	rank = comm.Get_rank()
	size = comm.Get_size()

	if(rank == 0):
		print "["+str(rank)+"]: In Root Parallel"

	if (rank != 0):
		print "["+str(rank)+"]: In child parallel"

	# set the number of cities and route
	num_cities = len(dist_matrix)

	cur_route = range(num_cities)
	cur_route = saga_utils.shuffle_list(cur_route, num_cities);

	init_temp = 0.1 + random.random() * num_cities 
	cur_temp = init_temp

	# SA parameters
	reset_temp = 4 
	bound_temp = 1.5
	thermostat = 0.9
	reannealing = 1 * num_cities

	cur_energy = saga_utils.energy_distance(cur_route, dist_matrix)
	best_energy = cur_energy

	best_route = cur_route

	reduction_count = 0
	step_count = 0
	unchanged_count = 0

	all_energies = [0] * reannealing
	all_energies[0] = cur_energy

	fitness = 0

	ga_reannealing = 1

	print "["+str(rank)+"]: Starting SA with energy = ", best_energy, " and init temp = ", init_temp

	while(reduction_count < 160 * reannealing):
		print "["+str(rank)+"]: step = ", reduction_count
		# Boltzman 
		shuffle_count = math.floor(math.sqrt(cur_temp))
		# Fast
		# shuffle_count = math.floor(cur_temp)

		new_route = copy.deepcopy(cur_route)
		new_route = saga_utils.shuffle_list(new_route, shuffle_count)
		new_energy = saga_utils.energy_distance(new_route, dist_matrix)

		delta_energy = new_energy - best_energy

		acc_prob = random.random()

		if(delta_energy < 0 or acc_prob < math.exp(-delta_energy/cur_temp)):
			#record the energy for fitness
			all_energies[reduction_count % reannealing] = cur_energy

			# print unchanged_count
			if delta_energy < 0:
				# print "["+str(rank)+"]: @",step_count," best_energy : ", best_energy, ", unchanged_count : ", unchanged_count
				best_energy = new_energy
				best_route = copy.deepcopy(new_route)
				unchanged_count = 0
			else:
				unchanged_count += 1
			cur_route = copy.deepcopy(new_route)
			cur_energy = new_energy
			reduction_count += 1
			# if unchanged_count == 0:
			# 	print "["+str(rank)+"]: @",step_count," best_energy : ", best_energy, " cur_temp : ", cur_temp, ", unchanged_count : ", unchanged_count

			if(reduction_count % reannealing == 0):
				if ga_reannealing :
					# calculate fitness
					baseline_energy = sum(all_energies)/len(all_energies)
					fitness = 0
					fitness = sum([(baseline_energy - x) for x in all_energies if x < baseline_energy])
					
					# set up fintess and temp exchange data
					all_temps = [0] * size
					all_fitness = [0] * size

					# print "["+str(rank)+"]: reannealing @",step_count, ", fitness : ", fitness, ", cur temp: ", cur_temp

					# print "["+str(rank)+"]: reannealing @",step_count," best_energy : ", best_energy, " cur_temp : ", cur_temp, ", unchanged_count : ", unchanged_count
					comm.barrier();
					# print "["+str(rank)+"]: cur_time : ",cur_time

					all_fitness = comm.gather(fitness, root=0)
					all_temps = comm.gather(cur_temp, root=0)

					if rank == 0:
						print "received fitness : ", all_fitness
						print "received temps: ", all_temps

					all_temps = comm.bcast(all_temps, root=0)
					all_fitness = comm.bcast(all_fitness, root=0)
					
					# print "["+str(rank)+"]: ", all_temps
					# print "["+str(rank)+"]: ", all_fitness

					cur_temp = saga_tsa_ga.ga_temp(all_temps, all_fitness)
				else:
					cur_temp *= thermostat
					if cur_temp < bound_temp:
						cur_temp = reset_temp
				
				cur_time =  MPI.Wtime()
				cur_route = copy.deepcopy(best_route)
				cur_energy = best_energy
				print "["+str(rank)+"]:  @",reduction_count/reannealing, "[", cur_time, "] new temp = ", cur_temp, " energy = ", cur_energy, " baseline = ", baseline_energy, min(all_energies), len(all_energies)
				all_energies = [0] * reannealing


		step_count = step_count + 1

	print "["+str(rank)+"]: final best_energy = ", best_energy, " after total runs = ", reduction_count
	# return (best_energy, best_route, step_count)


if __name__ == '__main__':
	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()

	if(len(sys.argv) < 2):
		print "usage : python saga_tsa_sa_parallel.py [data file name]"
		sys.exit(-1)

	if rank == 0:
		# read the filename from cmdline
		filename = str(sys.argv[1])
		
		# read the data file and build the distance matrix
		dist_matrix = saga_utils.parse_xml_data(filename)
		# dist_matrix = tsa_data_create.tsa_data()
	else:
		dist_matrix = None

	comm.barrier()
	start =  MPI.Wtime()
	
	# Broadcast the arrays
	dist_matrix = comm.bcast(dist_matrix, root=0)

	if(rank == 0):
		print "["+str(rank)+"]: Distributed data of size : ", len(dist_matrix)

	if (rank != 0):
		print "["+str(rank)+"]: Received data of size : ", len(dist_matrix)

	parallel_sa(dist_matrix,comm)
