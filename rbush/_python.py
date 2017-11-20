import numpy as np

INF = np.iinfo(np.int64).max


class RBushNode(object):
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.data = None
        self.leaf = None
        self.height = None
        self.children = None


def create_node(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
                data=None, leaf=None, height=None, children=None):
    node = RBushNode(xmin, ymin, xmax, ymax)
    node.data = data
    node.leaf = leaf
    node.height = height
    node.children = children
    return node


def get(children, index):
    try:
        child = children[index]
    except:
        child = None
    return child
