from abc import ABCMeta, abstractmethod


class ActiveTaskApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def addTask(self, uniqueId: str) -> None:
        """ Add Task

        Add a new task to the users device.
        :param uniqueId: A globally unique reference to this task.
            This reference is created by the initiating plugin.
            HINT : Ensure you prefix the uniqueId with your plugin name.
        
        """

    @property
    @abstractmethod
    def removeTask(self, uniqueId: str) -> None:
        """ Remove Task
        
        Remove a task from the users device.
        
        :param uniqueId: The uniqueId provided when the task was created.
        """
