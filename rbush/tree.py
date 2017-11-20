from .core import *
from .node import *


@profile
def insert(root, xmin, ymin, xmax, ymax, data, maxentries, minentries):
    item = create_node(xmin, ymin, xmax, ymax, data)

    path = list()
    node = choose_subtree(root, item, path)

    node.children.append(item)
    node = extend(node, item)

    assert get(path, len(path)-1) is node
    assert get(path, 0) is root

    if len(node.children) > maxentries:
        root = balance_tree(path, maxentries, minentries)
    return root


@profile
def search(node, xmin, ymin, xmax, ymax):
    bbox = create_node(xmin, ymin, xmax, ymax)
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


@profile
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
            children = list()
            children.append(node)
            children.append(new_node)
            root = create_node(children=children,
                               leaf=False,
                               height=node.height+1)
    return root


@profile
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
