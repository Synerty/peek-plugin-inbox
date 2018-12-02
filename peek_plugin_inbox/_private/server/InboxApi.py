import logging
from datetime import datetime
from typing import Optional

import pytz
from peek_plugin_inbox._private.server.controller.MainController import \
    MainController
from peek_plugin_inbox._private.storage.Activity import Activity
from peek_plugin_inbox._private.storage.Task import Task
from peek_plugin_inbox._private.storage.TaskAction import TaskAction
from peek_plugin_inbox.server.InboxApiABC import InboxApiABC, NewTask, \
    NewActivity
from peek_plugin_inbox.tuples.ActivityTuple import ActivityTuple
from peek_plugin_inbox.tuples.TaskTuple import TaskTuple
from peek_plugin_user.server.UserApiABC import UserApiABC
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class InboxApi(InboxApiABC):

    def __init__(self, ormSessionCreator, userPluginApi: UserApiABC,
                 mainController: MainController):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi
        self._mainController = mainController

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def addTask(self, task: NewTask) -> None:
        # Create the database task from the parameter
        dbTask = Task()
        for name in dbTask.tupleFieldNames():
            if getattr(task, name, None) and name is not "actions":
                setattr(dbTask, name, getattr(task, name))

        # Set the time of the message
        dbTask.dateTime = datetime.now(pytz.utc)

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
                oldTask = session.query(Task) \
                    .filter(Task.pluginName == task.pluginName) \
                    .filter(Task.uniqueId == task.uniqueId) \
                    .one()

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

        reactor.callLater(0, self._mainController.taskAdded, taskId, userId)

    @deferToThreadWrapWithLogger(logger)
    def completeTask(self, pluginName: str, uniqueId: str) -> None:
        session = self._ormSessionCreator()
        try:
            task = session.query(Task) \
                .filter(Task.pluginName == pluginName) \
                .filter(Task.uniqueId == uniqueId) \
                .one()

            task.stateFlags = task.stateFlags | Task.STATE_COMPLETED
            taskId, userId = task.id, task.userId
            session.commit()

            reactor.callLater(0, self._mainController.taskUpdated, taskId, userId)

        except NoResultFound:
            logger.debug("Task %s has been deleted" % taskId)

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def removeTask(self, pluginName: str, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        try:
            tasks = session.query(Task) \
                .filter(Task.pluginName == pluginName) \
                .filter(Task.uniqueId == uniqueId) \
                .all()

            if tasks:
                task = tasks[0]
                taskId, userId = task.id, task.userId
                session.delete(task)
                session.commit()

            else:
                raise ValueError("Task does not exist, %s " % uniqueId)

        finally:
            session.close()

        reactor.callLater(0, self._mainController.taskRemoved, taskId, userId)

    @deferToThreadWrapWithLogger(logger)
    def getTasks(self, pluginName: str, uniqueIdLike: Optional[str] = None,
                 userId: Optional[str] = None) -> Deferred:
        session = self._ormSessionCreator()
        try:
            qry = session.query(Task) \
                .filter(Task.pluginName == pluginName)

            if uniqueIdLike:
                qry = qry.filter(Task.uniqueId.ilike(uniqueIdLike))

            if userId:
                qry = qry.filter(Task.userId == userId)

            taskTuples = []
            for task in qry.all():
                taskTuple = TaskTuple()
                for fieldName in taskTuple.tupleFieldNames():
                    setattr(taskTuple, fieldName, getattr(task, fieldName))
                taskTuples.append(taskTuple)

            return taskTuples

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def addActivity(self, activity: NewActivity) -> None:
        # Create the database task from the parameter
        dbActivity = Activity()
        for name in dbActivity.tupleFieldNames():
            if getattr(activity, name, None):
                setattr(dbActivity, name, getattr(activity, name))

        session = self._ormSessionCreator()
        try:
            try:
                oldActivity = session.query(Activity) \
                    .filter(Activity.pluginName == activity.pluginName) \
                    .filter(Activity.uniqueId == activity.uniqueId) \
                    .one()

                if activity.overwriteExisting:
                    session.delete(oldActivity)
                    session.commit()

                else:
                    raise Exception("Activity with uniqueId %s already exists"
                                    % activity.uniqueId)

            except NoResultFound:
                pass

            session.add(dbActivity)
            session.commit()
            taskId, userId = dbActivity.id, dbActivity.userId

        finally:
            session.close()

        reactor.callLater(0, self._mainController.activityAdded, taskId, userId)

    @deferToThreadWrapWithLogger(logger)
    def removeActivity(self, pluginName: str, uniqueId: str) -> None:

        session = self._ormSessionCreator()
        try:
            activities = session.query(Activity) \
                .filter(Activity.pluginName == pluginName) \
                .filter(Activity.uniqueId == uniqueId) \
                .all()

            if activities:
                activity = activities[0]
                activityId, userId = activity.id, activity.userId
                session.delete(activity)
                session.commit()

            else:
                raise ValueError("Activity %s does not exist" % uniqueId)

        finally:
            session.close()

        reactor.callLater(0, self._mainController.activityRemoved, activityId, userId)

    @deferToThreadWrapWithLogger(logger)
    def getActivities(self, pluginName: str, uniqueIdLike: Optional[str] = None,
                      userId: Optional[str] = None) -> Deferred:
        session = self._ormSessionCreator()
        try:
            qry = session.query(Activity) \
                .filter(Activity.pluginName == pluginName)

            if uniqueIdLike:
                qry = qry.filter(Activity.uniqueId.ilike(uniqueIdLike))

            if userId:
                qry = qry.filter(Activity.userId == userId)

            activityTuples = []
            for activity in qry.all():
                activityTuple = ActivityTuple()
                for fieldName in activityTuple.tupleFieldNames():
                    setattr(activityTuple, fieldName, getattr(activity, fieldName))
                activityTuples.append(activityTuple)

            return activityTuples

        finally:
            session.close()
