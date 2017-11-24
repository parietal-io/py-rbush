from .core import *


import numba as nb


# @nb.njit
def max(x, y):
    if x > y:
        return x
    return y


# @nb.njit
def min(x, y):
    if x < y:
        return x
    return y


#@profile
def calc_enlarged_area(a, b):
    return _calc_enlarged_area(a.xmin, a.ymin, a.xmax, a.ymax,
                               b.xmin, b.ymin, b.xmax, b.ymax)

# @nb.njit
def _calc_enlarged_area(axmin, aymin, axmax, aymax,
                        bxmin, bymin, bxmax, bymax):
    sectx = max(axmax, bxmax) - min(axmin, bxmin)
    secty = max(aymax, bymax) - min(aymin, bymin)
    return sectx * secty


#@profile
def extend(a, b):
    """
    Return 'a' box enlarged by 'b'
    """
    xmin, ymin, xmax, ymax = _extend(a.xmin, a.ymin, a.xmax, a.ymax,
                                     b.xmin, b.ymin, b.xmax, b.ymax)
    a.xmin = xmin
    a.ymin = ymin
    a.xmax = xmax
    a.ymax = ymax
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
    return (bbox.xmax - bbox.xmin) + (bbox.ymax - bbox.ymin)


#@profile
def calc_dist_xmargin(node, minentries):
    sort_xmargin(node)
    return calc_dist_margin(node, minentries)


#@profile
def calc_dist_ymargin(node, minentries):
    sort_ymargin(node)
    return calc_dist_margin(node, minentries)


def sort_xmargin(node):
    node.children.sort(key=lambda a: a.xmin)
    return node


def sort_ymargin(node):
    node.children.sort(key=lambda a: a.ymin)
    return node


#@profile
def calc_dist_margin(node, minentries):
    M = len(node.children)
    m = minentries

    bbox_left = calc_bbox(node, 0, m)
    bbox_right = calc_bbox(node, M - m, M)
    margin = calc_bbox_margin(bbox_left) + calc_bbox_margin(bbox_right)

    for i in range(m, M - m):
        child = get(node.children, i)
        bbox_left = extend(bbox_left, child)
        margin = margin + calc_bbox_margin(bbox_left)

    for i in range(M-m-1, m-1, -1):
        child = get(node.children, i)
        bbox_right = extend(bbox_right, child)
        margin = margin + calc_bbox_margin(bbox_right)

    return margin


def calc_bbox(node, left_index, right_index, destnode=None):
    """
    Return a node enlarged by all children between left/right
    """
    if destnode is None:
        destnode = create_node()
    for i in range(left_index, right_index):
        child = get(node.children, i)
        destnode = extend(destnode, child)
    return destnode


def adjust_bbox(node):
    """
    Update node borders after its children
    """
    node = calc_bbox(node, 0, len(node.children), node)
    return node


def adjust_bboxes(bbox, path):
    # adjust bboxes along the given tree path
    for i in range(len(path)-1, -1, -1):
        extend(path[i], bbox)


#@profile
def split(node, minentries):
    sort_splitaxis(node, minentries)
    index = choose_splitindex(node, minentries)
    if index is None:
        index = minentries

    num_children = len(node.children) - index
    adopted = splice(node.children, index, num_children)
    new_node = create_node(height=node.height,
                           leaf=node.leaf,
                           children=adopted)

    # Update the sizes (limits) of each box
    adjust_bbox(node)
    adjust_bbox(new_node)

    return new_node


#@profile
def sort_splitaxis(node, minentries):
    xmargin = calc_dist_xmargin(node, minentries)
    ymargin = calc_dist_ymargin(node, minentries)
    if (xmargin < ymargin):
        sort_xmargin(node)
    return node


#@profile
def choose_splitindex(node, minentries):
    '''
    Return the index (children) where to split

    Split position tries to minimize (primarily) the boxes overlap
    and, secondly, the area cover by each combination of boxes.
    '''
    M = len(node.children)
    m = minentries

    minArea = INF
    minOverlap = INF

    index = None
    for i in range(m, M - m + 1):
        bbox1 = calc_bbox(node, 0, i)
        bbox2 = calc_bbox(node, i, M)

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


def splice(items, index, num_items):
    removed_items = list()
    for i in range(num_items):
        item = items.pop(index)
        removed_items.append(item)
    return removed_items


def calc_intersection_area(a, b):
    xmin = max(a.xmin, b.xmin)
    ymin = max(a.ymin, b.ymin)
    xmax = min(a.xmax, b.xmax)
    ymax = min(a.ymax, b.ymax)
    return max(0, xmax - xmin) * max(0, ymax - ymin)


def contains(bbox, node):
    """
    Return True if 'bbox' contains 'node'
    """
    bbox_lower_node = bbox.xmin <= node.xmin and bbox.ymin <= node.ymin
    bbox_upper_node = node.xmax <= bbox.xmax and node.ymax <= bbox.ymax
    return bbox_lower_node and bbox_upper_node


def intersects(bbox, node):
    node_lower_bbox = node.xmin <= bbox.xmax and node.ymin <= bbox.ymax
    node_upper_bbox = node.xmax >= bbox.xmin and node.ymax >= bbox.ymin
    return node_lower_bbox and node_upper_bbox


def calc_bbox_area(a):
    return (a.xmax - a.xmin) * (a.ymax - a.ymin)
