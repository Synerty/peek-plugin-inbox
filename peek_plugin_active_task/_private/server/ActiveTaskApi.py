from peek_plugin_active_task._private.server.ActiveTaskProcessor import \
    ActiveTaskProcessor
from peek_plugin_active_task._private.storage.Task import Task
from peek_plugin_active_task._private.storage.TaskAction import TaskAction
from peek_plugin_active_task.server.ActiveTaskApiABC import ActiveTaskApiABC, NewTask
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC


class ActiveTaskApi(ActiveTaskApiABC):
    def __init__(self, ormSessionCreator, userPluginApi: UserDbServerApiABC
                 , taskProc: ActiveTaskProcessor):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi
        self._taskProc = taskProc

    def shutdown(self):
        pass

    def addTask(self, task: NewTask) -> None:
        """ Add Task

        Add a new task to the users device.
        
        :param task: The definition of the task to add.
        
        """
        # Create the database task from the parameter
        dbTask = Task()
        for name in dbTask.tupleFieldNames():
            if getattr(task, name, None):
                setattr(dbTask, name, getattr(task, name))

        dbTask.actions = []
        for action in task.actions:
            dbAction = TaskAction()
            dbAction.task = dbTask

            for name in dbAction.tupleFieldNames():
                if getattr(action, name, None):
                    setattr(dbAction, name, getattr(action, name))

        session = self._ormSessionCreator()
        try:
            session.add(dbTask)
            session.commit()
            taskId, userId = dbTask.id, dbTask.userId
        finally:
            session.close()

        self._taskProc.taskAdded(taskId, userId)

    def removeTask(self, uniqueId: str) -> None:
        """ Remove Task
        
        Remove a task from the users device.
        
        :param uniqueId: The uniqueId provided when the task was created.
        """

        session = self._ormSessionCreator()
        tasks = session.query(Task).filter(Task.uniqueId == uniqueId).all()

        if tasks:
            task = tasks[0]
            taskId, userId = task.id, task.userId

        session.expunge_all()
        session.close()

        if not tasks:
            raise ValueError("Task does not exist")

        session = self._ormSessionCreator()
        (session.query(Task)
         .filter(Task.uniqueId == uniqueId)
         .delete(synchronize_session=False))
        session.close()

        self._taskProc.taskRemoved(taskId, userId)
