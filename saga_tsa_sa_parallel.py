from mpi4py import MPI
import numpy as np
import time
import sys
import random
import math
import copy
import saga_utils
import tsa_data_create


def parallel_sa(dist_matrix,comm, p_root=0):
	rank = comm.Get_rank()
	size = comm.Get_size()

	# Broadcast the arrays
	dist_matrix = comm.bcast(dist_matrix, root=p_root)

	if(rank == 0):
		print "["+str(rank)+"]: Distributed data!"

	if (rank != 0):
		print "["+str(rank)+"]: Received data!"

		# set the number of cities and route
		num_cities = len(dist_matrix)

		cur_route = range(num_cities)
		cur_route = saga_utils.shuffle_list(cur_route, num_cities);

		init_temp = 10
		cur_temp = init_temp

		# SA parameters
		reset_temp = 4 
		bound_temp = 1.5
		thermostat = 0.9
		reannealing = 10

		cur_energy = saga_utils.energy_distance(cur_route, dist_matrix)
		best_energy = cur_energy

		best_route = cur_route

		reduction_count = 0
		step_count = 0
		unchanged_count = 0

		print "["+str(rank)+"]: Starting SA with energy = ", best_energy

		while(unchanged_count < 20):
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
				# print unchanged_count
				if delta_energy < 0:
					# print "["+str(rank)+"]: @",step_count," best_energy : ", best_energy, ", unchanged_count : ", unchanged_count
					best_energy = new_energy
					best_route = new_route
					unchanged_count = 0
				else:
					unchanged_count += 1
				cur_route = new_route
				cur_energy = new_energy
				reduction_count += 1
				if unchanged_count == 0:
					print "["+str(rank)+"]: @",step_count," best_energy : ", best_energy, " cur_temp : ", cur_temp, ", unchanged_count : ", unchanged_count

				if(reduction_count % reannealing == 0):
					cur_temp *= thermostat
					# print "["+str(rank)+"]: reannealing! : ", reduction_count ,cur_temp, unchanged_count, best_energy
					if cur_temp < bound_temp :
						# print "["+str(rank)+"]: resetting! : ", cur_temp, " to ", reset_temp
						print "["+str(rank)+"]: @",step_count," best_energy : ", best_energy, " cur_temp : ", cur_temp, ", unchanged_count : ", unchanged_count
						cur_temp = reset_temp

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
	
	# read the filename from cmdline
	filename = str(sys.argv[1])
	
	# read the data file and build the distance matrix
	dist_matrix = saga_utils.parse_xml_data(filename)
	# dist_matrix = tsa_data_create.tsa_data()

	parallel_sa(dist_matrix,comm)
