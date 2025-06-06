'''
Information for the instance of the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List
import os
import csv

from src.scheduling.instance.job import Job
from src.scheduling.instance.operation import Operation
from src.scheduling.instance.machine import Machine


class Instance(object):
    '''
    classdocs
    '''

    def __init__(self, instance_name):
        '''
        Constructor
        '''
        self._instance_name = instance_name
        self._machines = []
        self._jobs = []
        self._operations = []
        self._machine_dict = {}
        self._job_dict = {}
        self._operation_dict = {}

    @classmethod
    def from_file(cls, folderpath):
        inst = cls(os.path.basename(folderpath))
        # Reading the operation info
        jobs = {}
        operations = {}
        op_list = []
        with open(folderpath + os.path.sep + inst._instance_name + '_op.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            for row in csv_reader:
                job_id = int(row[0])
                op_id = int(row[1])
                machine_id = int(row[2])
                processing_time = int(row[3])
                energy = int(row[4])
                # Create job if not exists
                if job_id not in jobs:
                    jobs[job_id] = Job(job_id)
                # Create operation if not exists
                if (job_id, op_id) not in operations:
                    op = Operation(job_id, op_id)
                    operations[(job_id, op_id)] = op
                    op_list.append(op)
                    jobs[job_id].add_operation(op)
                # Add machine info to operation (no Machine instance, just data)
                operations[(job_id, op_id)]._machine_info[machine_id] = (processing_time, energy)
        inst._jobs = list(jobs.values())
        inst._job_dict = jobs
        inst._operations = op_list
        inst._operation_dict = operations

        # reading machine info
        machines = []
        machine_dict = {}
        with open(folderpath + os.path.sep + inst._instance_name + '_mach.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)
            for row in csv_reader:
                machine_id = int(row[0])
                set_up_time = int(row[1])
                set_up_energy = int(row[2])
                tear_down_time = int(row[3])
                tear_down_energy = int(row[4])
                min_consumption = int(row[5])
                end_time = int(row[6])
                machine = Machine(machine_id, set_up_time, set_up_energy, tear_down_time, tear_down_energy, min_consumption, end_time)
                machines.append(machine)
                machine_dict[machine_id] = machine
        inst._machines = machines
        inst._machine_dict = machine_dict
        return inst

    @property
    def name(self):
        return self._instance_name

    @property
    def machines(self) -> List[Machine]:
        return self._machines

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    @property
    def operations(self) -> List[Operation]:
        return self._operations

    @property
    def nb_jobs(self):
        return len(self._jobs)

    @property
    def nb_machines(self):
        return len(self._machines)

    @property
    def nb_operations(self):
        return len(self._operations)

    def __str__(self):
        return f"{self.name}_M{self.nb_machines}_J{self.nb_jobs}_O{self.nb_operations}"

    def get_machine(self, machine_id) -> Machine:
        return self._machine_dict.get(machine_id, None)

    def get_job(self, job_id) -> Job:
        return self._job_dict.get(job_id, None)

    def get_operation(self, operation_id) -> Operation:
        # operation_id can be a tuple (job_id, operation_id)
        return self._operation_dict.get(operation_id, None)
