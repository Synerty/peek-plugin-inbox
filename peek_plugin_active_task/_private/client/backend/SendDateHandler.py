from datetime import datetime

from vortex.handler.ModelHandler import ModelHandler

from peek_plugin_active_task._private.PluginNames import activeTaskFilt

sendDateFilt = {"key": "sendDate"}
sendDateFilt.update(activeTaskFilt)


class SendDateHandler(ModelHandler):
    def buildModel(self, **kwargs):
        return ["From Server : %s" % datetime.utcnow()]


def makeSendDateHandler():
    return SendDateHandler(sendDateFilt)
