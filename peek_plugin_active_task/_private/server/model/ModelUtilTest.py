from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.trial import unittest


class ModelUtilTest(unittest.TestCase):
    def testActiveTask(self):
        self.assertTrue(True)

        d = Deferred()
        reactor.callLater(0.5, d.callback, True)
        return d

        # def testTraceHb9(self):
        #     session = getNovaOrmSession()
        #     hb9Node = session.query(ModelNode).filter(ModelNode.id == 1010114).one()
        #     print trace(hb9Node, depth=8)
