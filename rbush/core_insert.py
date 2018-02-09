# An inner-node is defined as:
#      0:    1:    2:    3:
# 0: [[xmin, ymin, xmax, ymax],
# 1:  children,
# 2:  leaf,
# 3:  height]
#
# The leaves (items) are:
#      0:    1:    2:    3:
# 0: [[xmin, ymin, xmax, ymax],
# 1:  data]
#
from .core_common import (create_node,
                          create_item,
                          xminf, xmaxf, yminf, ymaxf,
                          INF)


from math import ceil, log, pow, sqrt

import numpy as np


def calc_bbox(children):
    xmin = INF
    xmax = -INF
    ymin = INF
    ymax = -INF
    for i in range(0, len(children)):
        child = children[i]
        xmin = min(xmin, xminf(child))
        ymin = min(ymin, yminf(child))
        xmax = max(xmax, xmaxf(child))
        ymax = max(ymax, ymaxf(child))
    return np.array([xmin, ymin, xmax, ymax], dtype=float)


# @profile
def load(root, boxes, maxentries, minentries):
    """
    Bulk insertion of items from 'boxes'

    'boxes' is expected to be a numerical array of (N,4) dimensions,
    or an array of named objects with columns 'xmin,ymin,xmax,ymax'
    """
    # If boxes is empty or None, do nothing
    if boxes is None or len(boxes) == 0:
        return root

    # recursively build the tree with the given boxes
    # from scratch using OMT algorithm
    node = build_tree(boxes, 0, len(boxes)-1, maxentries, minentries)

    root = node

    return root


# @profile
def build_tree(boxes, first, last, maxentries, minentries, height=None):
    """
    Build RBush from 'boxes' items between 'first','last' (inclusive)
    """
    N = last - first + 1
    M = maxentries

    if N <= M:

        children = []
        for i in range(first, last+1):
            children.append(create_item(boxes[i], i))
        bbox = calc_bbox(children)

        return create_node(bbox, children=children, leaf=True, height=1)

    if height is None:
        # target height of the bulk-loaded tree
        height = ceil(log(N) / log(M))

        # target number of root entries to maximize storage utilization
        M = ceil(N / pow(M, height - 1))

    # split the boxes into M mostly square tiles
    N2 = ceil(N / M)
    N1 = N2 * ceil(sqrt(M))

    multiselect(boxes, first, last, N1, 0)

    children = list()
    for i in range(first, last+1, N1):
        last2 = min(i + N1 - 1, last)
        multiselect(boxes, i, last2, N2, 1)
        for j in range(i, last2+1, N2):
            last3 = min(j + N2 - 1, last2)
            # pack each entry recursively
            children.append(build_tree(boxes, first=j, last=last3,
                                       height=height - 1,
                                       maxentries=maxentries,
                                       minentries=minentries))
    bbox = calc_bbox(children)
    node = create_node(bbox, leaf=False, height=height, children=children)
    return node


# @profile
def multiselect(boxes, first, last, n, column):
    stack = [first, last]
    mid = None
    while len(stack):
        first = stack.pop(0)
        last = stack.pop(0)
        if (last - first) <= n:
            continue
        mid = first + ceil((last - first) / n / 2) * n
        quicksort(boxes, first, last, column)
        stack.extend([first, mid, mid, last])


# @profile
def quicksort(boxes, first, last, column):
    idx = np.argsort(boxes[first:last, column], kind='quicksort')
    idx += first
    boxes[first:last, :] = boxes[idx, :]
