from .node import *
from copy import copy
import math


def remove(root, xmin, ymin, xmax, ymax):
    bbox = create_node(xmin, ymin, xmax, ymax)
    return remove_item(root, bbox, lambda a,b:a.xmin==b.xmin)


def remove_item(node, bbox, is_equal):
    items = []
    if not intersects(bbox, node):
        return items
    if node.leaf:
        indexes = []
        for i in range(len(node.children)):
            child = get(node.children, i)
            if is_equal(bbox, child):
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            items.append(node.children.pop(i))
        if len(items) > 0:
            adjust_bbox(node)
    else:
        indexes = []
        for i in range(len(node.children)):
            child = get(node.children, i)
            items.extend(remove_item(child, bbox, is_equal))
            if len(child.children) == 0:
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            empty = node.children.pop(i)
        if len(items) > 0:
            adjust_bbox(node)
    return items


#@profile
def insert(root, xmin, ymin, xmax, ymax, data,
           maxentries, minentries):
    """
    Insert arrays [xmin],[ymin],[xmax],[ymax],[data]
    """
    for i in range(len(xmin)):
        item = create_node(xmin[i], ymin[i], xmax[i], ymax[i], data[i])
        root = insert_node(root, item, maxentries, minentries)
    return root


#@profile
def insert_node(root, item, maxentries, minentries):
    """
    Insert node 'item' accordingly in 'root' node (tree)
    """
    if item.height is None:
        level = root.height - 1
    else:
        level = root.height - item.height - 1
    path = list()
    node = choose_subtree(root, item, level, path)

    node.children.append(item)
    # node = extend(node, item)  # this will be done by 'adjust_bboxes' below

    assert get(path, len(path)-1) is node
    assert get(path, 0) is root

    adjusted_path = adjust_bboxes(item, path)

    if len(node.children) > maxentries:
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

        if node.leaf or len(path)-1 == level:
            break

        min_enlargement = INF
        min_area = INF

        target_node = None
        for i in range(len(node.children)):
            child = get(node.children, i)
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

        node = target_node or get(node.children, 0)

    return node


# @profile
def balance_nodes(path, maxentries, minentries):
    root = get(path, 0)
    for level in range(len(path)-1, -1, -1):
        node = get(path, level)
        if len(node.children) <= maxentries:
            break
        new_node1, new_node2 = split(node, minentries)
        assert node.height == new_node1.height
        assert node.height == new_node2.height
        if level > 0:
            parent = get(path, level-1)
            ind = parent.children.index(node)
            node_trash = parent.children.pop(i)
            assert node is node_trash
            parent.children.append(new_node1)
            parent.children.append(new_node2)
            # NOTE: 'parent' has had your borders extended when we 'insert'
        else:
            children = list()
            children.append(new_node1)
            children.append(new_node2)
            root = create_node(children=children,
                               leaf=False,
                               height=new_node1.height+1)
            root = adjust_bbox(root)
    return root


# @profile
def search(node, xmin, ymin, xmax, ymax):
    bbox = create_node(xmin, ymin, xmax, ymax)
    return search_node(node, bbox)


def search_node(node, bbox):
    items = list()
    if node is None:
        return items
    if not intersects(bbox, node):
        return items
    if contains(bbox, node):
        items.extend(retrieve_all_items(node))
        return items
    if node.children is None:
        items.append(node)
    else:
        n_items = len(node.children)
        for i in range(n_items):
            child = get(node.children, i)
            items.extend(search_node(child, bbox))
    return items


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
        xmin, ymin, xmax, ymax, data = data.T
        return insert(root, xmin, ymin, xmax, ymax, data,
                      maxentries=maxentries, minentries=minentries)

    # recursively build the tree with the given data
    # from scratch using OMT algorithm
    node = build_tree(data, 0, len(data)-1, maxentries, minentries)

    if not len(root.children):
        # save as is if tree is empty
        root = node
    elif (root.height == node.height):
        # split root if trees have the same height
        children = list()
        children.append(root)
        children.append(node)
        root = create_node(children=children,
                           leaf=False,
                           height=node.height+1)
        root = adjust_bbox(root)
    else:
        if root.height < node.height:
            # swap trees if inserted one is bigger
            tmpNode = root
            root = node
            node = tmpNode
        # insert the small tree into the large tree at appropriate level
        level = root.height - node.height - 1
        root = insert_node(root, node, level, True)
    return root


@profile
def build_tree(data, first, last, maxentries, minentries, height=None):
    """
    Build RBush from 'data' items between 'first','last' (inclusive)
    """
    N = last - first + 1
    M = maxentries

    if N <= M:
        children = list()
        for i in range(first, last+1):
            _node = create_node(data[i][0], data[i][1], data[i][2], data[i][3])
            children.append(_node)
        node = create_node(children=children, leaf=True, height=1)
        node = adjust_bbox(node)
        return node

    if height is None:
        # target height of the bulk-loaded tree
        height = math.ceil(math.log(N) / math.log(M))

        # target number of root entries to maximize storage utilization
        M = math.ceil(N / math.pow(M, height - 1))

    node = create_node(leaf=False, height=height, children=list())

    # split the data into M mostly square tiles
    N2 = math.ceil(N / M)
    N1 = N2 * math.ceil(math.sqrt(M))

    multiselect(data, first, last, N1, 0)

    for i in range(first, last+1, N1):
        last2 = min(i + N1 - 1, last)
        multiselect(data, i, last2, N2, 1)
        for j in range(i, last2+1, N2):
            last3 = min(j + N2 - 1, last2)
            # pack each entry recursively
            node.children.append(build_tree(data, first=j, last=last3,
                                            height=height - 1,
                                            maxentries=maxentries,
                                            minentries=minentries))
    node = adjust_bbox(node)
    return node


# def compare_x(a, b):
#     # return a.xmin - b.xmin
#     return a[0] - b[0]
#
#
# def compare_y(a, b):
#     # return a.ymin - b.ymin
#     return a[1] - b[1]


@profile
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


@profile
def quicksort(data, first, last, column):
    idx = np.argsort(data[first:last, column], kind='quicksort')
    data[first:last,:] = data[idx,:]


# def create_subarray(data, first, last, column):
#     last = last+1
#     arange = np.arange(first, last).reshape(last-first, 1)
#     sdata = data[first:last, column].reshape(last-first, 1)
#     sdata = np.concatenate([arange, sdata], axis=1).astype(int)
#     return sdata


# def overwrite_array(data, sdata, first, last):
#     last = last+1
#     inds = sdata[:, 0]
#     data[first:last] = data[inds.tolist()]
#     return data


# from numba import njit, int32, jit, int64


# @njit(int64(int64[:],int64[:]))
# def compare(a, b):
#     # return a.ymin - b.ymin
#     return a[1] - b[1]
#
# @njit((int64[:,:],int64,int64))
# def swap(arr, i, j):
#     tmp = arr[i]
#     arr[i] = arr[j]
#     arr[j] = tmp


# @profile
# @njit((int64[:,:],int64,int64,int64))
# def quickselect(data, k, first, last):
#     while (last > first):
#         if last - first > 600:
#             n = last - first + 1
#             m = k - first + 1
#             z = math.log(n)
#             s = 0.5 * math.exp(2 * z / 3)
#             if m - n / 2 < 0:
#                 d = -1
#             else:
#                 d = 1
#             sd = 0.5 * math.sqrt(z * s * (n - s) / n) * d
#             newLeft = max(first, math.floor(k - m * s / n + sd))
#             newRight = min(last, math.floor(k + (n - m) * s / n + sd))
#             quickselect(data, k, newLeft, newRight)
#
#         t = data[k]
#         i = first
#         j = last
#
#         swap(data, first, k)
#         if (compare(data[last], t) > 0):
#             swap(data, first, last)
#
#         while (i < j):
#             swap(data, i, j)
#             i = i+1
#             j = j-1
#             while (compare(data[i], t) < 0):
#                 i = i+1
#             while (compare(data[j], t) > 0):
#                 j = j-1
#
#         if (compare(data[first], t) == 0):
#             swap(data, first, j)
#         else:
#             j = j+1
#             swap(data, j, last)
#
#         if (j <= k):
#             first = j + 1
#         if (k <= j):
#             last = j - 1
#
#
# def default_compare(a, b):
#     if a < b:
#         return -1
#     if a > b:
#         return 1
#     return 0
