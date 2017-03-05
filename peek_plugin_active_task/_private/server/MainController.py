import logging

from peek_plugin_active_task._private.storage.Activity import Activity
from peek_plugin_active_task._private.storage.Task import Task
from peek_plugin_active_task._private.storage.TaskAction import TaskAction
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC
from sqlalchemy.orm.exc import NoResultFound
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.TupleAction import TupleGenericAction
from vortex.TupleSelector import TupleSelector
from vortex.VortexFactory import VortexFactory
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    PROCESS_PERIOD = 0.5

    def __init__(self, ormSessionCreator,
                 userPluginApi: UserDbServerApiABC,
                 tupleObserver: TupleDataObservableHandler):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi
        self._tupleObserver = tupleObserver

        # self._processLoopingCall = LoopingCall(self._process)

    # def start(self):
    #     d = self._processLoopingCall.start(self.PROCESS_PERIOD, now=False)
    #     d.addErrback(vortexLogFailure, logger)

    def shutdown(self):
        pass
        # self._processLoopingCall.stop()

    def _notifyObserver(self, tupleName: str, userId: str) -> None:
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(tupleName, {"userId": userId})
        )

    def taskAdded(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def taskUpdated(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def taskRemoved(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def activityRemoved(self, activityId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    def activityAdded(self, taskId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    @deferToThreadWrap
    def processTupleAction(self, tupleAction: TupleGenericAction):
        if tupleAction.key == Task.tupleName():
            self._processTaskUpdate(tupleAction)
            return

        elif tupleAction.key == TaskAction.tupleName():
            self._processTaskActionUpdate(tupleAction)
            return

        raise Exception("Unhandled tuple action key=%s" % tupleAction.key)

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

            if autoDelete & stateFlags:
                (session.query(Task)
                 .filter(Task.id == taskId)
                 .delete(synchronize_session=False))
                session.commit()

                if onDeletedPayload:
                    VortexFactory.sendVortexMsgLocally(onDeletedPayload)

            self._notifyObserver(Task.tupleName(), userId)

        except NoResultFound:
            logger.debug("Task %s has already been deleted" % taskId)

        finally:
            session.close()
