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


# @profile
def load(root, data, maxentries, minentries):
    """
    Bulk insertion of items from 'data'

    'data' is expected to be a numerical array of (N,4) dimensions,
    or an array of named objects with columns 'xmin,ymin,xmax,ymax'
    """
    # If data is empty or None, do nothing
    if data is None or len(data) == 0:
        return root

    # recursively build the tree with the given data
    # from scratch using OMT algorithm
    node = build_tree(data, 0, len(data)-1, maxentries, minentries)

    root = node

    return root


# @profile
def build_tree(data, first, last, maxentries, minentries, height=None):
    """
    Build RBush from 'data' items between 'first','last' (inclusive)
    """
    N = last - first + 1
    M = maxentries

    if N <= M:
        children = list()
        for i in range(first, last+1):
            children.append(create_item(data[i], i))
        bbox = calc_bbox_children(children)
        node = create_node(bbox, children=children, leaf=True, height=1)
        return node

    if height is None:
        # target height of the bulk-loaded tree
        height = ceil(log(N) / log(M))

        # target number of root entries to maximize storage utilization
        M = ceil(N / pow(M, height - 1))

    # split the data into M mostly square tiles
    N2 = ceil(N / M)
    N1 = N2 * ceil(sqrt(M))

    multiselect(data, first, last, N1, 0)

    children = list()
    for i in range(first, last+1, N1):
        last2 = min(i + N1 - 1, last)
        multiselect(data, i, last2, N2, 1)
        for j in range(i, last2+1, N2):
            last3 = min(j + N2 - 1, last2)
            # pack each entry recursively
            children.append(build_tree(data, first=j, last=last3,
                                       height=height - 1,
                                       maxentries=maxentries,
                                       minentries=minentries))
    bbox = calc_bbox_children(children)
    node = create_node(bbox, leaf=False, height=height, children=children)
    return node


# @profile
def multiselect(data, first, last, n, column):
    stack = [first, last]
    mid = None
    while len(stack):
        first = stack.pop(0)
        last = stack.pop(0)
        if (last - first) <= n:
            continue
        mid = first + ceil((last - first) / n / 2) * n
        quicksort(data, first, last, column)
        stack.extend([first, mid, mid, last])


# @profile
def quicksort(data, first, last, column):
    idx = np.argsort(data[first:last, column], kind='quicksort')
    idx += first
    data[first:last, :] = data[idx, :]


def calc_bbox_children(children):
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
    return (xmin, ymin, xmax, ymax)
