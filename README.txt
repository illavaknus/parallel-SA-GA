README

Project : PSAGA
By : Tunde Agboola and Shashank Sunkavalli

Code Files :
SAGASolver.py : The solver class that accepts a SAGAProblem object and runs PSAGA on it
SAGAProblem.py : Abstract class to represent a problem in put to PSAGA
SAGATravellingSalesman.py : Problem class for TSP
SAGASudokuProblem.py : Problem class for Sudoku
SAGA_tsp_parallel.py : driver file for TSP problems
SAGA_sudoku_parallel.py : driver file for Sudoku problems
saga_utils.py : utilities file

Data Files :
XML files are the input files for TSP 
txt files are input files for Sudoku

Usage :
mpirun -n N python SAGA_tsp_parallel.py data/XYZ.xml
mpirun -n N python SAGA_tsp_parallel.py data/XYZ.txt

where N is the number of processes
