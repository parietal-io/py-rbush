import numpy as np
from trial_python_objects import get

INF = np.iinfo(np.int64).max

MAXENTRIES = 9
MINENTRIES = int(9*0.4)


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


class RBush(object):
    def __init__(self, maxentries=None, minentries=None):
        self.maxentries = maxentries or MAXENTRIES
        self.minentries = minentries or MINENTRIES
        self._root = self.create_root()

    def create_root(self):
        return create_node(leaf=True, height=1, children=list())

    def insert(self, xmin, ymin, xmax, ymax, data=0):
        root = insert(self._root, xmin, ymin, xmax, ymax, data,
                      maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def all(self):
        return retrieve_all_items(self._root)

    def search(self, xmin, ymin, xmax, ymax):
        return search(self._root, xmin, ymin, xmax, ymax)


def search(node, xmin, ymin, xmax, ymax):
    bbox = create_node(xmin, ymin, xmax, ymax)
    return search_item(node, bbox)


def search_item(node, bbox):
    items = list()
    if node is None:
        return items
    if contains(bbox, node):
        items.extend(retrieve_all_items(node))
        return items
    if not intersects(bbox, node):
        return items
    if node.children is None:
        items.append(node)
    else:
        n_items = len(node.children)
        for i in range(n_items):
            child = get(node.children, i)
            items.extend(search_item(child, bbox))
    return items


def contains(bbox, node):
    bbox_lower_node = bbox.xmin <= node.xmin and bbox.ymin <= node.ymin
    bbox_upper_node = node.xmax <= bbox.xmax and node.ymax <= bbox.ymax
    return bbox_lower_node and bbox_upper_node


def intersects(bbox, node):
    node_lower_bbox = node.xmin <= bbox.xmax and node.ymin <= bbox.ymax
    node_upper_bbox = node.xmax >= bbox.xmin and node.ymax >= bbox.ymin
    return node_lower_bbox and node_upper_bbox


def retrieve_all_items(node):
    items = list()
    if node.children is None:
        items.append(node)
        return items
    n_items = len(node.children)
    for i in range(n_items):
        item = get(node.children, i)
        if node.leaf:
            items.append(item)
        else:
            items.extend(retrieve_all_items(item))
    return items


def insert(root, xmin, ymin, xmax, ymax, data=None,
           maxentries=MAXENTRIES, minentries=MINENTRIES):
    item = create_node(xmin, ymin, xmax, ymax, data)

    path = list()
    node = choose_subtree(root, item, path)

    node.children.append(item)
    node = extend(node, item)

    assert get(path, len(path)-1) is node
    assert get(path, 0) is root

    if len(node.children) > maxentries:
        root = balance_tree(path)
    return root


def balance_tree(path, maxentries, minentries):
    root = get(path, 0)
    for level in range(len(path)-1, -1, -1):
        node = get(path, level)
        if len(node.children) <= maxentries:
            break
        new_node = split(node, minentries)
        if level > 0:
            parent = get(path, level-1)
            parent.children.append(new_node)
        else:
            root = create_node(children=list(node, new_node),
                               leaf=False,
                               height=node.height+1)
    return root


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


def adjust_bbox(node):
    """
    Update node borders after its children
    """
    node = calc_bbox(node, 0, len(node.children), node)
    return node


def sort_splitaxis(node, minentries):
    xmargin = calc_dist_xmargin(node, minentries)
    ymargin = calc_dist_ymargin(node, minentries)
    if (xmargin < ymargin):
        sort_xmargin(node)
    return node


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


def calc_enlarged_area(a, b):
    sect1 = max(a.xmax, b.xmax) - min(a.xmin, b.xmin)
    sect2 = max(a.ymax, b.ymax) - min(a.ymin, b.ymin)
    return sect1 * sect2


def calc_bbox_area(a):
    return (a.xmax - a.xmin) * (a.ymax - a.ymin)


def calc_dist_xmargin(node, minentries):
    sort_xmargin(node)
    return calc_dist_margin(node, minentries)


def calc_dist_ymargin(node, minentries):
    sort_ymargin(node)
    return calc_dist_margin(node, minentries)


def sort_xmargin(node):
    node.children.sort(key='xmin')
    return node


def sort_ymargin(node):
    node.children.sort(key='ymin')
    return node


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


def calc_bbox_margin(bbox):
    return (bbox.xmax - bbox.xmin) + (bbox.ymax - bbox.ymin)


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


def extend(node, bbox):
    """Return 'a' box enlarged by 'b'"""
    node.xmin = min(node.xmin, bbox.xmin)
    node.ymin = min(node.ymin, bbox.ymin)
    node.xmax = max(node.xmax, bbox.xmax)
    node.ymax = max(node.ymax, bbox.ymax)
    return node


def choose_subtree(node, bbox, path):
    '''
    Return the node and add to path the tree to insert new item

    Traverse the subtree searching for the node tightest path,
    the node at the end is where closest to 'bbox' is closer or

    '''
    while True:
        path.append(node)

        if node.leaf:
            break

        min_enlargement = INF
        min_area = INF

        target_node = None
        for i in range(len(node.children)):
            child = get(node.children, i)
            area = calc_bbox_area(child)
            enlargement = calc_enlarged_area(bbox, child) - area

            # choose entry with the least area enlargement
            if (enlargement < min_enlargement):
                min_enlargement = enlargement
                if area < min_area:
                    min_area = area
                target_node = child
            else:
                if (enlargement == min_enlargement):
                    # otherwise choose one with the smallest area
                    if area < min_area:
                        min_area = area
                        target_node = child

        node = target_node or get(node.children, 0)

    return node
