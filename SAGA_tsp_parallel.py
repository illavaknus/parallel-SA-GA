from mpi4py import MPI
import numpy as np
import time
import sys
import random
import math
import copy
from SAGAProblem import SAGAProblem
from SAGATravellingSalesman import SAGATravellingSalesman
from SAGASolver import SAGASolver
import saga_utils


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

	# Wait until data has been broadcast and then start the timer
	comm.barrier()
	if rank == 0:
		start =  MPI.Wtime()

	saga_tsp = SAGATravellingSalesman(saga_utils.shuffle_list(range(len(dist_matrix)), len(dist_matrix)), dist_matrix)
	
	saga_solver = SAGASolver()
	saga_solver.initialize(saga_tsp)

	# if(rank == 0):
	# 	print "["+str(rank)+"]: Distributed data of size : ", len(dist_matrix)

	# if (rank != 0):
	# 	print "["+str(rank)+"]: Received data of size : ", len(dist_matrix)

	saga_solver.solve(comm, start, 0)

	# Stop the time and print the total run time
	# if rank == 0:
	# 	stop = MPI.Wtime()
	# 	print "Running time: %.5f" % (stop - start)


