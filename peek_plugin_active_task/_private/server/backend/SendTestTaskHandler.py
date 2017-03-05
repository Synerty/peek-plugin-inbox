from peek_plugin_active_task.server.ActiveTaskApiABC import NewTask, ActiveTaskApiABC, \
    NewTaskAction
from vortex.Payload import Payload
from vortex.handler.ModelHandler import ModelHandler


_filt = {
    "plugin": "peek_plugin_active_task",
    "key": "sendTestTask"
}

class _SendTestTaskHandler(ModelHandler):
    def __init__(self, thisPluginsApi:ActiveTaskApiABC):
        ModelHandler.__init__(self, _filt)
        self._thisPluginsApi = thisPluginsApi

    def buildModel(self, payload, **kwargs):
        formData = payload.tuples[0]

        vmsg = Payload().toVortexMsg()

        newTask = NewTask(**formData)
        newTask.actions = [NewTaskAction(onActionPayload=vmsg, **a) for a in formData['actions']]
        self._thisPluginsApi.addTask(newTask)

        return []

def createSendTestTaskHander(thisPluginsApi:ActiveTaskApiABC):
    return _SendTestTaskHandler(thisPluginsApi)