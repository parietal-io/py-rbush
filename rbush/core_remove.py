from ._python import INF, create_node


def remove(root, xmin, ymin, xmax, ymax):
    bbox = (xmin, ymin, xmax, ymax)
    # return remove_item(root, bbox, lambda bbox,node:bbox[0]==node[0][0])
    return remove_item(root, bbox, intersects)


def remove_item(node, bbox, is_equal):
    items = []
    if not intersects(bbox, node):
        return items
    if node[2] is True:
        indexes = []
        for i in range(len(node[1])):
            child = node[1][i]
            if is_equal(bbox, child):
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            items.append(node[1].pop(i))
        if len(items) > 0:
            adjust_bbox(node)
    else:
        indexes = []
        for i in range(len(node[1])):
            child = node[1][i]
            items.extend(remove_item(child, bbox, is_equal))
            if len(child[1]) == 0:
                indexes.append(i)
        for i in range(len(indexes)-1, -1, -1):
            empty = node[1].pop(i)
        if len(items) > 0:
            adjust_bbox(node)
    return items


def intersects(bbox, node):
    node_lower_bbox = node[0][0] <= bbox[2] and node[0][1] <= bbox[3]
    node_upper_bbox = node[0][2] >= bbox[0] and node[0][3] >= bbox[1]
    return node_lower_bbox and node_upper_bbox


def calc_bbox_children_indexes(children, i_ini, i_fin):
    xmin = INF
    xmax = -INF
    ymin = INF
    ymax = -INF
    for i in range(i_ini, i_fin):
        child = children[i]
        xmin = min(xmin, child[0][0])
        ymin = min(ymin, child[0][1])
        xmax = max(xmax, child[0][2])
        ymax = max(ymax, child[0][3])
    return (xmin, ymin, xmax, ymax)


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
