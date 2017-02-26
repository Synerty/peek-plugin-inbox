import logging
from datetime import datetime

from twisted.internet import reactor
from txhttputil.util.DeferUtil import printFailure
from vortex.SerialiseUtil import fromStr, T_DATETIME

logger = logging.getLogger(__name__)


REPEAT = 0.5


def callWorkerSleepLoop():
    # logger.info("Sleep Only Task - Ticking along")

    from peek_plugin_active_task._private.worker.ActiveTaskWorkerTask import task1
    startTime = datetime.utcnow()

    d = task1.delay("Some task arg str")

    def cb(resultStr):
        resultDate = fromStr(resultStr, T_DATETIME)
        logger.info("Sleep Only Task started %s, returned %s",
                    resultDate - startTime,
                    datetime.utcnow() - startTime)

        reactor.callLater(REPEAT, callWorkerSleepLoop)

    d.addCallback(cb)
    d.addErrback(printFailure)
    return d


def callWorkerDbLoop():
    # logger.info("DB Update Task - Ticking along")

    from peek_plugin_active_task._private.worker.ActiveTaskWorkerTask import dbTask
    startTime = datetime.utcnow()
    d = dbTask.delay("db update task str arg")

    def cb(newId):
        logger.info("DB Update Task newId %s, returned %s",
                    newId,
                    datetime.utcnow() - startTime)
        reactor.callLater(REPEAT, callWorkerDbLoop)

    d.addCallback(cb)
    d.addErrback(printFailure)
    return d



def start():
    for _ in range(1):
        callWorkerSleepLoop()

    for _ in range(1):
        callWorkerDbLoop()