from .node import *
from copy import copy
import math

import numpy as np


def remove(root, xmin, ymin, xmax, ymax):
    bbox = (xmin, ymin, xmax, ymax)
    return remove_item(root, bbox, lambda bbox,node:bbox[0]==xminf(node))


def remove_item(node, bbox, is_equal):
    items = []
    if not intersects(bbox, node):
        return items
    if leaff(node) is True:
        indexes = []
        for i in range(len(childrenf(node))):
            child = get(childrenf(node), i)
            if is_equal(bbox, child):
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            items.append(childrenf(node).pop(i))
        if len(items) > 0:
            adjust_bbox(node)
    else:
        indexes = []
        for i in range(len(childrenf(node))):
            child = get(childrenf(node), i)
            items.extend(remove_item(child, bbox, is_equal))
            if len(childrenf(child)) == 0:
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            empty = childrenf(node).pop(i)
        if len(items) > 0:
            adjust_bbox(node)
    return items


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
        level = heightf(root) - 1
    else:
        level = heightf(root) - item_height - 1
    path = list()
    node = choose_subtree(root, item, level, path)

    childrenf(node).append(item)
    # node = extend(node, item)  # this will be done by 'adjust_bboxes' below

    assert get(path, len(path)-1) is node
    assert get(path, 0) is root

    adjusted_path = adjust_bboxes(item, path)

    if len(childrenf(node)) > maxentries:
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

        if leaff(node) or len(path)-1 == level:
            break

        min_enlargement = INF
        min_area = INF

        target_node = None
        for i in range(len(childrenf(node))):
            child = get(childrenf(node), i)
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

        node = target_node or get(childrenf(node), 0)

    return node


# @profile
def balance_nodes(path, maxentries, minentries):
    root = get(path, 0)
    for level in range(len(path)-1, -1, -1):
        node = get(path, level)
        if len(childrenf(node)) <= maxentries:
            break
        new_node1, new_node2 = split(node, minentries)
        assert heightf(node) == heightf(new_node1)
        assert heightf(node) == heightf(new_node2)
        if level > 0:
            parent = get(path, level-1)
            childrenf(parent).remove(node)
            childrenf(parent).append(new_node1)
            childrenf(parent).append(new_node2)
            # NOTE: 'parent' has had your borders extended when we 'insert'
        else:
            children = list()
            children.append(new_node1)
            children.append(new_node2)
            root = create_root(children=children,
                               leaf=False,
                               height=heightf(new_node1)+1)
            root = adjust_bbox(root)
    return root


# @profile
def search(node, xmin, ymin, xmax, ymax):
    bbox = create_bbox(xmin, ymin, xmax, ymax)
    nodes = search_node(node, bbox)
    # return np.asarray([[n.xmin, n.ymin, n.xmax, n.ymax] for n in nodes])
    return nodes

# @profile
def search_node(node, bbox):
    items = list()
    if node is None:
        return items
    if not intersects(bbox, node):
        return items
    if contains(bbox, node):
        items.extend(retrieve_all_items(node))
        return items
    if childrenf(node) is None:
        items.append(node)
    else:
        n_items = len(childrenf(node))
        for i in range(n_items):
            child = get(childrenf(node), i)
            items.extend(search_node(child, bbox))
    return items


# @profile
def retrieve_all_items(node):
    items = list()
    if childrenf(node) is None:
        items.append(node)
        return items
    n_items = len(childrenf(node))
    for i in range(n_items):
        item = get(childrenf(node), i)
        if leaff(node):
            items.append(item)
        else:
            items.extend(retrieve_all_items(item))
    return items


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

    # If data is small ( < minimum entries), just insert one-by-one
    if len(data) < minentries:
        if data.shape[1] == 5:
            xmin, ymin, xmax, ymax, data = data.T
        else:
            xmin, ymin, xmax, ymax = data.T
            data = [None]*len(xmin)
        return insert(root, xmin, ymin, xmax, ymax, data,
                      maxentries=maxentries, minentries=minentries)

    # recursively build the tree with the given data
    # from scratch using OMT algorithm
    node = build_tree(data, 0, len(data)-1, maxentries, minentries)

    if not len(childrenf(root)):
        # save as is if tree is empty
        root = node
    elif (heightf(root) == heightf(node)):
        # split root if trees have the same height
        children = list()
        children.append(root)
        children.append(node)
        bbox = calc_bbox_children(children)
        root = create_node(bbox, children=children, leaf=False, height=heightf(node)+1)
    else:
        if heightf(root) < heightf(node):
            # swap trees if inserted one is bigger
            tmpNode = root
            root = node
            node = tmpNode
        # insert the small tree into the large tree at appropriate level
        level = heightf(root) - heightf(node) - 1
        root = insert_node(root, node, level, True)
    return root


def create_item(bbox, data=None):
    return (bbox, data)


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
            children.append(create_item(data[i]))
            # _node = create_node(data[i][0], data[i][1], data[i][2], data[i][3])
            # children.append(_node)
        bbox = calc_bbox_children(children)
        node = create_node(bbox, children=children, leaf=True, height=1)
        return node

    if height is None:
        # target height of the bulk-loaded tree
        height = math.ceil(math.log(N) / math.log(M))

        # target number of root entries to maximize storage utilization
        M = math.ceil(N / math.pow(M, height - 1))

    # split the data into M mostly square tiles
    N2 = math.ceil(N / M)
    N1 = N2 * math.ceil(math.sqrt(M))

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
        mid = first + math.ceil((last - first) / n / 2) * n
        quicksort(data, first, last, column)
        stack.extend([first, mid, mid, last])


# @profile
def quicksort(data, first, last, column):
    idx = np.argsort(data[first:last, column], kind='quicksort')
    idx += first
    data[first:last,:] = data[idx,:]
