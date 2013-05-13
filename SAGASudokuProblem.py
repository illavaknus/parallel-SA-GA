import sys
import numpy as np
from SAGAProblem import SAGAProblem
from random import shuffle, random, sample, randint
from copy import deepcopy
from math import exp
from math import sqrt

"""
Sudoku Problem to be used by SAGASolver
Can solve variable sized Sudoku boards
Some of the logic used was referenced from the following site:
https://github.com/erichowens/SudokuSolver
"""
class SAGASudokuProblem(SAGAProblem):

    def __init__(self, data=None, _given_indices=None):
        """
        Initialize the Sudoku with optional data and given indices
        parameters. If the given indices aren't passed, all values
        greater than zero will be considered the given values of
        the Sudoku
        @pre data must be NxN array where N is a perfect square
        """
        #Set the data array if it isn't defined
        if data is None:
            self._data = np.array([5,3,0,0,7,0,0,0,0,
                                  6,0,0,1,9,5,0,0,0,
                                  0,9,8,0,0,0,0,6,0,
                                  8,0,0,0,6,0,0,0,3,
                                  4,0,0,8,0,3,0,0,1,
                                  7,0,0,0,2,0,0,0,6,
                                  0,6,0,0,0,0,2,8,0,
                                  0,0,0,4,1,9,0,0,5,
                                  0,0,0,0,8,0,0,7,9])
        else:
            self._data = data
        
        #Set the value for N
        self._N = int(sqrt(len(self._data)))
        
        #Set the given entries if they are defined
        if _given_indices is None:
            self._given_indices = np.arange(self._N**2)[self._data > 0]
        else:
            self._given_indices = _given_indices
        
        #Fill the board with random initial values
        for num in range(self._N):
            sg_indices = self._get_subgrid_indices(num)
            sg = self._data[sg_indices]
            open_indices = [ind for i,ind in enumerate(sg_indices) if sg[i] == 0]
            missing_values = [i for i in range(1,self._N+1) if i not in sg]
            shuffle(missing_values)
            for ind, value in zip(open_indices, missing_values):
                self._data[ind] = value
    

    def get_energy(self):
        """
        Calculates the energy by counting the number of duplicate
        entries in each row, column, and subgrid
        """
        energy = 0
        for i in range(self._N):
            energy += self._N - len(set(self._data[self._get_subgrid_indices(i)]))
            energy += self._N - len(set(self._data[self._get_row_indices(i)]))
            energy += self._N - len(set(self._data[self._get_col_indices(i)]))
        return energy

    def criteria_fulfilled(self, iteration, energy):
        """
        Returns true iff the energy is 0, which means
        the Sudoku has been solved
        """
        return energy == 0

    def generate_candidate(self, L):
        """
        Creates a new candidate Sudoku board by swapping
        up to L non-given entries in a random subgrids
        """
        new_data = deepcopy(self._data)
        for swaps in range(L):
            sg = randint(0,self._N-1)
            sg_indices = self._get_subgrid_indices(sg)
            sg_indices = filter(lambda x:x not in self._given_indices, sg_indices)
            index1, index2 = sample(sg_indices, 2)
            new_data[index1], new_data[index2] = new_data[index2], new_data[index1]
        return SAGASudokuProblem(new_data, self._given_indices)

    def print_results(self):
        """
        Print out the contents of the Sudoku
        """
        result = ""
        N_sqrt = sqrt(self._N)
        for i in range(self._N**2):
            if i % self._N == 0 and i != 0:
                result += "\n"
            if i % (self._N * N_sqrt) == 0 and i != 0:
                result += "\n" 
            if i % N_sqrt == 0:
                result += " "
            result += str(self._data[i])
        print result

    def _get_subgrid_indices(self, i):
        """
        Get the indices of the i'th subgrid. Subgrids are
        numbered in a row increasing manner
        """
        N_sqrt = int(sqrt(self._N))
        r_start = (i // N_sqrt) * N_sqrt
        c_start = (i % N_sqrt) * N_sqrt
        return np.array([self._N * (r_start+(j//N_sqrt)) + (c_start+(j%N_sqrt)) for j in range(self._N)])
        
    def _get_col_indices(self, j):
        """
        Get the indices of the j'th column
        """
        return np.arange(j, self._N * (self._N-1) + j + 1, self._N)
        
    def _get_row_indices(self, i):
        """
        Get the indices of the i'th row
        """
        return np.arange(self._N * i, self._N * i + self._N)
        