from mpi4py import MPI
import numpy as np
import time
import saga_utils
import sys
import random

if __name__ == '__main__':

	if(len(sys.argv) < 2):
		print "usage : python saga_tsa_sa_serial.py [data file name]"
		sys.exit(-1)
	
	filename = str(sys.argv[1])
	
	dist_matrix = saga_utils.parse_xml_data(filename)
	num_cities = len(dist_matrix)

	route = range(num_cities)

	print route, saga_utils.energy_distance(route, dist_matrix)

	route = saga_utils.shuffle_list(route,50)

	print route, saga_utils.energy_distance(route, dist_matrix)