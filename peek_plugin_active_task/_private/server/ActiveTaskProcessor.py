import logging

from twisted.internet.task import LoopingCall

from peek_plugin_active_task.server.ActiveTaskApiABC import NewTask
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC
from vortex.DeferUtil import vortexLogFailure

logger = logging.getLogger(__name__)


class ActiveTaskProcessor:
    PROCESS_PERIOD = 0.5

    def __init__(self, ormSessionCreator, userPluginApi: UserDbServerApiABC):
        self._ormSessionCreator = ormSessionCreator
        self._userPluginApi = userPluginApi

        self._processLoopingCall = LoopingCall(self._process)

    def start(self):
        d = self._processLoopingCall.start(self.PROCESS_PERIOD, now=False)
        d.addErrback(vortexLogFailure, logger)

    def shutdown(self):
        self._processLoopingCall.stop()

    def taskAdded(self, taskId: int, userId: str):
        pass

    def taskRemoved(self, taskId: int, userId: str):
        pass

    def _process(self):
        pass

    def _dispatchTask(self, task: NewTask) -> None:
        logger.debug("Talking to mobile device %s" % action.__class__)

        if not userId:
            raise Exception("userId |%s| is not valid" % userId)

        peekClientToken = yield self._userPluginApi.peekDeviceTokenForUser(userId)

        if not peekClientToken:
            raise Exception("peekClientToken |%s| for userId |%s| is not valid"
                            % (peekClientToken, userId))

        resultTuple = yield self._sendAction(action, peekClientToken)

        defer.returnValue(resultTuple)

    def _dispatchTaskToDevice(
            self):  # , tupleAction: TupleActionABC, peekClientToken: str) -> Deferred:
        filt = dict(name=actionToClientActionProcessorName,
                    key="tupleActionProcessorName",
                    peekClientToken=peekClientToken)
        filt.update(actionToClientPluginFilt)

        payload = Payload(filt=filt, tuples=[tupleAction])
        payloadResponse = PayloadResponse(payload, destVortexName=peekClientName)

        # Convert the data to TupleAction
        payloadResponse.addCallback(lambda payload_: payload_.tuples[0])
        return payloadResponse
