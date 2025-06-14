'''
Machine on which operation are executed.

@author: Vassilissa Lehoux
'''
from typing import List
from src.scheduling.instance.operation import Operation


class Machine(object):
    '''
    Machine class.
    When operations are scheduled on the machine, contains the relative information. 
    '''

    def __init__(self, machine_id: int, set_up_time: int, set_up_energy: int, tear_down_time: int,
                 tear_down_energy:int, min_consumption: int, end_time: int):
        '''
        Constructor
        Machine is stopped at the beginning of the planning and need to
        be started before executing any operation.
        @param end_time: End of the schedule on this machine: the machine must be
          shut down before that time.
        '''
        self._machine_id = machine_id
        self._set_up_time = set_up_time
        self._set_up_energy = set_up_energy
        self._tear_down_time = tear_down_time
        self._tear_down_energy = tear_down_energy
        self._min_consumption = min_consumption
        self._end_time = end_time
        
        # Scheduling state
        self._scheduled_operations = []
        self._start_times = []
        self._stop_times = []
        self._current_energy = 0

    def reset(self):
        self._scheduled_operations = []
        self._start_times = []
        self._stop_times = []
        self._current_energy = 0

    @property
    def set_up_time(self) -> int:
        return self._set_up_time

    @property
    def tear_down_time(self) -> int:
        return self._tear_down_time

    @property
    def machine_id(self) -> int:
        return self._machine_id

    @property
    def scheduled_operations(self) -> List:
        '''
        Returns the list of the scheduled operations on the machine.
        '''
        return self._scheduled_operations.copy()

    @property
    def available_time(self) -> int:
        """
        Returns the next time at which the machine is available
        after processing its last operation of after its last set up.
        """
        if not self._scheduled_operations:
            if not self._start_times:
                # Machine hasn't been started yet
                return 0
            else:
                # Machine is currently running or stopped
                return self._stop_times[-1] if self._stop_times else self._start_times[-1] + self._set_up_time
        else:
            last_op = self._scheduled_operations[-1]
            return last_op.end_time

    def add_operation(self, operation: Operation, start_time: int) -> int:
        '''
        Adds an operation on the machine, at the end of the schedule,
        as soon as possible after time start_time.
        Returns the actual start time.
        '''
        # Check if machine needs to be started
        actual_start = max(start_time, self.available_time)
        
        # If machine is not running, we need to start it
        if not self._start_times or (self._stop_times and self._stop_times[-1] > self._start_times[-1]):
            # Machine is stopped, need to start it
            machine_start_time = max(actual_start - self._set_up_time, 0)
            self._start_times.append(machine_start_time)
            self._current_energy += self._set_up_energy
            actual_start = machine_start_time + self._set_up_time
        
        # Schedule the operation
        if not operation.schedule(self.machine_id, actual_start):
            return -1  # Scheduling failed
            
        self._scheduled_operations.append(operation)
        self._current_energy += operation.energy
        
        return actual_start
  
    def stop(self, at_time):
        """
        Stops the machine at time at_time.
        """
        assert self.available_time <= at_time
        
               
        # Only stop if machine is running
        if not self._stop_times or len(self._start_times) > len(self._stop_times):
            self._stop_times.append(at_time)
            self._current_energy += self._tear_down_energy
            # Add minimal consumption between last stop and end_time if needed
            if at_time < self._end_time:
                self._current_energy += (self._end_time - at_time) * self._min_consumption
        elif len(self._stop_times) >= 1 and self._stop_times[-1] > at_time:
            self._current_energy -= (self._stop_times[-1] - at_time) * self._min_consumption
            self._stop_times[-1] = at_time

    @property
    def working_time(self) -> int:
        '''
        Total time during which the machine is running
        '''
        total = 0
        for i in range(len(self._start_times)):
            stop_time = self._stop_times[i] if i < len(self._stop_times) else self._end_time
            total += stop_time - self._start_times[i]
        return total

    @property
    def start_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is started
        in increasing order
        """
        return self._start_times.copy()

    @property
    def stop_times(self) -> List[int]:
        """
        Returns the list of the times at which the machine is stopped
        in increasing order
        """
        return self._stop_times.copy()

    @property
    def total_energy_consumption(self) -> int:
        """
        Total energy consumption of the machine during planning exectution.
        Includes:
        - Setup energy for each start
        - Teardown energy for each stop
        - Operation energy
        - Minimal consumption when idle
        """
        return self._current_energy

    def __str__(self):
        return f"M{self.machine_id}"

    def __repr__(self):
        return str(self)
