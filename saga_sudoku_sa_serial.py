import sys
import numpy as np
from SAGASudokuProblem import SAGASudokuProblem
from random import shuffle, random, sample, randint
from copy import deepcopy
from math import exp, sqrt
from math import sqrt


if __name__ == "__main__":

    data = None
    if len(sys.argv) == 2:
        try:
            filename = str(sys.argv[1])
            raw = np.loadtxt(filename, dtype="int")
            data = raw.reshape(1,raw.size)[0]
            n = int(sqrt(len(data)))
            n_sqrt = int(sqrt(n))
            if n != sqrt(len(data)) or n_sqrt != sqrt(n):
                print "Must pass in a NxN Sudoku where N is a perfect square"
                sys.exit(-1)
        except IOError as e:
            print "Unable to load file"
            sys.exit(-1)

    SP = SAGASudokuProblem(data)
    print "Original Puzzle:"
    SP.print_results()
    print "Original Energy:"
    print SP.get_energy()
    best_SP = deepcopy(SP)
    current_score = SP.get_energy()
    best_score = current_score
    T = 0.5
    count = 0
    
    while (count < 400000):
        try:
            if (count % 1000 == 0): 
                print "Iteration %s,    \tT = %.5f, \tbest_score = %s, \tcurrent_score = %s"%(count, T, 
                                                               best_score, current_score)
            SP_candidate = SP.generate_candidate(1)
            candidate_score = SP_candidate.get_energy()
            delta_S = float(current_score - candidate_score)
            
            if (exp((delta_S/T)) - random() > 0):
                SP = SP_candidate
                current_score = candidate_score 
        
            if (current_score < best_score):
                best_SP = deepcopy(SP)
                best_score = best_SP.get_energy()
        
            if candidate_score == 0:
                SP = SP_candidate
                break
    
            T = .99999*T
            count += 1
        except:
            print "Hit an inexplicable numerical error. It's a random algorithm-- try again."            
    if best_score == 0:
        print "\nSOLVED THE PUZZLE."
    else:
        print "\nDIDN'T SOLVE. (%s/%s points). It's a random algorithm-- try again."%(best_score,-162)
    print "\nFinal Puzzle:"
    SP.print_results()

        
