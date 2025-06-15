'''
Neighborhoods for solutions.
They must derive from the Neighborhood class.

@author: Vassilissa Lehoux
'''
from typing import Dict

from src.scheduling.instance.instance import Instance
from src.scheduling.solution import Solution


class Neighborhood(object):
    '''
    Base neighborhood class for solutions of a given instance.
    Do not modify!!!
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        self._instance = instance

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        raise "Not implemented error"

    def first_better_neighbor(self, sol: Solution):
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        raise "Not implemented error"


class SwapNeighborhood(Neighborhood):
    '''
    Voisinage par échange de machines entre deux opérations.
    Pour chaque paire d'opérations affectées à des machines différentes, si les deux machines peuvent exécuter les deux opérations, on échange leur affectation.
    '''

    def __init__(self, instance: Instance, params: Dict=dict()):
        '''
        Constructor
        '''
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the best solution in the neighborhood of the solution.
        Can be the solution itself.
        '''
        prev_sol = sol
        while True:
            next_sol = self.first_better_neighbor(prev_sol)
            if next_sol == prev_sol:
                return prev_sol
            prev_sol = next_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        '''
        Returns the first solution in the neighborhood of the solution
        that improves other it and the solution itself if none is better.
        '''
        ops = [op for op in sol.all_operations if op.assigned]
        for i in range(len(ops)):
            for j in range(i+1, len(ops)):
                op1, op2 = ops[i], ops[j]
                m1, m2 = op1.assigned_to, op2.assigned_to
                if m1 == m2:
                    continue
                if m2 in op1._machine_info and m1 in op2._machine_info:
                    new_sol = self._swap_operations(sol, op1, op2)
                    if new_sol and new_sol.is_feasible and new_sol.objective < sol.objective:
                        return new_sol
        return sol

    def _swap_operations(self, sol: Solution, op1, op2):
        from copy import deepcopy
        new_sol = deepcopy(sol)
        # 1. Gather execution order for each machine
        op_schedule = {}  # op_id -> (machine_id, start_time)
        for machine in new_sol.inst.machines:
            for op in machine.scheduled_operations:
                op_schedule[(op.job_id, op.operation_id)] = (machine.machine_id, op.start_time)

        # 2. Swap machine and time for op1 and op2
        key1 = (op1.job_id, op1.operation_id)
        key2 = (op2.job_id, op2.operation_id)
        m1, t1 = op_schedule[key1]
        m2, t2 = op_schedule[key2]
        op_schedule[key1] = (m2, t2)
        op_schedule[key2] = (m1, t1)

        # 3. Build the ordered list of all operations (as in constructive)
        all_ops = new_sol.all_operations
        operation_in_order_of_execution = {}
        max_nb_op = 0
        for operation in all_ops:
            pred_count = len(operation.predecessors)
            if pred_count in operation_in_order_of_execution:
                operation_in_order_of_execution[pred_count].append(operation)
            else:
                operation_in_order_of_execution[pred_count] = [operation]
            max_nb_op = max(max_nb_op, pred_count)
        list_ordered = []
        for i in range(max_nb_op+1):
            if i in operation_in_order_of_execution:
                list_ordered += operation_in_order_of_execution[i]

        # 4. Reset solution and reschedule all operations in order
        new_sol.reset()
        for op in list_ordered:
            key = (op.job_id, op.operation_id)
            if key in op_schedule:
                machine_id, start_time = op_schedule[key]
                machine = new_sol.inst.get_machine(machine_id)
                op.schedule(machine_id, start_time)
                machine.add_operation(op, start_time)
        return new_sol


class ShiftNeighborhood(Neighborhood):
    '''
    Voisinage par décalage temporel d'une opération sur sa machine.
    On tente de décaler une opération plus tôt ou plus tard si possible.
    '''
    def __init__(self, instance: Instance, params: Dict = dict()):
        super().__init__(instance, params)

    def best_neighbor(self, sol: Solution) -> Solution:
        prev_sol = sol
        while True:
            next_sol = self.first_better_neighbor(prev_sol)
            if next_sol == prev_sol:
                return prev_sol
            prev_sol = next_sol

    def first_better_neighbor(self, sol: Solution) -> Solution:
        for op in sol.all_operations:
            if not op.assigned:
                continue
            for delta in [-1, 1]:
                new_sol = self._shift_operation(sol, op, delta)
                if new_sol and new_sol.is_feasible and new_sol.objective < sol.objective:
                    return new_sol
        return sol

    def _shift_operation(self, sol: Solution, op, delta):
        from copy import deepcopy
        new_sol = deepcopy(sol)
        # 1. Gather execution order for each machine
        op_schedule = {}  # (job_id, op_id) -> (machine_id, start_time)
        for machine in new_sol.inst.machines:
            for opx in machine.scheduled_operations:
                op_schedule[(opx.job_id, opx.operation_id)] = (machine.machine_id, opx.start_time)

        # 2. Change the start time of op by delta
        key = (op.job_id, op.operation_id)
        if key in op_schedule:
            machine_id, start_time = op_schedule[key]
            new_start_time = start_time + delta
            # Ensure new_start_time is not before min_start_time
            min_start_time = op.min_start_time
            new_start_time = max(new_start_time, min_start_time)
            op_schedule[key] = (machine_id, new_start_time)

        # 3. Build the ordered list of all operations (as in constructive)
        all_ops = new_sol.all_operations
        operation_in_order_of_execution = {}
        max_nb_op = 0
        for operation in all_ops:
            pred_count = len(operation.predecessors)
            if pred_count in operation_in_order_of_execution:
                operation_in_order_of_execution[pred_count].append(operation)
            else:
                operation_in_order_of_execution[pred_count] = [operation]
            max_nb_op = max(max_nb_op, pred_count)
        list_ordered = []
        for i in range(max_nb_op+1):
            if i in operation_in_order_of_execution:
                list_ordered += operation_in_order_of_execution[i]

        # 4. Reset solution and reschedule all operations in order
        new_sol.reset()
        for opx in list_ordered:
            keyx = (opx.job_id, opx.operation_id)
            if keyx in op_schedule:
                machine_id, start_time = op_schedule[keyx]
                machine = new_sol.inst.get_machine(machine_id)
                opx.schedule(machine_id, start_time)
                machine.add_operation(opx, start_time)
        return new_sol

# Aliases for use in local search
MyNeighborhood1 = SwapNeighborhood
MyNeighborhood2 = ShiftNeighborhood
