import logging

from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_active_task._private.PluginNames import activeTaskFilt, \
    activeTaskActionProcessorName

from peek_plugin_active_task._private.server.MainController import \
    MainController

logger = logging.getLogger(__name__)


def makeTupleActionProcessorHandler(activeTaskProcessor: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=activeTaskActionProcessorName,
        additionalFilt=activeTaskFilt,
        defaultDelegate=activeTaskProcessor)
    return processor
