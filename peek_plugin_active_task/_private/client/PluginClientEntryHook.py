import logging

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from twisted.internet import reactor

from peek_plugin_active_task._private.client.backend.SendDateHandler import makeSendDateHandler

logger = logging.getLogger(__name__)


class PluginClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        self._runningHandlers = []

    def load(self):
        logger.debug("loaded")

    def start(self):
        self._runningHandlers.append(makeSendDateHandler())

        def started():
            self._startLaterCall = None
            logger.info("started")

        self._startLaterCall = reactor.callLater(3.0, started)
        logger.info("starting")

    def stop(self):
        while self._runningHandlers:
            self._runningHandlers.pop().shutdown()

        if self._startLaterCall:
            self._startLaterCall.cancel()
        logger.info("stopped")

    def unload(self):
        logger.info("unloaded")
