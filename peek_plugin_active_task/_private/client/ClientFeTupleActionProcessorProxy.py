from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_active_task._private.PluginNames import activeTaskFilt, \
    activeTaskActionProcessorName


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
        tupleActionProcessorName=activeTaskActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=activeTaskFilt)
