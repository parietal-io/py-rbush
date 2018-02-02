from .core_common import (xminf, xmaxf, yminf, ymaxf,
                          childrenf, dataf, leaff)


# @profile
def search(node, bbox):
    items = []
    search_node(node, bbox, items)
    items = search_nodes(items, bbox)
    return items


# @profile
def search_node(node, bbox, items):

    # Considering 'x' the horizontal axes and 'y' the vertical..
    # * if bbox right border is at the right of node left border
    #      and bbox upper border is above node lower border
    # * if bbox left border is at the left of node right border
    #      and bbox lower border is below node upper border
    # * they intersect:
    node_lower_bbox = xminf(node) <= bbox[2] and yminf(node) <= bbox[3]
    node_upper_bbox = xmaxf(node) >= bbox[0] and ymaxf(node) >= bbox[1]
    intersects = node_lower_bbox and node_upper_bbox
    if not intersects:
        return

    if leaff(node):
        items.extend(childrenf(node))
        return

    for child in childrenf(node):
        search_node(child, bbox, items)

#import numba as nb
#@nb.njit
def search_nodes(items, bbox):
    out = []
    for i in range(len(items)):
        item = items[i]
        # Considering 'x' the horizontal axes and 'y' the vertical..
        # * if bbox right border is at the right of node left border
        #      and bbox upper border is above node lower border
        # * if bbox left border is at the left of node right border
        #      and bbox lower border is below node upper border
        # * they intersect:
        node_lower_bbox = xminf(item) <= bbox[2] and yminf(item) <= bbox[3]
        node_upper_bbox = xmaxf(item) >= bbox[0] and ymaxf(item) >= bbox[1]
        intersects = node_lower_bbox and node_upper_bbox
        if intersects:
            out.append(dataf(item))
    return out
