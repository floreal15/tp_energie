'''
Job. It is composed of several operations.

@author: Vassilissa Lehoux
'''
from typing import List

from src.scheduling.instance.operation import Operation


class Job(object):
    '''
    Job class.
    Contains information on the next operation to schedule for that job
    '''

    def __init__(self, job_id: int):
        self._job_id = job_id
        self._operations: List[Operation] = []
        self._next_op_idx = 0

    @property
    def job_id(self) -> int:
        return self._job_id

    def reset(self):
        for op in self._operations:
            op.reset()
        self._next_op_idx = 0

    @property
    def operations(self) -> List[Operation]:
        return self._operations.copy()

    @property
    def next_operation(self) -> Operation:
        if self.planned:
            raise AttributeError("Pas d'opération suivante")
        return self._operations[self._next_op_idx]

    def schedule_operation(self):
        if not self.planned:
            self._next_op_idx += 1

    @property
    def planned(self) -> bool:
        return self._next_op_idx >= len(self._operations)

    @property
    def operation_nb(self) -> int:
        return len(self._operations)

    def add_operation(self, operation: Operation):
        if self._operations:
            precedent = self._operations[-1]
            operation.add_predecessor(precedent)
        self._operations.append(operation)

    @property
    def completion_time(self) -> int:
        fins = [op.end_time for op in self._operations if op.assigned]
        return max(fins) if fins else 0
