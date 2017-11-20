from .core import *
from .node import *

import math


# @profile
def insert(root, xmin, ymin, xmax, ymax,  # data,
           maxentries, minentries):
    if len(xmin) > 1:
        return load(root, [xmin, ymin, xmax, ymax], maxentries, minentries)
    else:
        item = create_node(xmin[0], ymin[0], xmax[0], ymax[0])  # , data[0])
        return _insert_item(root, item, maxentries, minentries)


def _insert_item(root, item, maxentries, minentries):
    if item.height is None:
        level = root.height - 1
    else:
        level = root.height - item.height - 1
    path = list()
    node = choose_subtree(root, item, level, path)

    node.children.append(item)
    node = extend(node, item)

    assert get(path, len(path)-1) is node
    assert get(path, 0) is root

    if len(node.children) > maxentries:
        root = balance_tree(path, maxentries, minentries)
    return root


# @profile
def search(node, xmin, ymin, xmax, ymax):
    bbox = create_node(xmin, ymin, xmax, ymax)
    return search_item(node, bbox)


def search_item(node, bbox):
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
            items.extend(search_item(child, bbox))
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
            # NOTE: 'parent' has had your borders extended when we 'insert'
        else:
            children = list()
            children.append(node)
            children.append(new_node)
            root = create_node(children=children,
                               leaf=False,
                               height=node.height+1)
            adjust_bbox(root)
    return root


# @profile
def choose_subtree(node, bbox, level, path):
    '''
    Return the node and add to path the tree to insert new item

    Traverse the subtree searching for the node tightest path,
    the node at the end is where closest to 'bbox' is closer or

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
    len_ = len(data)
    if len_ < minentries:
        for i in range(len_):
            root = insert(root, *data[i],
                          maxentries=maxentries, minentries=minentries)
        return root

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
        adjust_bbox(root)
    else:
        if root.height < node.height:
            # swap trees if inserted one is bigger
            tmpNode = root
            root = node
            node = tmpNode
        # insert the small tree into the large tree at appropriate level
        level = root.height - node.height - 1
        root = _insert_item(root, node, level, True)
    return root


def build_tree(data, first, last, maxentries, minentries, height=None):
    """
    Build RBush from 'data' items between 'first','last' (inclusive)
    """
    N = last - first + 1
    M = maxentries

    if N <= M:
        children = list()
        for i in range(first, last+1):
            children.append(create_node(data[i][0], data[i][1],
                                        data[i][2], data[i][3]))
        node = create_node(children=children, leaf=True, height=1)
        adjust_bbox(node)
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

    multiselect(data, first, last, N1, compare_x)

    for i in range(first, last+1, N1):
        last2 = min(i + N1 - 1, last)
        multiselect(data, i, last2, N2, compare_y)
        for j in range(i, last2+1, N2):
            last3 = min(j + N2 - 1, last2)
            # pack each entry recursively
            node.children.append(build_tree(data, first=j, last=last3,
                                            height=height - 1,
                                            maxentries=maxentries,
                                            minentries=minentries))
    adjust_bbox(node)
    return node


def compare_x(a, b):
    # return a.xmin - b.xmin
    return a[0] - b[0]


def compare_y(a, b):
    # return a.ymin - b.ymin
    return a[1] - b[1]


def multiselect(data, first, last, n, compare):
    stack = [first, last]
    mid = None
    while len(stack):
        first = stack.pop(0)
        last = stack.pop(0)
        if (last - first) <= n:
            continue
        mid = first + math.ceil((last - first) / n / 2) * n
        quickselect(data, mid, first, last, compare)
        stack.extend([first, mid, mid, last])


def quickselect(data, k, first, last, compare):
    while (last > first):
        if last - first > 600:
            n = last - first + 1
            m = k - first + 1
            z = math.log(n)
            s = 0.5 * math.exp(2 * z / 3)
            d = -1 if m - n / 2 < 0 else 1
            sd = 0.5 * math.sqrt(z * s * (n - s) / n) * d
            newLeft = max(first, math.floor(k - m * s / n + sd))
            newRight = min(last, math.floor(k + (n - m) * s / n + sd))
            quickselect(data, k, newLeft, newRight, compare)

        t = data[k]
        i = first
        j = last

        swap(data, first, k)
        if (compare(data[last], t) > 0):
            swap(data, first, last)

        while (i < j):
            swap(data, i, j)
            i = i+1
            j = j-1
            while (compare(data[i], t) < 0):
                i = i+1
            while (compare(data[j], t) > 0):
                j = j-1

        if (compare(data[first], t) == 0):
            swap(data, first, j)
        else:
            j = j+1
            swap(data, j, last)

        if (j <= k):
            first = j + 1
        if (k <= j):
            last = j - 1


def swap(arr, i, j):
    tmp = arr[i]
    arr[i] = arr[j]
    arr[j] = tmp


def default_compare(a, b):
    if a < b:
        return -1
    if a > b:
        return 1
    return 0
