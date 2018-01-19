from rbush import RBush
from rbush.data import generate_data_array
from time import time
import numpy as np

import numba as nb

from tinyr import RTree

def test_against_brute_force_numba():
    data = generate_data_array(100000,10)

    b = RBush()
    b.load(data)

    b.boxes = data
    b.data = np.arange(len(data))
    
    search_box = (-1, -1, 1, 1)

    c = search_brute_force(b.data, b.boxes, *search_box)
    t1 = time()
    c = search_brute_force(b.data, b.boxes, *search_box)
    c = search_brute_force(b.data, b.boxes, *search_box)
    c = search_brute_force(b.data, b.boxes, *search_box)
    t2 = time()
    print('BRUTE FORCE;', len(c), 'time: {:.5f}'.format(t2 - t1))

    r = RTree()
    for i,d in enumerate(data):
        r.insert(i,tuple(d))

    c = r.search(search_box)
    rbush_t1 = time()
    c = r.search(search_box)
    c = r.search(search_box)
    c = r.search(search_box)
    rbush_t2 = time()
    print('RBUSH;', len(c), 'time: {:.5f}'.format(rbush_t2 - rbush_t1))
    assert rbush_t2 - rbush_t1 < t2 - t1, 'Sorry not fast enough yet'


@nb.njit
def search_brute_force(data, boxes, xmin, ymin, xmax, ymax):
    final_result = []
    for i in range(len(boxes)):
        rxmin = boxes[i][0]
        rymin = boxes[i][1]
        rxmax = boxes[i][2]
        rymax = boxes[i][3]

        # intersects
        if (rxmin <= xmax and rymin <= ymax) and (rxmax >= xmin and rymax >= ymin):
            final_result.append(data[i])

    return final_result
