'''
Test of the Solution class.

@author: Vassilissa Lehoux
'''
import unittest
import os

from src.scheduling.instance.instance import Instance
from src.scheduling.optim.constructive import Greedy, NonDeterminist
from src.scheduling.solution import Solution
from src.scheduling.tests.test_utils import TEST_FOLDER_DATA, TEST_FOLDER
from src.scheduling.optim.neighborhoods import SwapNeighborhood, ShiftNeighborhood


class TestSolution(unittest.TestCase):

    def setUp(self):
        self.inst1 = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")

    def tearDown(self):
        pass

    def test_init_sol(self):
        sol = Solution(self.inst1)
        self.assertEqual(len(sol.all_operations), len(self.inst1.operations),
                         'Nb of operations should be the same between instance and solution')
        self.assertEqual(len(sol.available_operations), len(self.inst1.jobs),
                         'One operation per job should be available for scheduling')

    def test_schedule_op(self):
        sol = Solution(self.inst1)
        operation = self.inst1.operations[0]
        machine = self.inst1.machines[1]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 12, 'wrong operation duration')
        self.assertEqual(operation.energy, 12, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 20, 'wrong set up time for machine')
        self.assertEqual(operation.end_time, 32, 'wrong operation end time')
        self.assertEqual(machine.available_time, 32, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[2]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 1, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 9, 'wrong operation duration')
        self.assertEqual(operation.energy, 10, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 41, 'wrong operation end time')
        self.assertEqual(machine.available_time, 41, 'wrong available time')
        self.assertEqual(machine.working_time, 120, 'wrong working time for machine')
        operation = self.inst1.operations[1]
        machine = self.inst1.machines[0]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 5, 'wrong operation duration')
        self.assertEqual(operation.energy, 6, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 32, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 37, 'wrong operation end time')
        self.assertEqual(machine.available_time, 37, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        operation = self.inst1.operations[3]
        sol.schedule(operation, machine)
        self.assertEqual(operation.assigned, True, 'operation should be assigned')
        self.assertEqual(operation.assigned_to, 0, 'wrong machine machine')
        self.assertEqual(operation.processing_time, 10, 'wrong operation duration')
        self.assertEqual(operation.energy, 9, 'wrong operation energy cost')
        self.assertEqual(operation.start_time, 41, 'wrong start time for operation')
        self.assertEqual(operation.end_time, 51, 'wrong operation end time')
        self.assertEqual(machine.available_time, 51, 'wrong available time')
        self.assertEqual(machine.working_time, 83, 'wrong working time for machine')
        self.assertEqual(machine.start_times[0], 17)
        self.assertEqual(machine.stop_times[0], 100)
        self.assertTrue(sol.is_feasible, 'Solution should be feasible')
        plt = sol.gantt('tab20')
        plt.savefig(TEST_FOLDER + os.path.sep +  'temp.png')

    def test_objective(self):
        sol = Solution(self.inst1)
        # Before any scheduling, objective should be zero or raise because not feasible
        with self.assertRaises(Exception):
            _ = sol.objective

        # Schedule all operations greedily
        while sol.available_operations:
            op = sol.available_operations[0]
            # find a compatible machine
            for m in self.inst1.machines:
                if m.machine_id in op._machine_info:
                    sol.schedule(op, m)
                    break

        # Now that all operations are scheduled, objective should be an integer > 0
        obj = sol.objective
        self.assertIsInstance(obj, int, "Objective should be integer")
        self.assertGreater(obj, 0, "Objective should be positive after full schedule")

    def test_evaluate(self):
        sol = Solution(self.inst1)
        # Evaluate should mirror objective once feasible
        # Schedule all operations
        while sol.available_operations:
            op = sol.available_operations[0]
            for m in self.inst1.machines:
                if m.machine_id in op._machine_info:
                    sol.schedule(op, m)
                    break

        val_eval = sol.evaluate
        val_obj = sol.objective
        self.assertEqual(val_eval, val_obj, "evaluate and objective must match")
        self.assertIsInstance(val_eval, int, "evaluate should return an integer")

    def test_optim_greed(self):
        inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "../../../../data/jsp5")
        heur = Greedy()
        sol = heur.run(inst)
        plt = sol.gantt("tab20")
        plt.savefig("gantt.png")
        self.assertTrue(sol.is_feasible,"sould be feasible")


    def test_optim_non_det(self):
        inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "../../../../data/jsp5")
        heur = NonDeterminist()
        sol = heur.run(inst)
        plt = sol.gantt("tab20")
        plt.savefig("gantt.png")
        self.assertTrue(sol.is_feasible,"sould be feasible")


class TestNeighborhoods(unittest.TestCase):
    def setUp(self):
        self.inst = Instance.from_file(TEST_FOLDER_DATA + os.path.sep + "jsp1")
        self.heur = NonDeterminist()
        self.sol = self.heur.run(self.inst)

    def test_swap_neighborhood(self):
        neigh = SwapNeighborhood(self.inst)
        neighbor_sol = neigh.best_neighbor(self.sol)
        self.assertTrue(neighbor_sol.is_feasible, "SwapNeighborhood: neighbor should be feasible")
        # Le voisin doit être au moins aussi bon ou meilleur
        self.assertLessEqual(neighbor_sol.objective, self.sol.objective, "SwapNeighborhood: neighbor should not be worse than original")

    def test_shift_neighborhood(self):
        neigh = ShiftNeighborhood(self.inst)
        neighbor_sol = neigh.best_neighbor(self.sol)
        self.assertTrue(neighbor_sol.is_feasible, "ShiftNeighborhood: neighbor should be feasible")
        self.assertLessEqual(neighbor_sol.objective, self.sol.objective, "ShiftNeighborhood: neighbor should not be worse than original")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
