from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

from peek_plugin_active_task._private.storage import DeclarativeBase

alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
