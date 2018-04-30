import logging

from twisted.internet.defer import inlineCallbacks

from peek_plugin_inbox._private.tuples.AdminSendTestActivityActionTuple import \
    AdminSendTestActivityActionTuple
from peek_plugin_inbox._private.tuples.AdminSendTestTaskActionTuple import \
    AdminSendTestTaskActionTuple
from peek_plugin_inbox.server.InboxApiABC import NewTaskAction, InboxApiABC
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleAction import TupleGenericAction

logger = logging.getLogger(__name__)


class AdminTestController:

    def __init__(self, thisPluginsApi:InboxApiABC):
        self._thisPluginsApi = thisPluginsApi

    def start(self):
        pass

    def shutdown(self):
        pass

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleGenericAction):
        if isinstance(tupleAction,AdminSendTestActivityActionTuple):
            yield self._processAddTestActivity(tupleAction)
            return []

        elif isinstance(tupleAction,AdminSendTestTaskActionTuple):
            yield self._processAddTestTask(tupleAction)
            return []

        return None

    @inlineCallbacks
    def _processAddTestActivity(self, tupleAction: AdminSendTestActivityActionTuple):
        """ Process Add Test Activity
        
        """

        from peek_plugin_inbox.server.InboxApiABC import NewActivity
        newTask = NewActivity(**tupleAction.formData)
        yield self._thisPluginsApi.addActivity(newTask)

        return []

    @inlineCallbacks
    def _processAddTestTask(self, tupleAction: AdminSendTestTaskActionTuple):
        """ Process Add Test Task

        """

        vmsg = PayloadEnvelope().toVortexMsg()

        from peek_plugin_inbox.server.InboxApiABC import NewTask
        newTask = NewTask(**tupleAction.formData)
        newTask.overwriteExisting = True
        newTask.actions = [NewTaskAction(onActionPayloadEnvelope=vmsg, **a) for a in tupleAction.formData['actions']]
        yield self._thisPluginsApi.addTask(newTask)

        return []
