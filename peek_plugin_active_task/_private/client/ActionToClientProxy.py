'''
import json
import logging
from copy import copy

from peek_plugin_base.PeekVortexUtil import peekServerName
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadResponse import PayloadResponse
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

from peek_plugin_active_task._private.PluginNames import \
    activeTaskActionProcessorName, activeTaskFilt

logger = logging.getLogger(__name__)


class ActionToClientProxy:
    """ Tuple Action Processor Client Proxy

    This class proxies the TupleActions onto the client frontend.

    #.  Each client frontend is given a peekClientToken when it logs.
    #.  The client tells us what it's peekClientToken is,
            we record the peekClientToken and what votexUuid it came from.
    #.  The peek-server sends us tuple actions, those messages will have the
                peekClientToken in the filt.
            We get this token, match it to out list, then relay it on to the correct
            client frontend.

    Mobile App  <--
    Web App     <-- peek_client <-- peek_server
    Mobile App  <--

    """

    def __init__(self):

        self._filt = dict(name=activeTaskActionProcessorName,
                          key="tupleActionProcessorName")
        self._filt.update(activeTaskFilt)

        self._vortexUuidsByClientToken = {}

        tokenUpdateFilt = dict(key="tokenUpdate")
        tokenUpdateFilt.update(activeTaskFilt)

        self._endpoint = PayloadEndpoint(self._filt, self._process)

        self._clientTokenUpdateEndpoint = PayloadEndpoint(
            tokenUpdateFilt, self._processClientTokenUpdate)

    def shutdown(self):
        self._endpoint.shutdown()

    def _processClientTokenUpdate(self, payload, vortexUuid, **kwargs):
        peekClientToken = payload.filt["peekClientToken"]
        self._vortexUuidsByClientToken[peekClientToken] = vortexUuid
        logger.debug("Received token update from client_fe %s" % peekClientToken)

    def _process(self, payload: Payload, vortexName: str,
                 sendResponse: SendVortexMsgResponseCallable, **kwargs):

        # Ignore responses from the client frontend
        # Only process messages from the server
        # Responses from the client are handled by PayloadResponse
        if vortexName != peekServerName:
            return

        # First off, get the peekClientToken
        peekClientToken = payload.filt["peekClientToken"]

        clientVortexUuid = self._vortexUuidsByClientToken.get(peekClientToken)

        # If we did get a clientVortexUuid, check if it's connected.
        if (clientVortexUuid
            and not clientVortexUuid in VortexFactory.getRemoteVortexUuids()):
            clientVortexUuid = None

        if not clientVortexUuid:
            msg = "Client for token %s is not connected" % peekClientToken
            logger.debug(msg)
            sendResponse(Payload(payload.filt, result=msg))
            return

        # Keep a copy of the incoming filt, in case they are using PayloadResponse
        responseFilt = copy(payload.filt)

        # Track the response, log an error if it fails
        # 7 Seconds is long enough.
        # VortexJS defaults to 10s, so we have some room for round trip time.
        pr = PayloadResponse(payload, timeout=7, resultCheck=False)

        def reply(payload):
            payload.filt = responseFilt
            sendResponse(payload.toVortexMsg())

        pr.addCallback(reply)

        pr.addCallback(lambda _: logger.debug(
            "Received action response from client_fe %s" % peekClientToken))

        pr.addErrback(lambda f: logger.error(
            "Received no response from token %s, %s\n%s",
            peekClientToken, f, payload.tuples))

        d = VortexFactory.sendVortexMsg(vortexMsgs=payload.toVortexMsg(),
                                        destVortexUuid=clientVortexUuid)
        d.addErrback(vortexLogFailure, logger)
        
'''