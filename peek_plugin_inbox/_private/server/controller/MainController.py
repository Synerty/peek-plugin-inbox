import logging
from datetime import datetime
from typing import Optional

import pytz
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.task import LoopingCall

from peek_core_email.server.EmailApiABC import EmailApiABC
from peek_plugin_inbox._private.storage.Activity import Activity
from peek_plugin_inbox._private.storage.Task import Task
from peek_plugin_inbox._private.storage.TaskAction import TaskAction
from peek_plugin_user.server.UserApiABC import UserApiABC
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.TupleAction import TupleGenericAction
from vortex.TupleSelector import TupleSelector
from vortex.VortexFactory import VortexFactory
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    PROCESS_PERIOD = 60.0  # Every minutes

    def __init__(self, ormSessionCreator,
                 userPluginApi: UserApiABC,
                 emailApi: EmailApiABC,
                 tupleObserver: TupleDataObservableHandler):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi
        self._emailApi = emailApi
        self._tupleObserver = tupleObserver

        self._processLoopingCall = LoopingCall(self._deleteOnDateTime)

    def start(self):
        d = self._processLoopingCall.start(self.PROCESS_PERIOD, now=False)
        d.addErrback(vortexLogFailure, logger)

    def shutdown(self):
        self._processLoopingCall.stop()

    def _notifyObserver(self, tupleName: str, userId: str) -> None:
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(tupleName, {"userId": userId})
        )

    def taskAdded(self, taskId: int, userId: str):
        d = self._sendSmsNotification(taskId)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

        d = self._sendEmailNotification(taskId)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

        self._notifyObserver(Task.tupleName(), userId)

    def taskUpdated(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def taskRemoved(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def activityRemoved(self, activityId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    def activityAdded(self, taskId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleGenericAction):
        if tupleAction.key == Task.tupleName():
            yield self._processTaskUpdate(tupleAction)
            return []

        elif tupleAction.key == TaskAction.tupleName():
            yield self._processTaskActionUpdate(tupleAction)
            return []

        raise Exception("Unhandled tuple action key=%s" % tupleAction.key)

    @deferToThreadWrapWithLogger(logger)
    def _processTaskActionUpdate(self, tupleAction: TupleGenericAction):
        """ Process Task Action Update
        
        This method locally delivers the payload action that was provided when
         the task was created.
        """
        actionId = tupleAction.data["id"]
        session = self._ormSessionCreator()
        try:
            action = session.query(TaskAction).filter(TaskAction.id == actionId).one()
            # userId = action.task.userId
            VortexFactory.sendVortexMsgLocally(action.onActionPayload)

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _processTaskUpdate(self, tupleAction: TupleGenericAction):
        """ Process Task Update
        
        Process updates to the task from the UI.
        
        """
        taskId = tupleAction.data["id"]
        session = self._ormSessionCreator()
        try:
            task = session.query(Task).filter(Task.id == taskId).one()
            userId = task.userId
            wasDelivered = task.stateFlags & Task.STATE_DELIVERED
            wasCompleted = task.stateFlags & Task.STATE_COMPLETED
            wasDialogConfirmed = task.stateFlags & Task.STATE_DIALOG_CONFIRMED

            if tupleAction.data.get("stateFlags") is not None:
                newFlags = tupleAction.data["stateFlags"]
                task.stateFlags = (task.stateFlags | newFlags)

            if tupleAction.data.get("notificationSentFlags") is not None:
                mask = tupleAction.data["notificationSentFlags"]
                task.notificationSentFlags = (task.notificationSentFlags | mask)

            if task.autoComplete & task.stateFlags:
                task.stateFlags = (task.stateFlags | Task.STATE_COMPLETED)

            autoDelete = task.autoDelete
            stateFlags = task.stateFlags
            onDeletedPayload = task.onDeletedPayload

            # Commit the updates.
            session.commit()

            newDelivery = not wasDelivered and (newFlags & Task.STATE_DELIVERED)
            if newDelivery and task.onDeliveredPayload:
                VortexFactory.sendVortexMsgLocally(task.onDeliveredPayload)

            newCompleted = not wasCompleted and (newFlags & Task.STATE_COMPLETED)
            if newCompleted and task.onCompletedPayload:
                VortexFactory.sendVortexMsgLocally(task.onCompletedPayload)

            newDialogConfirmed = (newFlags & Task.STATE_DIALOG_CONFIRMED)
            newDialogConfirmed &= not wasDialogConfirmed
            if newDialogConfirmed and task.onDialogConfirmPayload:
                VortexFactory.sendVortexMsgLocally(task.onDialogConfirmPayload)

            if autoDelete & stateFlags:
                (session.query(Task)
                 .filter(Task.id == taskId)
                 .delete(synchronize_session=False))
                session.commit()

                if onDeletedPayload:
                    VortexFactory.sendVortexMsgLocally(onDeletedPayload)

            self._notifyObserver(Task.tupleName(), userId)

        except NoResultFound:
            logger.debug("_processTaskUpdate Task %s has already been deleted" % taskId)

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _deleteOnDateTime(self):
        session = self._ormSessionCreator()
        usersToNotify = set()

        try:
            delActivityQry = (
                session
                    .query(Activity)
                    .filter(Activity.autoDeleteDateTime < datetime.now(pytz.utc))
            )

            delTaskQry = (
                session
                    .query(Task)
                    .filter(Task.autoDeleteDateTime < datetime.now(pytz.utc)))

            for activity in delActivityQry:
                usersToNotify.add(activity.userId)

            for task in delTaskQry:
                usersToNotify.add(task.userId)

            delActivityQry.delete(synchronize_session=False)
            delTaskQry.delete(synchronize_session=False)

            session.commit()

        finally:
            session.close()

        for userId in usersToNotify:
            self._notifyObserver(Activity.tupleName(), userId)

    @inlineCallbacks
    def _sendSmsNotification(self, taskId: int) -> Deferred:
        task = yield self._loadTask(taskId)
        if not task:
            return

        if not (task.notificationRequiredFlags & Task.NOTIFY_BY_SMS):
            return

        user = yield self._userPluginApi.infoApi.user(task.userId)

        if not user:
            logger.debug("No user for %s" % task.userId)
            return

        if not user.mobile:
            logger.debug("User %s has no phone number" % task.userId)
            return

        desc = task.description if task.description else ""

        yield self._emailApi.sendSms(
            contents="%s\n%s" % (task.title, desc),
            mobile=user.mobile
        )

        yield self._addNotificationSentFlags(taskId, Task.NOTIFY_BY_SMS)

    @inlineCallbacks
    def _sendEmailNotification(self, taskId: int) -> Deferred:
        task = yield self._loadTask(taskId)
        if not task:
            return

        if not (task.notificationRequiredFlags & Task.NOTIFY_BY_EMAIL):
            return

        user = yield self._userPluginApi.infoApi.user(task.userId)

        if not user:
            logger.debug("No user for %s" % task.userId)
            return

        if not user.email:
            logger.debug("User %s has no email" % task.userId)
            return

        desc = task.description if task.description else ""

        yield self._emailApi.sendEmail(
            contents="%s\n%s" % (task.title, desc),
            subject=task.title,
            addresses=[user.email],
            isHtml=False
        )

        yield self._addNotificationSentFlags(taskId, Task.NOTIFY_BY_EMAIL)

    @deferToThreadWrapWithLogger(logger)
    def _loadTask(self, taskId: int) -> Optional[Task]:
        session = self._ormSessionCreator()

        try:
            task = session.query(Task).filter(Task.id == taskId).one()
            session.expunge_all()
            return task

        except NoResultFound:
            logger.debug("_processTaskUpdate Task %s has already been deleted" % taskId)
            return None

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _addNotificationSentFlags(self, taskId: int, flags: int):
        session = self._ormSessionCreator()

        try:
            task = session.query(Task).filter(Task.id == taskId).one()
            task.notificationSentFlags = task.notificationSentFlags | flags
            session.commit()

        except NoResultFound:
            logger.debug("_processTaskUpdate Task %s has already been deleted" % taskId)

        finally:
            session.close()
