from peek_plugin_inbox.server.InboxApiABC import NewTask, InboxApiABC, \
    NewTaskAction, NewActivity
from vortex.Payload import Payload
from vortex.handler.ModelHandler import ModelHandler


_filt = {
    "plugin": "peek_plugin_inbox",
    "key": "sendTestActivity"
}

class _SendTestActivityHandler(ModelHandler):
    def __init__(self, thisPluginsApi:InboxApiABC):
        ModelHandler.__init__(self, _filt)
        self._thisPluginsApi = thisPluginsApi

    def buildModel(self, payload, **kwargs):
        formData = payload.tuples[0]

        newTask = NewActivity(**formData)
        self._thisPluginsApi.addActivity(newTask)

        return []

def createSendTestActivityHander(thisPluginsApi:InboxApiABC):
    return _SendTestActivityHandler(thisPluginsApi)