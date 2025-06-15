'''
Heuristics that compute an initial solution and
then improve it.

@author: Vassilissa Lehoux
'''
from typing import Dict

from src.scheduling.optim.heuristics import Heuristic
from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.constructive import NonDeterminist
from src.scheduling.optim.neighborhoods import MyNeighborhood1


class FirstNeighborLocalSearch(Heuristic):
    '''
    Vanilla local search will first create a solution,
    then at each step try and improve it by looking at
    solutions in its neighborhood.
    The first solution found that improves over the current solution
    replaces it.
    The algorithm stops when no solution is better than the current solution
    in its neighborhood.
    '''

    def __init__(self, params: Dict = dict()):
        '''
        Constructor
        '''
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass, params: Dict = dict()) -> Solution:
        '''
        Compute a solution for the given instance.
        '''
        # Initial solution
        init_heur = InitClass()
        current_solution = init_heur.run(instance)
        neighborhood = NeighborClass(instance)
        improved = True
        while improved:
            improved = False
            neighbor = neighborhood.first_better_neighbor(current_solution)
            if neighbor is not current_solution and neighbor.objective < current_solution.objective:
                current_solution = neighbor
                improved = True
        return current_solution


class BestNeighborLocalSearch(Heuristic):
    '''
    Vanilla local search will first create a solution,
    then at each step try and improve it by looking at
    solutions in its neighborhood.
    The best solution found that improves over the current solution
    replaces it.
    The algorithm stops when no solution is better than the current solution
    in its neighborhood.
    '''

    def __init__(self, params: Dict = dict()):
        '''
        Constructor
        '''
        self.params = params

    def run(self, instance: Instance, InitClass, NeighborClass=None, params: Dict = dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        '''
        from src.scheduling.optim.neighborhoods import MyNeighborhood1, MyNeighborhood2
        # Initial solution
        init_heur = InitClass()
        current_solution = init_heur.run(instance)
        neighborhoods = [MyNeighborhood1(instance), MyNeighborhood2(instance)]
        improved = True
        while improved:
            improved = False
            best_neighbor = current_solution
            for neighborhood in neighborhoods:
                neighbor = neighborhood.best_neighbor(current_solution)
                if neighbor is not current_solution and neighbor.objective < best_neighbor.objective:
                    best_neighbor = neighbor
            if best_neighbor is not current_solution:
                current_solution = best_neighbor
                improved = True
        return current_solution


if __name__ == "__main__":
    # To play with the heuristics
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    import os
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp10")
    heur = FirstNeighborLocalSearch()
    sol = heur.run(inst, NonDeterminist, MyNeighborhood1)
    plt = sol.gantt("tab20")
    plt.savefig("gantt.png")
