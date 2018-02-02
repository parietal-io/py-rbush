import numpy as np
INF = np.iinfo(np.int64).max


def create_bbox(xmin, ymin, xmax, ymax):
    return (xmin, ymin, xmax, ymax)


def create_item(bbox, data):
    return (bbox, data)


def create_node(bbox, leaf=None, height=None, children=None):
    return (bbox, children, leaf, height)


def create_root(children=None, height=1, leaf=True):
    if children is None:
        children = []
    bbox = np.array([INF, INF, -INF, -INF])
    return create_node(bbox, leaf=leaf, height=height, children=children)


#import numba as nb
#@nb.jit
def xminf(node):
    return node[0][0]


#@nb.jit
def yminf(node):
    return node[0][1]


#@nb.jit
def xmaxf(node):
    return node[0][2]


#@nb.jit
def ymaxf(node):
    return node[0][3]


#@nb.jit
def dataf(node):
    return node[1]


def childrenf(node):
    return node[1]


def leaff(node):
    return node[2]


def heightf(node):
    return node[3]
