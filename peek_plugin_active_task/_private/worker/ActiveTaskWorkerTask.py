from datetime import datetime
from time import sleep

from celery.utils.log import get_task_logger
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_active_task._private.storage.ActiveTaskTable import ActiveTaskTable
from sqlalchemy.sql.functions import func
from txcelery.defer import CeleryClient
from vortex.SerialiseUtil import toStr

from peek_plugin_active_task._private.worker.ActiveTaskCeleryApp import celeryApp

logger = get_task_logger(__name__)


def add1(val):
    return val + 1

@CeleryClient
@celeryApp.task
def task1(inStr):
    logger.info("Received %s", inStr)
    sleep(1.0)
    return toStr(datetime.utcnow())


@CeleryClient
@celeryApp.task
def dbTask(string1):
    logger.info('Running')
    session = CeleryDbConn.getDbSession()
    session.add(ActiveTaskTable(string1=string1))
    session.commit()

    id = session.query(func.max(ActiveTaskTable.id))[0]

    return id
