'''
Object containing the solution to the optimization problem.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.instance import Instance
from src.scheduling.instance.operation import Operation

from src.scheduling.instance.machine import Machine
from matplotlib import pyplot as plt
from matplotlib import colormaps

class Solution(object):
    def __init__(self, instance: Instance):
        self._instance = instance
        for op in self._instance.operations:
            op.reset()
        for m in self._instance.machines:
            m.reset()

    @property
    def inst(self) -> Instance:
        return self._instance

    def reset(self):
        for op in self._instance.operations:
            op.reset()
        for m in self._instance.machines:
            m.reset()

    @property
    def is_feasible(self) -> bool:
        return all(op.assigned for op in self._instance.operations)

    @property
    def evaluate(self) -> int:
        if not self.is_feasible:
            raise Exception("Solution is not feasible")
        return self.objective

    @property
    def objective(self) -> int:
        if not self.is_feasible:
            raise Exception("Solution is not feasible")
        total = 0
        for job in self._instance.jobs:
            total += job.completion_time
        return total

    @property
    def cmax(self) -> int:
        if not self.is_feasible:
            raise Exception("Solution is not feasible")
        return max(job.completion_time for job in self._instance.jobs)

    @property
    def sum_ci(self) -> int:
        return self.objective

    @property
    def total_energy_consumption(self) -> int:
        if not self.is_feasible:
            raise Exception("Solution is not feasible")
        return sum(m.total_energy_consumption for m in self._instance.machines)

    def __str__(self) -> str:
        return ""

    def to_csv(self):
        raise NotImplementedError

    def from_csv(self, inst_folder, operation_file, machine_file):
        raise NotImplementedError

    @property
    def available_operations(self) -> List[Operation]:
        avail = []
        for op in self._instance.operations:
            if not op.assigned:
                ready = True
                for pred in op.predecessors:
                    if not pred.assigned:
                        ready = False
                        break
                if ready:
                    avail.append(op)
        return avail

    @property
    def all_operations(self) -> List[Operation]:
        return self._instance.operations.copy()

    def schedule(self, operation: Operation, machine: Machine):
        assert operation in self.available_operations
        earliest = operation.min_start_time

        if not machine.start_times:
            machine.add_operation(operation, earliest)
            machine._stop_times.append(machine._end_time)
            machine._current_energy += machine._tear_down_energy
            return

        if machine.stop_times and machine.stop_times[-1] > machine.available_time:
            machine._stop_times.pop()

        machine.add_operation(operation, max(earliest, machine.available_time))
        machine._stop_times.append(machine._end_time)
        machine._current_energy += machine._tear_down_energy


    def gantt(self, colormapname):
        """
        Generate a plot of the planning.
        Standard colormaps can be found at https://matplotlib.org/stable/users/explain/colors/colormaps.html
        """
        fig, ax = plt.subplots()
        colormap = colormaps[colormapname]
        for machine in self.inst.machines:
            machine_operations = sorted(machine.scheduled_operations, key=lambda op: op.start_time)
            for operation in machine_operations:
                operation_start = operation.start_time
                operation_end = operation.end_time
                operation_duration = operation_end - operation_start
                operation_label = f"O{operation.operation_id}_J{operation.job_id}"

                # Set color based on job ID
                color_index = operation.job_id + 2
                if color_index >= colormap.N:
                    color_index = color_index % colormap.N
                color = colormap(color_index)

                ax.broken_barh(
                    [(operation_start, operation_duration)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=color,
                    edgecolor='black'
                )

                middle_of_operation = operation_start + operation_duration / 2
                ax.text(
                    middle_of_operation,
                    machine.machine_id,
                    operation_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
            set_up_time = machine.set_up_time
            tear_down_time = machine.tear_down_time
            for (start, stop) in zip(machine.start_times, machine.stop_times):
                start_label = "set up"
                stop_label = "tear down"
                ax.broken_barh(
                    [(start, set_up_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(0),
                    edgecolor='black'
                )
                ax.broken_barh(
                    [(stop, tear_down_time)],
                    (machine.machine_id - 0.4, 0.8),
                    facecolors=colormap(1),
                    edgecolor='black'
                )
                ax.text(
                    start + set_up_time / 2.0,
                    machine.machine_id,
                    start_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )
                ax.text(
                    stop + tear_down_time / 2.0,
                    machine.machine_id,
                    stop_label,
                    rotation=90,
                    ha='center',
                    va='center',
                    fontsize=8
                )

        fig = ax.figure
        fig.set_size_inches(12, 6)

        ax.set_yticks(range(self._instance.nb_machines))
        ax.set_yticklabels([f'M{machine_id+1}' for machine_id in range(self.inst.nb_machines)])
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_title('Gantt Chart')
        ax.grid(True)

        return plt
