import numpy as np
INF = np.iinfo(np.int64).max


def create_bbox(xmin, ymin, xmax, ymax):
    return (xmin, ymin, xmax, ymax)


def create_node(bbox, leaf=None, height=None, children=None):
    return (bbox, children, leaf, height)


def create_root(children=None, height=1, leaf=True):
    if children is None:
        children = []
    bbox = np.array([INF, INF, -INF, -INF])
    return create_node(bbox, leaf=leaf, height=height, children=children)


def get(children, index):
    try:
        child = children[index]
    except:
        child = None
    return child
