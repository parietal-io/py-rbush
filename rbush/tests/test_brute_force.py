from rbush.rbush_core import RBush
from rbush.data import generate_data_array
from time import time
import numpy as np

import numba as nb


def test_against_brute_force_numba():
    b = RBush()
    data = generate_data_array(100000,10)
    b.load(data)

    search_box = (-1, -1, 1, 1)

    c = search_brute_force(b.data, b.boxes, *search_box)
    t1 = time()
    c = search_brute_force(b.data, b.boxes, *search_box)
    c = search_brute_force(b.data, b.boxes, *search_box)
    c = search_brute_force(b.data, b.boxes, *search_box)
    t2 = time()
    t_brute = t2 - t1
    print('BRUTE FORCE;', len(c), 'time: {:.5f}'.format(t_brute))

    c = b.search(*search_box)
    rbush_t1 = time()
    c = b.search(*search_box)
    c = b.search(*search_box)
    c = b.search(*search_box)
    rbush_t2 = time()
    #print('RBUSH;', len(c), 'time: {:.5f}'.format(rbush_t2 - rbush_t1))
    t_goal = rbush_t2 - rbush_t1
    print('RBUSH;', c.size, 'time: {:.5f}'.format(t_goal))
    assert t_goal < t_brute, "Nope...not fast enough"


@nb.jit
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


if __name__ == '__main__':
    test_against_brute_force_numba()
