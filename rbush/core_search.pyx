import numpy as np
cimport numpy as np
np.import_array()

ctypedef np.int_t DTINT_t
ctypedef np.float_t DTFLT_t


# @profile
def search_node(tuple node, np.ndarray[DTFLT_t] bbox, list items):
    cdef:
        np.ndarray[DTFLT_t] ibox
        # object ibox
        double xmin, ymin, xmax, ymax
        bint node_lower_bbox
        bint node_upper_bbox
        bint intersects
        tuple child

    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]

    # print(node[0])
    ibox = node[0]
    # print(ibox[2])
    # Considering 'x' the horizontal axes and 'y' the vertical..
    # * if bbox right border is at the right of node left border
    #      and bbox upper border is above node lower border
    # * if bbox left border is at the left of node right border
    #      and bbox lower border is below node upper border
    # * they intersect:
    node_lower_bbox = ibox[0] <= xmax and ibox[1] <= ymax
    node_upper_bbox = ibox[2] >= xmin and ibox[3] >= ymin
    intersects = node_lower_bbox and node_upper_bbox
    if not intersects:
        return

    if node[2]:
        items.extend(node[1])
        return

    for child in node[1]:
        search_node(child, bbox, items)


cdef list search_nodes(np.ndarray[DTFLT_t] bbox,
                       np.ndarray[DTFLT_t, ndim=2] iboxes,
                       np.ndarray[DTINT_t] data):
    cdef:
        np.ndarray[DTFLT_t] ibox
        unsigned int leng, i=0
        double xmin, ymin, xmax, ymax
        bint node_lower_bbox
        bint node_upper_bbox
        bint intersects
        # array.array a = array.array('i')
        list out = []

    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]

    leng = len(iboxes)
    for i in range(leng):
        ibox = iboxes[i]
        # Considering 'x' the horizontal axes and 'y' the vertical..
        # * if bbox right border is at the right of node left border
        #      and bbox upper border is above node lower border
        # * if bbox left border is at the left of node right border
        #      and bbox lower border is below node upper border
        # * they intersect:
        node_lower_bbox = ibox[0] <= xmax and ibox[1] <= ymax
        node_upper_bbox = ibox[2] >= xmin and ibox[3] >= ymin
        intersects = node_lower_bbox and node_upper_bbox
        if not intersects:
            continue
        out.append(data[i])

    return out


# @profile
def search(tuple node, np.ndarray[DTFLT_t] bbox):
    items = []

    # First collect all items from intersecting leaves
    search_node(node, bbox, items)

    if not len(items):
        return None

    iboxes, data = zip(*items)
    iboxes = np.asarray(iboxes)
    data = np.asarray(data).astype(int)

    # Filter the intersecting items
    items = search_nodes(bbox, iboxes, data)

    return items
