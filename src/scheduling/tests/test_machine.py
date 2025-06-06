'''
Tests for the Machine class

@author: Vassilissa Lehoux
'''
import unittest
from src.scheduling.instance.machine import Machine
from src.scheduling.instance.operation import Operation, OperationScheduleInfo


class TestMachine(unittest.TestCase):

    def setUp(self):
        # Create a machine with:
        # - setup_time = 2, setup_energy = 10
        # - teardown_time = 1, teardown_energy = 5
        # - min_consumption = 1 per time unit
        # - end_time = 100
        self.machine = Machine(
            machine_id=1,
            set_up_time=2,
            set_up_energy=10,
            tear_down_time=1,
            tear_down_energy=5,
            min_consumption=1,
            end_time=100
        )
        
        # Create test operations with schedule info already set
        # (assuming Operation class doesn't have add_machine_info method)
        self.op1 = Operation(job_id=1, operation_id=1)
        self.op1._schedule_info = OperationScheduleInfo(
            machine_id=1,
            schedule_time=2,  # after setup
            duration=3,
            energy_consumption=20
        )
        
        self.op2 = Operation(job_id=1, operation_id=2)
        self.op2._schedule_info = OperationScheduleInfo(
            machine_id=1,
            schedule_time=10,
            duration=5,
            energy_consumption=30
        )
        
        self.op3 = Operation(job_id=2, operation_id=1)
        self.op3._schedule_info = OperationScheduleInfo(
            machine_id=1,
            schedule_time=22,
            duration=4,
            energy_consumption=25
        )

    def tearDown(self):
        self.machine.reset()

    def test_initial_state(self):
        self.assertEqual(self.machine.machine_id, 1)
        self.assertEqual(self.machine.set_up_time, 2)
        self.assertEqual(self.machine.tear_down_time, 1)
        self.assertEqual(len(self.machine.scheduled_operations), 0)
        self.assertEqual(len(self.machine.start_times), 0)
        self.assertEqual(len(self.machine.stop_times), 0)
        self.assertEqual(self.machine.available_time, 0)
        self.assertEqual(self.machine.total_energy_consumption, 0)

    def test_add_first_operation(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        start_time = self.machine.add_operation(self.op1, 0)
        self.assertEqual(start_time, 2)  # 0 + setup_time(2)
        self.assertEqual(len(self.machine.scheduled_operations), 1)
        self.assertEqual(self.machine.scheduled_operations[0], self.op1)
        
        # Check machine state
        self.assertEqual(len(self.machine.start_times), 1)
        self.assertEqual(self.machine.start_times[0], 0)  # Started at time 0
        self.assertEqual(len(self.machine.stop_times), 0)  # Not stopped yet
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_add_operation_with_delay(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        # First operation starts immediately
        start1 = self.machine.add_operation(self.op1, 0)
        self.assertEqual(start1, 2)
        
        # Second operation requested at time 10 (after first completes at 5)
        start2 = self.machine.add_operation(self.op2, 10)
        self.assertEqual(start2, 10)  # No setup needed, machine already running
        self.assertEqual(len(self.machine.scheduled_operations), 2)
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_stop_machine(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        # Add an operation
        self.machine.add_operation(self.op1, 0)
        self.machine.stop(5)  # op1 ends at 5
        
        # Verify stop
        self.assertEqual(len(self.machine.stop_times), 1)
        self.assertEqual(self.machine.stop_times[0], 5)
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_working_time_single_operation(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        self.machine.add_operation(self.op1, 0)
        self.machine.stop(5)  # op1 ends at 5
        
        # Working time = setup_time(2) + op1 duration(3)
        self.assertEqual(self.machine.working_time, 5)
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_total_energy_consumption(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        # Add first operation with setup
        self.machine.add_operation(self.op1, 0)
        
        # Energy: setup(10) + op1(20)
        self.assertEqual(self.machine.total_energy_consumption, 30)
        
        # Stop the machine
        self.machine.stop(5)
        # Energy: previous(30) + teardown(5) + idle(95 * 1)
        self.assertEqual(self.machine.total_energy_consumption, 130)
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_multiple_operations(self):
        # Mock the operation scheduling
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: True
        
        # Schedule operations
        self.machine.add_operation(self.op1, 0)
        self.machine.stop(5)
        self.machine.add_operation(self.op2, 10)
        self.machine.stop(17)
        self.machine.add_operation(self.op3, 20)
        
        # Verify all operations are scheduled correctly
        self.assertEqual(len(self.machine.scheduled_operations), 3)
        
        # Restore original method
        Operation.schedule = original_schedule

    def test_operation_scheduling_conflict(self):
        # Create an operation that can't be scheduled
        invalid_op = Operation(job_id=3, operation_id=1)
        
        # Mock the schedule method to return False
        original_schedule = Operation.schedule
        Operation.schedule = lambda self, machine_id, at_time: False
        
        start_time = self.machine.add_operation(invalid_op, 0)
        self.assertEqual(start_time, -1)  # Indicates failure
        self.assertEqual(len(self.machine.scheduled_operations), 0)
        
        # Restore original method
        Operation.schedule = original_schedule


if __name__ == "__main__":
    unittest.main()