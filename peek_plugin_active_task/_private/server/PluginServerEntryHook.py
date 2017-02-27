import logging

from typing import Optional

from peek_plugin_active_task._private.server.ActiveTaskApi import ActiveTaskApi
from peek_plugin_active_task._private.server.ActiveTaskProcessor import \
    ActiveTaskProcessor
from peek_plugin_active_task._private.server.backend.SendTestTaskHandler import \
    createSendTestTaskHander
from peek_plugin_active_task._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)
        self._api = None
        self._taskProc = None

        self._shutdowns = []

    def load(self) -> None:
        loadStorageTuples()

        logger.debug("loaded")

    def start(self):
        userPluginApi = self.platform.getOtherPluginApi("peek_plugin_user")
        self._taskProc = ActiveTaskProcessor(self.dbSessionCreator,userPluginApi)
        self._api = ActiveTaskApi(self.dbSessionCreator,userPluginApi, self._taskProc)

        self._shutdowns.append(self._taskProc)
        self._shutdowns.append(self._api)
        self._shutdowns.append(createSendTestTaskHander(self._api))


        logger.debug("started")

    def stop(self):
        while self._shutdowns:
            self._shutdowns.pop().shutdown()

        logger.debug("stopped")

    def unload(self):
        self._taskProc = None
        self._api = None
        logger.debug("unloaded")

    ###### Implement PluginServerStorageEntryHookABC

    @property
    def dbMetadata(self):
        from peek_plugin_active_task._private.storage import DeclarativeBase
        return DeclarativeBase.metadata

    ###### Publish our API

    @property
    def publishedServerApi(self) -> Optional[object]:
        return self._api
