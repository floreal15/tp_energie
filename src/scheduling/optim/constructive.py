'''
Constructive heuristics that returns preferably **feasible** solutions.

@author: Vassilissa Lehoux
'''
from typing import Dict
import random

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution
from src.scheduling.optim.heuristics import Heuristic


class Greedy(Heuristic):
    '''
    A deterministic greedy method to return a solution.
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        self.solution = Solution

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        self.solution = Solution(instance)
        all_operation = self.solution.all_operations
        operation_in_order_of_execution = {}
        max_nb_op = 0
        for operation in all_operation:
            if f"{len(operation._predecessors)}" in operation_in_order_of_execution:
                operation_in_order_of_execution[f"{len(operation._predecessors)}"].append(operation)
            else:
                operation_in_order_of_execution[f"{len(operation._predecessors)}"] = [operation]
            max_nb_op = max(max_nb_op, len(operation._predecessors))
        list_ordered = []
        for i in range(max_nb_op+1):
            list_ordered = list_ordered + operation_in_order_of_execution[f"{i}"]
            
        
        for operation in list_ordered:
            operation
            machine_to_schedule = None
            min_start = operation.min_start_time
            for machine in self.solution.inst.machines:
                if machine_to_schedule == None:
                    machine_to_schedule = machine
                elif machine_to_schedule.available_time > min_start and machine.available_time < machine_to_schedule.available_time:
                        machine_to_schedule = machine
                elif (machine.available_time < min_start or machine.available_time < machine_to_schedule.available_time) and operation.compare_machine_at_time(machine, machine_to_schedule, min_start):
                    machine_to_schedule = machine
            self.solution.schedule(operation,machine_to_schedule)
        for machine in self.solution.inst.machines:
            machine.stop(machine.available_time)
        return self.solution


class NonDeterminist(Heuristic):
    '''
    Heuristic that returns different values for different runs with the same parameters
    (or different values for different seeds and otherwise same parameters)
    '''

    def __init__(self, params: Dict=dict()):
        '''
        Constructor
        @param params: The parameters of your heuristic method if any as a
               dictionary. Implementation should provide default values in the function.
        '''
        self.solution = Solution

    def run(self, instance: Instance, params: Dict=dict()) -> Solution:
        '''
        Computes a solution for the given instance.
        Implementation should provide default values in the function
        (the function will be evaluated with an empty dictionary).

        @param instance: the instance to solve
        @param params: the parameters for the run
        '''
        self.solution = Solution(instance)
        all_operation = self.solution.all_operations
        operation_in_order_of_execution = {}
        max_nb_op = 0
        nb_machine=len(self.solution.inst.machines)
        for operation in all_operation:
            if f"{len(operation._predecessors)}" in operation_in_order_of_execution:
                operation_in_order_of_execution[f"{len(operation._predecessors)}"].append(operation)
            else:
                operation_in_order_of_execution[f"{len(operation._predecessors)}"] = [operation]
            max_nb_op = max(max_nb_op, len(operation._predecessors))
        is_solution = False
        nb=0
        while not is_solution:
            nb = nb+1
            for i in range(max_nb_op+1):
                for operation in operation_in_order_of_execution[f"{i}"]:
                    manchine_id = random.randint(0,nb_machine-1)
                    self.solution.schedule(operation,self.solution.inst.machines[manchine_id])
            if self.solution.is_feasible:
                is_solution = True
            else:
                self.solution.reset()
            if nb == 1000:
                return self.solution
        
        for machine in self.solution.inst.machines:
            machine.stop(machine.available_time)
        return self.solution


if __name__ == "__main__":
    # Example of playing with the heuristics
    from src.scheduling.tests.test_utils import TEST_FOLDER_DATA
    import os
    inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
    heur = NonDeterminist()
    sol = heur.run(inst)
    plt = sol.gantt("tab20")
    plt.savefig("gantt.png")
