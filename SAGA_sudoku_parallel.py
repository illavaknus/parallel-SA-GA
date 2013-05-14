
import time
import sys
import random
import math
import copy
import saga_utils
import numpy as np
from math import sqrt
from mpi4py import MPI
from SAGAProblem import SAGAProblem
from SAGASudokuProblem import SAGASudokuProblem
from SAGASolver import SAGASolver



if __name__ == '__main__':
	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()

	data = None

	# If a filename is passed, read the contents of the file into a data array
	if rank == 0 and len(sys.argv) == 2:
		try:
			filename = str(sys.argv[1])
			raw = np.loadtxt(filename, dtype="int")
			data = raw.reshape(1,raw.size)[0]
			n = int(sqrt(len(data)))
			n_sqrt = int(sqrt(n))
			if n != sqrt(len(data)) or n_sqrt != sqrt(n):
			    print "Must pass in a NxN Sudoku where N is a perfect square"
			    comm.Abort(-1)
		except IOError as e:
			print "Unable to load file"
			comm.Abort(-1)
	
	# Broadcast the data
	data = comm.bcast(data, root=0)
	
	# Wait until data has been broadcast and then start the timer
	comm.barrier()
	if rank == 0:
		start =  MPI.Wtime()

	# Initialize the Sudoku and begin the algorithm
	saga_sudoku = SAGASudokuProblem(data)
	saga_solver = SAGASolver()
	saga_solver.initialize(saga_sudoku)
	saga_solver.run_annealing(comm, 0)

	# Stop the time and print the total run time
	if rank == 0:
		stop = MPI.Wtime()
		print "Running time: %.5f" % (start - stop)


