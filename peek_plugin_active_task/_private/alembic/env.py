from peek_plugin_active_task._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_plugin_active_task._private.storage import DeclarativeBase

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
