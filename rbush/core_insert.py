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
        bbox = calc_bbox_children(children)

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
    bbox = calc_bbox_children(children)
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


# @profile
def insert(root, xmin, ymin, xmax, ymax, data,
           maxentries, minentries):
    """
    Insert arrays [xmin],[ymin],[xmax],[ymax],[data]
    """
    for i in range(len(xmin)):
        item = create_item((xmin[i], ymin[i], xmax[i], ymax[i]), data[i])
        root = insert_node(root, item, maxentries, minentries)
    return root


# @profile
def insert_node(root, item, maxentries, minentries, item_height=None):
    """
    Insert node 'item' accordingly in 'root' node (tree)
    """
    if item_height is None:
        level = root[3] - 1
    else:
        level = root[3] - item_height - 1
    path = list()
    node = choose_subtree(root, item, level, path)

    node[1].append(item)
    # node = extend(node, item)  # this will be done by 'adjust_bboxes' below

    assert path[len(path)-1] is node
    assert path[0] is root

    adjusted_path = adjust_bboxes(item, path)

    if len(node[1]) > maxentries:
        root = balance_nodes(adjusted_path, maxentries, minentries)
    else:
        root = adjusted_path[0]
    return root


# @profile
def choose_subtree(node, bbox, level, path):
    '''
    Return node closets to 'bbox', fill 'path' with nodes visited
    '''
    while True:
        path.append(node)

        if node[2] or len(path)-1 == level:
            break

        min_enlargement = INF
        min_area = INF

        target_node = None
        for i in range(len(node[1])):
            child = node[1][i]
            area = calc_bbox_area(child)
            enlargement = calc_enlarged_area(bbox, child) - area

            # choose entry with the least area enlargement
            if enlargement < min_enlargement:
                min_enlargement = enlargement
                if area < min_area:
                    min_area = area
                target_node = child
            else:
                if enlargement == min_enlargement:
                    # otherwise choose one with the smallest area
                    if area < min_area:
                        min_area = area
                        target_node = child

        node = target_node or node[1][0]

    return node


# @profile
def balance_nodes(path, maxentries, minentries):
    root = path[0]
    for level in range(len(path)-1, -1, -1):
        node = path[level]
        if len(node[1]) <= maxentries:
            break
        new_node1, new_node2 = split(node, minentries)
        assert node[3] == new_node1[3]
        assert node[3] == new_node2[3]
        if level > 0:
            parent = path[level-1]
            parent[1].remove(node)
            parent[1].append(new_node1)
            parent[1].append(new_node2)
            # NOTE: 'parent' has had your borders extended when we 'insert'
        else:
            children = list()
            children.append(new_node1)
            children.append(new_node2)
            root = create_root(children=children,
                               leaf=False,
                               height=new_node1[3]+1)
            root = adjust_bbox(root)
    return root


def split(node, minentries):
    sort_splitaxis(node, minentries)
    index = choose_splitindex(node, minentries)
    if index is None:
        index = minentries

    num_children = len(node[1]) - index
    adopted = splice(node[1], index, num_children)
    bbox = calc_bbox_children(adopted)
    new_node = create_node(bbox, height=node[3],
                           leaf=node[2], children=adopted)

    # Update the sizes (limits) of each box
    node = adjust_bbox(node)

    return node, new_node


# @profile
def sort_splitaxis(node, minentries):
    xmargin = calc_dist_xmargin(node, minentries)
    ymargin = calc_dist_ymargin(node, minentries)
    if (xmargin < ymargin):
        sort_xmargin(node)
    return node


# @profile
def choose_splitindex(node, minentries):
    '''
    Return the index (children) where to split

    Split position tries to minimize (primarily) the boxes overlap
    and, secondly, the area cover by each combination of boxes.
    '''
    M = len(node[1])
    m = minentries

    minArea = INF
    minOverlap = INF

    index = None
    for i in range(m, M - m + 1):
        bbox1 = calc_bbox_children_indexes(node, 0, i)
        bbox2 = calc_bbox_children_indexes(node, i, M)

        overlap = calc_intersection_area(bbox1, bbox2)
        area = calc_bbox_area(bbox1) + calc_bbox_area(bbox2)

        # choose distribution with minimum overlap
        if (overlap < minOverlap):
            minOverlap = overlap
            index = i
            if area < minArea:
                minArea = area

        else:
            if overlap == minOverlap:
                # otherwise choose distribution with minimum area
                if area < minArea:
                    minArea = area
                    index = i

    return index


def calc_intersection_area(a, b):
    xmin = max(xminf(a), xminf(b))
    ymin = max(yminf(a), yminf(b))
    xmax = min(xmaxf(a), xmaxf(b))
    ymax = min(ymaxf(a), ymaxf(b))
    return max(0, xmax - xmin) * max(0, ymax - ymin)


def calc_bbox_area(a):
    return (xmaxf(a) - xminf(a)) * (ymaxf(a) - yminf(a))


# @profile
def calc_enlarged_area(a, b):
    return _calc_enlarged_area(xminf(a), yminf(a), xmaxf(a), ymaxf(a),
                               xminf(b), yminf(b), xmaxf(b), ymaxf(b))


# @nb.njit
def _calc_enlarged_area(axmin, aymin, axmax, aymax,
                        bxmin, bymin, bxmax, bymax):
    sectx = max(axmax, bxmax) - min(axmin, bxmin)
    secty = max(aymax, bymax) - min(aymin, bymin)
    return sectx * secty


# @profile
def extend(a, b):
    """
    Return 'a' box enlarged by 'b'
    """
    xmin, ymin, xmax, ymax = _extend(xminf(a), yminf(a), xmaxf(a), ymaxf(a),
                                     xminf(b), yminf(b), xmaxf(b), ymaxf(b))
    a = create_node([xmin, ymin, xmax, ymax],
                    leaf=a[2], height=a[3], children=a[1])
    return a


# @nb.njit
def _extend(axmin, aymin, axmax, aymax,
            bxmin, bymin, bxmax, bymax):
    xmin = min(axmin, bxmin)
    ymin = min(aymin, bymin)
    xmax = max(axmax, bxmax)
    ymax = max(aymax, bymax)
    return xmin, ymin, xmax, ymax


def calc_bbox_margin(bbox):
    return (xmaxf(bbox) - xminf(bbox)) + (ymaxf(bbox) - yminf(bbox))


# @profile
def calc_dist_xmargin(node, minentries):
    sort_xmargin(node)
    return calc_dist_margin(node, minentries)


# @profile
def calc_dist_ymargin(node, minentries):
    sort_ymargin(node)
    return calc_dist_margin(node, minentries)


def sort_xmargin(node):
    node[1].sort(key=lambda a: xminf(a))
    return node


def sort_ymargin(node):
    node[1].sort(key=lambda a: yminf(a))
    return node


# @profile
def calc_dist_margin(node, minentries):
    M = len(node[1])
    m = minentries

    bbox_left = calc_bbox_children_indexes(node, 0, m)
    bbox_right = calc_bbox_children_indexes(node, M - m, M)
    margin = calc_bbox_margin(bbox_left) + calc_bbox_margin(bbox_right)

    for i in range(m, M - m):
        child = node[1][i]
        bbox_left = extend(bbox_left, child)
        margin = margin + calc_bbox_margin(bbox_left)

    for i in range(M-m-1, m-1, -1):
        child = node[1][i]
        bbox_right = extend(bbox_right, child)
        margin = margin + calc_bbox_margin(bbox_right)

    return margin


def calc_bbox_children_indexes(children, i_ini, i_fin):
    xmin = INF
    xmax = -INF
    ymin = INF
    ymax = -INF
    for i in range(i_ini, i_fin):
        child = children[i]
        xmin = min(xmin, xminf(child))
        ymin = min(ymin, yminf(child))
        xmax = max(xmax, xmaxf(child))
        ymax = max(ymax, ymaxf(child))
    return np.array([xmin, ymin, xmax, ymax], dtype=float)


def calc_bbox_children(children):
    return calc_bbox_children_indexes(children, 0, len(children))


def adjust_bbox(node):
    """
    Update node borders after its children
    """
    bbox = calc_bbox_children(node[1])
    new_node = create_node(bbox, children=node[1],
                           leaf=node[2], height=node[3])
    return new_node


def adjust_bboxes(bbox, path):
    # adjust bboxes along the given tree path
    # for i in range(len(path)-1, -1, -1):
    #     extend(path[i], bbox)
    new_path = []
    child = None
    for i in range(len(path)-1, -1, -1):
        node = extend(path[i], bbox)
        if child is not None:
            substitute(node, path[i+1], child)
        child = node
        new_path.append(node)
    new_path.reverse()
    return new_path


def splice(items, index, num_items):
    removed_items = list()
    for i in range(num_items):
        item = items.pop(index)
        removed_items.append(item)
    return removed_items


def substitute(parent, old_child, new_child):
    parent[1].remove(old_child)
    parent[1].append(new_child)
