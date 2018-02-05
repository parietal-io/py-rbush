
# import numpy as np
cimport numpy as np
np.import_array()

ctypedef np.float_t DTYPE_t

# @profile
def search(node, bbox):
    items = []
    search_node(node, bbox, items)
    items = search_nodes(items, bbox)
    return items


# @profile
#cdef void search_node(tuple node, tuple bbox, list items):
def search_node(tuple node, tuple bbox, list items):
    cdef:
        bint node_lower_bbox
        bint node_upper_bbox
        bint intersects
        tuple child
        tuple ibox

    ibox = node[0]
    # Considering 'x' the horizontal axes and 'y' the vertical..
    # * if bbox right border is at the right of node left border
    #      and bbox upper border is above node lower border
    # * if bbox left border is at the left of node right border
    #      and bbox lower border is below node upper border
    # * they intersect:
    node_lower_bbox = ibox[0] <= bbox[2] and ibox[1] <= bbox[3]
    node_upper_bbox = ibox[2] >= bbox[0] and ibox[3] >= bbox[1]
    intersects = node_lower_bbox and node_upper_bbox
    if not intersects:
        return

    if node[2]:
        items.extend(node[1])
        return

    for child in node[1]:
        search_node(child, bbox, items)


cdef list search_nodes(list items, tuple bbox):
    cdef:
        list out
        unsigned int i
        tuple item
        bint node_lower_bbox
        bint node_upper_bbox
        bint intersects
        np.ndarray[DTYPE_t] ibox

    out = []
    for i in range(len(items)):
        item = items[i]
        ibox = item[0]
        # Considering 'x' the horizontal axes and 'y' the vertical..
        # * if bbox right border is at the right of node left border
        #      and bbox upper border is above node lower border
        # * if bbox left border is at the left of node right border
        #      and bbox lower border is below node upper border
        # * they intersect:
        node_lower_bbox = ibox[0] <= bbox[2] and ibox[1] <= bbox[3]
        node_upper_bbox = ibox[2] >= bbox[0] and ibox[3] >= bbox[1]
        intersects = node_lower_bbox and node_upper_bbox
        if intersects:
            out.append(item[1])
    return out
