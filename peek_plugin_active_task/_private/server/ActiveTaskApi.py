from datetime import datetime

from peek_plugin_active_task._private.server.MainController import \
    MainController
from peek_plugin_active_task._private.storage.Activity import Activity
from peek_plugin_active_task._private.storage.Task import Task
from peek_plugin_active_task._private.storage.TaskAction import TaskAction
from peek_plugin_active_task.server.ActiveTaskApiABC import ActiveTaskApiABC, NewTask, \
    NewActivity
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC


class ActiveTaskApi(ActiveTaskApiABC):
    def __init__(self, ormSessionCreator, userPluginApi: UserDbServerApiABC
                 , taskProc: MainController):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi
        self._taskProc = taskProc

    def shutdown(self):
        pass

    def addTask(self, task: NewTask) -> None:
        # Create the database task from the parameter
        dbTask = Task()
        for name in dbTask.tupleFieldNames():
            if getattr(task, name, None) and name is not "actions":
                setattr(dbTask, name, getattr(task, name))

        # Set the time of the message
        dbTask.dateTime = datetime.utcnow()

        dbTask.actions = []
        for action in task.actions:
            dbAction = TaskAction()
            dbAction.task = dbTask
            dbTask.actions.append(dbAction)

            for name in dbAction.tupleFieldNames():
                if getattr(action, name, None):
                    setattr(dbAction, name, getattr(action, name))

        session = self._ormSessionCreator()
        try:
            session.add(dbTask)
            for dbAction in dbTask.actions:
                session.add(dbAction)
            session.commit()
            taskId, userId = dbTask.id, dbTask.userId
        finally:
            session.close()

        self._taskProc.taskAdded(taskId, userId)

    def removeTask(self, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        tasks = session.query(Task).filter(Task.uniqueId == uniqueId).all()

        if tasks:
            task = tasks[0]
            taskId, userId = task.id, task.userId

        session.expunge_all()
        session.close()

        if not tasks:
            raise ValueError("Task does not exist" % uniqueId)

        session = self._ormSessionCreator()
        (session.query(Task)
         .filter(Task.uniqueId == uniqueId)
         .delete(synchronize_session=False))
        session.close()

        self._taskProc.taskRemoved(taskId, userId)

    def addActivity(self, activity: NewActivity) -> None:
        # Create the database task from the parameter
        dbActivity = Activity()
        for name in dbActivity.tupleFieldNames():
            if getattr(activity, name, None):
                setattr(dbActivity, name, getattr(activity, name))

        session = self._ormSessionCreator()
        try:
            session.add(dbActivity)
            session.commit()
            taskId, userId = dbActivity.id, dbActivity.userId
        finally:
            session.close()

        self._taskProc.activityAdded(taskId, userId)

    def removeActivity(self, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        activities = session.query(Activity).filter(Activity.uniqueId == uniqueId).all()

        if activities:
            activity = activities[0]
            activityId, userId = activity.id, activity.userId

        session.expunge_all()
        session.close()

        if not activities:
            raise ValueError("Activity %s does not exist" % uniqueId)

        session = self._ormSessionCreator()
        (session.query(Activity)
         .filter(Activity.uniqueId == uniqueId)
         .delete(synchronize_session=False))
        session.close()

        self._taskProc.activityRemoved(activityId, userId)
