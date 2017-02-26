from sqlalchemy.orm.attributes import flag_modified

from peek.core.orm.ModelSet import ModelNode, ModelConn


def trace(startNode, depth=4, indent=0, tracedNodes=None, lastStartNode=None):
    assert isinstance(startNode, ModelNode)
    tracedNodes = tracedNodes if tracedNodes else set()

    if depth == 0:
        return ""

    formatProps = lambda n: ', '.join(["%s:'%s'" % i
                                       for i in list(n.props.items())
                                       if not i[0] in ['name', 'compareId']])

    str = '%s->[%s], id:%s, %s\n' % (('-' * 4 * indent),
                                     startNode.props.get('name', ''),
                                     startNode.id,
                                     formatProps(startNode))

    tracedNodes.add(startNode)

    for nextConn in startNode.connections:
        nextNode = nextConn.otherConnectedNode(startNode)
        if nextNode in tracedNodes:
            if nextNode != lastStartNode:
                str += "%s->id:%s (already traced)\n"
                str %= (('-' * 4 * (indent + 1)), nextNode.id)
            continue

        str += trace(nextNode,
                     depth=depth - 1,
                     indent=indent + 1,
                     tracedNodes=tracedNodes,
                     lastStartNode=startNode)

    return str


class GraphModel:
    def __init__(self):
        self.nodes = []
        self.edges = []

        self.__tracedNodes = set()

    def trace(self, startNode, depth=4, lastStartNode=None):
        assert isinstance(startNode, ModelNode), "startNode is not of type ModelNode"

        if depth == 0:
            return

        idVal = (startNode.props['alias']
                 if 'alias' in startNode.props else
                 'id:%s' % startNode.id)

        label = '%s\n[%s]\n%s' % (idVal,
                                  startNode.props['name'],
                                  startNode.type.name)

        self.__tracedNodes.add(startNode)
        self.nodes.append({'id': str(startNode.id), 'label': label})

        for nextConn in startNode.connections:
            nextNode = nextConn.otherConnectedNode(startNode)

            if depth != 1 and nextNode != lastStartNode:
                self.edges.append([str(startNode.id), str(nextNode.id)])

            if nextNode in self.__tracedNodes:
                continue

            self.trace(nextNode, depth=depth - 1, lastStartNode=startNode)

        return self.nodes, self.edges
