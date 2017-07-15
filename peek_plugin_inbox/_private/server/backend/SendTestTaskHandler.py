from peek_plugin_inbox.server.InboxApiABC import NewTask, InboxApiABC, \
    NewTaskAction
from vortex.Payload import Payload
from vortex.handler.ModelHandler import ModelHandler


_filt = {
    "plugin": "peek_plugin_inbox",
    "key": "sendTestTask"
}

class _SendTestTaskHandler(ModelHandler):
    def __init__(self, thisPluginsApi:InboxApiABC):
        ModelHandler.__init__(self, _filt)
        self._thisPluginsApi = thisPluginsApi

    def buildModel(self, payload, **kwargs):
        formData = payload.tuples[0]

        vmsg = Payload().toVortexMsg()

        newTask = NewTask(**formData)
        newTask.overwriteExisting = True
        newTask.actions = [NewTaskAction(onActionPayload=vmsg, **a) for a in formData['actions']]
        self._thisPluginsApi.addTask(newTask)

        return []

def createSendTestTaskHander(thisPluginsApi:InboxApiABC):
    return _SendTestTaskHandler(thisPluginsApi)