'''
Tests for the Job class

@author: Vassilissa Lehoux
'''
import unittest

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation, OperationScheduleInfo


class TestJob(unittest.TestCase):

    def setUp(self):
        self.job = Job(job_id=42)
        self.op1 = Operation(42, 1)
        self.op2 = Operation(42, 2)
        self.op3 = Operation(42, 3)

    def test_add_and_properties(self):
        self.assertEqual(self.job.job_id, 42)
        self.assertEqual(self.job.operation_nb, 0)
        self.assertTrue(self.job.planned)
        with self.assertRaises(AttributeError):
            _ = self.job.next_operation

        self.job.add_operation(self.op1)
        self.assertEqual(self.job.operation_nb, 1)
        self.assertIs(self.job.next_operation, self.op1)
        self.assertFalse(self.job.planned)

        self.job.add_operation(self.op2)
        self.job.add_operation(self.op3)
        self.assertEqual(self.job.operation_nb, 3)
        self.assertIs(self.job.next_operation, self.op1)

    def test_schedule_and_planned(self):
        self.job.add_operation(self.op1)
        self.job.add_operation(self.op2)
        self.job.add_operation(self.op3)

        self.job.schedule_operation()
        self.assertIs(self.job.next_operation, self.op2)
        self.assertFalse(self.job.planned)

        self.job.schedule_operation()
        self.assertIs(self.job.next_operation, self.op3)
        self.assertFalse(self.job.planned)

        self.job.schedule_operation()
        with self.assertRaises(AttributeError):
            _ = self.job.next_operation
        self.assertTrue(self.job.planned)
        self.assertEqual(self.job.operation_nb, 3)

        self.job.reset()
        self.assertEqual(self.job.operation_nb, 3)
        self.assertFalse(self.job.planned)
        self.assertIs(self.job.next_operation, self.op1)

    def test_completion_time(self):
        self.assertEqual(self.job.completion_time, 0)

        self.op1._schedule_info = OperationScheduleInfo(machine_id=0, schedule_time=0, duration=5, energy_consumption=0)
        self.op2._schedule_info = OperationScheduleInfo(machine_id=1, schedule_time=5, duration=4, energy_consumption=0)
        self.op3._schedule_info = OperationScheduleInfo(machine_id=0, schedule_time=9, duration=7, energy_consumption=0)

        self.job._operations = [self.op1, self.op2, self.op3]  # noqa: W0212
        self.assertEqual(self.job.completion_time, 16)

        self.job.reset()
        self.assertEqual(self.job.completion_time, 0)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


