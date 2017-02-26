import logging

from peek_plugin_active_task._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC):
    def load(self) -> None:
        loadStorageTuples()
        logger.debug("loaded")

    def start(self):
        logger.debug("started")

    def stop(self):
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    ###### Implement PluginServerStorageEntryHookABC

    @property
    def dbMetadata(self):
        from peek_plugin_active_task._private.storage import DeclarativeBase
        return DeclarativeBase.metadata
