import logging

from twisted.internet.defer import Deferred
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.TupleAction import TupleGenericAction
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_active_task._private.storage.Activity import Activity
from peek_plugin_active_task._private.storage.Task import Task
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC

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

    def taskRemoved(self, taskId: int, userId: str):
        self._notifyObserver(Task.tupleName(), userId)

    def activityRemoved(self, activityId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    def activityAdded(self, taskId, userId):
        self._notifyObserver(Activity.tupleName(), userId)

    @deferToThreadWrap
    def processTupleAction(self, tupleAction: TupleGenericAction) -> Deferred:
        if not tupleAction.key == Task.tupleName():
            raise Exception("Unhandled tuple action key=%s" % tupleAction.key)

        taskId = tupleAction.data["id"]
        session = self._ormSessionCreator()
        try:
            task = session.query(Task).filter(Task.id == taskId).one()
            userId = task.userId

            if "state" in tupleAction.data:
                newState = tupleAction.data["state"]
                task.state = newState

            if "notificationsSentMask" in tupleAction.data:
                mask = tupleAction.data["notificationsSentMask"]
                task.notificationsSent |= mask

            session.commit()

        finally:
            session.close()

        self._notifyObserver(Task.tupleName(), userId)

