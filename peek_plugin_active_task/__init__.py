from typing import Type

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC
from peek_plugin_active_task._private.client.PluginClientEntryHook import PluginClientEntryHook
from peek_plugin_active_task._private.server.PluginServerEntryHook import PluginServerEntryHook
from peek_plugin_active_task._private.worker.PluginWorkerEntryHook import PluginWorkerEntryHook

from peek_plugin_active_task._private.agent.PluginAgentEntryHook import PluginAgentEntryHook

__version__ = '0.0.1'


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    return PluginServerEntryHook


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    return PluginClientEntryHook


def peekWorkerEntryHook() -> Type[PluginWorkerEntryHookABC]:
    return PluginWorkerEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    return PluginAgentEntryHook
