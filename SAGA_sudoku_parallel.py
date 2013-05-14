
import time
import sys
import random
import math
import copy
import saga_utils
import numpy as np
from mpi4py import MPI
from SAGAProblem import SAGAProblem
from SAGASudokuProblem import SAGASudokuProblem
from SAGASolver import SAGASolver



if __name__ == '__main__':
	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()

	if(len(sys.argv) < 1):
		print "usage : python SAGA_tsa_sudoku_parallel.py"
		sys.exit(-1)

	# if rank == 0:
	# 	# read the filename from cmdline
	# 	filename = str(sys.argv[1])
		
	# 	# read the data file and build the distance matrix
	# 	dist_matrix = saga_utils.parse_xml_data(filename)
	# 	# dist_matrix = tsa_data_create.tsa_data()
	# else:
	# 	dist_matrix = None

	# comm.barrier()
	# start =  MPI.Wtime()
	
	# # Broadcast the arrays
	# dist_matrix = comm.bcast(dist_matrix, root=0)

	saga_sudoku = SAGASudokuProblem()
	
	saga_solver = SAGASolver()
	saga_solver.initialize(saga_sudoku)

	# saga_sudoku.print(res)
	# if(rank == 0):
	# 	print "["+str(rank)+"]: Distributed data of size : ", len(dist_matrix)

	# if (rank != 0):
	# 	print "["+str(rank)+"]: Received data of size : ", len(dist_matrix)

	saga_solver.run_annealing(comm, 0)


