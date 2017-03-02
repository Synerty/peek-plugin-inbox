from peek_plugin_active_task.server.ActiveTaskApiABC import NewTask, ActiveTaskApiABC, \
    NewTaskAction, NewActivity
from vortex.Payload import Payload
from vortex.handler.ModelHandler import ModelHandler


_filt = {
    "plugin": "peek_plugin_active_task",
    "key": "sendTestActivity"
}

class _SendTestActivityHandler(ModelHandler):
    def __init__(self, thisPluginsApi:ActiveTaskApiABC):
        ModelHandler.__init__(self, _filt)
        self._thisPluginsApi = thisPluginsApi

    def buildModel(self, payload, **kwargs):
        formData = payload.tuples[0]

        newTask = NewActivity(**formData)
        self._thisPluginsApi.addActivity(newTask)

        return []

def createSendTestActivityHander(thisPluginsApi:ActiveTaskApiABC):
    return _SendTestActivityHandler(thisPluginsApi)