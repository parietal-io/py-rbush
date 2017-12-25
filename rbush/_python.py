import numpy as np
INF = np.iinfo(np.int64).max


def create_root():
    children = list()
    bbox = np.array([INF, INF, -INF, -INF])
    return create_node(bbox, leaf=True, height=1, children=children)


def get(children, index):
    try:
        child = children[index]
    except:
        child = None
    return child


# from collections import namedtuple
# RBushNode = namedtuple('RBushNode', ['bbox', 'leaf', 'height', 'children'])

def create_bbox(xmin, ymin, xmax, ymax):
    return (xmin, ymin, xmax, ymax)

def create_node(bbox, leaf=None, height=None, children=None):
    return (bbox, children, leaf, height)


# from collections import namedtuple
# RBushNode = namedtuple('RBushNode',
#                        ['xmin', 'ymin', 'xmax', 'ymax',
#                         'data', 'leaf', 'height', 'children'])

#@profile
# def create_node(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
#                 data=None, leaf=None, height=None, children=None):
#     node = RBushNode(xmin, ymin, xmax, ymax, data, leaf, height, children)
#     return node


# @profile
# def create_node(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
#                 data=None, leaf=None, height=None, children=None):
#     node = RBushNode(xmin, ymin, xmax, ymax)
#     node.data = data
#     node.leaf = leaf
#     node.height = height
#     node.children = children
#     return node
#
#
# class RBushNode(object):
#     def __init__(self, xmin, ymin, xmax, ymax):
#         self.xmin = xmin
#         self.ymin = ymin
#         self.xmax = xmax
#         self.ymax = ymax
#         self.data = None
#         self.leaf = None
#         self.height = None
#         self.children = None
