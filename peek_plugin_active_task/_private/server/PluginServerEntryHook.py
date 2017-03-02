import logging

from peek_plugin_active_task._private.server.MainController import \
    MainController
from typing import Optional

from peek_plugin_active_task._private.server.ActiveTaskApi import ActiveTaskApi
from peek_plugin_active_task._private.server.ClientTupleActionProcessor import \
    makeTupleActionProcessorHandler
from peek_plugin_active_task._private.server.ClientTupleDataObservable import \
    makeTupleDataObservableHandler
from peek_plugin_active_task._private.server.backend.SendTestActivityHandler import \
    createSendTestActivityHander
from peek_plugin_active_task._private.server.backend.SendTestTaskHandler import \
    createSendTestTaskHander
from peek_plugin_active_task._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_user.server.UserDbServerApiABC import UserDbServerApiABC

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)
        self._api = None
        self._mainController = None

        self._runningHandlers = []

    def load(self) -> None:
        loadStorageTuples()

        logger.debug("loaded")

    def start(self):
        userPluginApi = self.platform.getOtherPluginApi("peek_plugin_user")

        assert isinstance(userPluginApi,
                          UserDbServerApiABC), "Expected UserDbServerApiABC"

        # Create the observable
        tupleObserver = makeTupleDataObservableHandler(self.dbSessionCreator)
        self._runningHandlers.append(tupleObserver)

        # Create the main controller
        self._mainController = MainController(self.dbSessionCreator, userPluginApi,
                                              tupleObserver)
        self._runningHandlers.append(self._mainController)

        # Create the endpoing that listens for TupleActions
        actionProcessor = makeTupleActionProcessorHandler(self._mainController)
        self._runningHandlers.append(actionProcessor)

        # Create the API that other plugins will use
        self._api = ActiveTaskApi(self.dbSessionCreator, userPluginApi,
                                  self._mainController)
        self._runningHandlers.append(self._api)

        # Add the handlers for the Admin UI
        self._runningHandlers.append(createSendTestActivityHander(self._api))
        self._runningHandlers.append(createSendTestTaskHander(self._api))

        # self._mainController.start()

        logger.debug("started")

    def stop(self):
        while self._runningHandlers:
            self._runningHandlers.pop().shutdown()

        logger.debug("stopped")

    def unload(self):
        self._mainController = None
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
