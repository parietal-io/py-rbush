import numba as nb

from ._python import *


@nb.njit(["int64(int64,int64)", "float64(float64,float64)"])
def max(x, y):
    if x > y:
        return x
    return y


@nb.njit(["int64(int64,int64)", "float64(float64,float64)"])
def min(x, y):
    if x < y:
        return x
    return y


def xminf(node):
    return node[0][0]


def yminf(node):
    return node[0][1]


def xmaxf(node):
    return node[0][2]


def ymaxf(node):
    return node[0][3]


def leaff(node):
    return node[2]


def childrenf(node):
    return node[1]


def heightf(node):
    return node[-1]


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
                    leaf=leaff(a), height=heightf(a), children=childrenf(a))
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
    childrenf(node).sort(key=lambda a: xminf(a))
    return node


def sort_ymargin(node):
    childrenf(node).sort(key=lambda a: yminf(a))
    return node


# @profile
def calc_dist_margin(node, minentries):
    M = len(childrenf(node))
    m = minentries

    bbox_left = calc_bbox(node, 0, m)
    bbox_right = calc_bbox(node, M - m, M)
    margin = calc_bbox_margin(bbox_left) + calc_bbox_margin(bbox_right)

    for i in range(m, M - m):
        child = get(childrenf(node), i)
        bbox_left = extend(bbox_left, child)
        margin = margin + calc_bbox_margin(bbox_left)

    for i in range(M-m-1, m-1, -1):
        child = get(childrenf(node), i)
        bbox_right = extend(bbox_right, child)
        margin = margin + calc_bbox_margin(bbox_right)

    return margin


def calc_bbox(node, left_index, right_index, destnode=None):
    """
    Return a node enlarged by all children between left/right
    """
    if destnode is None:
        destnode = create_node([INF, INF, -INF, -INF])
    for i in range(left_index, right_index):
        child = get(childrenf(node), i)
        destnode = extend(destnode, child)
    return destnode


def calc_bbox_children_indexes(children, i_ini, i_fin):
    xmin = INF
    xmax = -INF
    ymin = INF
    ymax = -INF
    for i in range(i_ini, i_fin):
        child = get(children, i)
        xmin = min(xmin, xminf(child))
        ymin = min(ymin, yminf(child))
        xmax = max(xmax, xmaxf(child))
        ymax = max(ymax, ymaxf(child))
    return (xmin, ymin, xmax, ymax)


def calc_bbox_children(children):
    return calc_bbox_children_indexes(children, 0, len(children))


def adjust_bbox(node):
    """
    Update node borders after its children
    """
    bbox = calc_bbox_children(childrenf(node))
    new_node = create_node(bbox, children=childrenf(node),
                           leaf=leaff(node), height=heightf(node))
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


def substitute(parent, old_child, new_child):
    childrenf(parent).remove(old_child)
    childrenf(parent).append(new_child)


# @profile
def split(node, minentries):
    sort_splitaxis(node, minentries)
    index = choose_splitindex(node, minentries)
    if index is None:
        index = minentries

    num_children = len(childrenf(node)) - index
    adopted = splice(childrenf(node), index, num_children)
    bbox = calc_bbox_children(adopted)
    new_node = create_node(bbox, height=heightf(node),
                           leaf=leaff(node), children=adopted)

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
    M = len(childrenf(node))
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
    xmin = max(xminf(a), xminf(b))
    ymin = max(yminf(a), yminf(b))
    xmax = min(xmaxf(a), xmaxf(b))
    ymax = min(ymaxf(a), ymaxf(b))
    return max(0, xmax - xmin) * max(0, ymax - ymin)


def contains(bbox, node):
    """
    Return True if 'bbox' contains 'node'
    """
    bbox_lower_node = bbox[0] <= xminf(node) and bbox[1] <= yminf(node)
    bbox_upper_node = xmaxf(node) <= bbox[2] and ymaxf(node) <= bbox[3]
    return bbox_lower_node and bbox_upper_node


def intersects(bbox, node):
    node_lower_bbox = xminf(node) <= bbox[2] and yminf(node) <= bbox[3]
    node_upper_bbox = xmaxf(node) >= bbox[0] and ymaxf(node) >= bbox[1]
    return node_lower_bbox and node_upper_bbox


def calc_bbox_area(a):
    return (xmaxf(a) - xminf(a)) * (ymaxf(a) - yminf(a))
