import time
from random import random
import math

from rbush import Rbush
from rbush.data import generate_data

N_insert = 10**5
N_search = 10**3
maxEntries = 9

def run():

    data = generate_data(N_insert,1)
    data2 = generate_data(N_insert, 1);
    bboxes100 = generate_data(N_search, 100 * math.sqrt(0.1));
    bboxes10 = generate_data(N_search, 10);
    bboxes1 = generate_data(N_search, 1);

    tree = Rbush(maxEntries)
    # insertion
    def insertion(tree,data):
        tic = time.time()
        for item in data:
            tree.insert(item)
        return time.time() - tic
    t_insertion = insertion(tree,data)
    print('{:d} insertions one-by-one: {:.5f}'.format(N_insert,t_insertion))

    # Search items 10%
    def search(tree,data):

        tic = time.time()
        for item in data:
            tree.search(item)
        return time.time() - tic
    t_search100 = search(tree,bboxes100)
    print('{:d} searchs in ~10%: {:.5f}'.format(N_search,t_search100))

    # Search items 1%
    def search(tree,data):
        tic = time.time()
        for item in data:
            tree.search(item)
        return time.time() - tic
    t_search10 = search(tree,bboxes10)
    print('{:d} searchs in ~1%: {:.5f}'.format(N_search,t_search10))

    # Search items 0.01%
    def search(tree,data):
        tic = time.time()
        for item in data:
            tree.search(item)
        return time.time() - tic
    t_search1 = search(tree,bboxes1)
    print('{:d} searchs in ~0.01%: {:.5f}'.format(N_search,t_search1))

    # removal
    def removal(tree,data):
        tic = time.time()
        for item in data:
            tree.remove(item)
        return time.time() - tic
    t_removal = removal(tree,data[:1000])
    print('{:d} removals: {:.5f}'.format(N_search,t_removal))


    tree = Rbush(maxEntries)
    # Bulk load
    def load(tree,data):
        tic = time.time()
        tree.load(data)
        return time.time() - tic
    t_bulk = load(tree,data2)
    print('{:d} items bulk load: {:.5f}'.format(N_insert,t_bulk))

    # Search items 1%
    def search(tree,data):
        tic = time.time()
        for item in data:
            tree.search(item)
        return time.time() - tic
    t_search10 = search(tree,bboxes10)
    print('{:d} searchs in ~1%: {:.5f}'.format(N_search,t_search10))

    # Search items 0.01%
    def search(tree,data):
        tic = time.time()
        for item in data:
            tree.search(item)
        return time.time() - tic
    t_search1 = search(tree,bboxes1)
    print('{:d} searchs in ~0.01%: {:.5f}'.format(N_search,t_search1))

if __name__ == '__main__':
    run()
