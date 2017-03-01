from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_active_task._private.PluginNames import activeTaskFilt, \
    activeTaskObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=activeTaskObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=activeTaskFilt)

