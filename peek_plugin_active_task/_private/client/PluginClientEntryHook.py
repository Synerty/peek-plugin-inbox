import logging

from peek_plugin_active_task._private.client.ActionToClientProxy import \
    ActionToClientProxy
from peek_plugin_active_task._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC

logger = logging.getLogger(__name__)


class PluginClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        self._runningHandlers = []

    def load(self):
        loadStorageTuples()
        logger.debug("loaded")

    def start(self):
        self._runningHandlers.append(ActionToClientProxy())
        logger.debug("started")

    def stop(self):
        while self._runningHandlers:
            self._runningHandlers.pop().shutdown()
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")
