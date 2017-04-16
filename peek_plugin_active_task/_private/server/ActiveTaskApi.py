import logging
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from peek_plugin_active_task._private.server.MainController import \
    MainController
from peek_plugin_active_task._private.storage.Activity import Activity
from peek_plugin_active_task._private.storage.Task import Task
from peek_plugin_active_task._private.storage.TaskAction import TaskAction
from peek_plugin_active_task.server.ActiveTaskApiABC import ActiveTaskApiABC, NewTask, \
    NewActivity
from peek_plugin_user.server.UserServerApiABC import UserServerApiABC

logger = logging.getLogger(__name__)


class ActiveTaskApi(ActiveTaskApiABC):
    def __init__(self, ormSessionCreator, userPluginApi: UserServerApiABC
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
            try:
                oldTask = (
                    session
                        .query(Task)
                        .filter(Task.uniqueId == task.uniqueId)
                        .one()
                )

                if task.overwriteExisting:
                    session.delete(oldTask)
                    session.commit()

                else:
                    raise Exception("Activity with uniqueId %s already exists"
                                    % task.uniqueId)

            except NoResultFound:
                pass

            session.add(dbTask)
            for dbAction in dbTask.actions:
                session.add(dbAction)
            session.commit()
            taskId, userId = dbTask.id, dbTask.userId

        finally:
            session.close()

        self._taskProc.taskAdded(taskId, userId)

    def completeTask(self, uniqueId: str) -> None:
        session = self._ormSessionCreator()
        try:
            task = session.query(Task).filter(Task.uniqueId == uniqueId).one()
            task.stateFlags = task.stateFlags | Task.STATE_COMPLETED
            taskId, userId = task.id, task.userId
            session.commit()

            self._taskProc.taskUpdated(taskId, userId)

        except NoResultFound:
            logger.debug("Task %s has been deleted" % taskId)

        finally:
            session.close()

    def removeTask(self, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        try:
            tasks = session.query(Task).filter(Task.uniqueId == uniqueId).all()

            if tasks:
                task = tasks[0]
                taskId, userId = task.id, task.userId
                session.delete(task)
                session.commit()

            else:
                raise ValueError("Task does not exist, %s " % uniqueId)

        finally:
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
            try:
                oldActivity = (
                    session
                        .query(Activity)
                        .filter(Activity.uniqueId == activity.uniqueId)
                        .one()
                )

                if activity.overwriteExisting:
                    session.delete(oldActivity)
                    session.commit()

                else:
                    raise Exception("Task with uniqueId %s already exists"
                                    % activity.uniqueId)

            except NoResultFound:
                pass

            session.add(dbActivity)
            session.commit()
            taskId, userId = dbActivity.id, dbActivity.userId

        finally:
            session.close()

        self._taskProc.activityAdded(taskId, userId)

    def removeActivity(self, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        try:
            activities = session.query(Activity).filter(
                Activity.uniqueId == uniqueId).all()

            if activities:
                activity = activities[0]
                activityId, userId = activity.id, activity.userId
                session.delete(activity)
                session.commit()

            else:
                raise ValueError("Activity %s does not exist" % uniqueId)

        finally:
            session.close()

        self._taskProc.activityRemoved(activityId, userId)
