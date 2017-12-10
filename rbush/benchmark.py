import time

N_INSERT = 10**3
N_REMOVE = 10**2
MAX_ENTRIES = 16


def search(tree, data):
    tic = time.time()
    for item in data:
        tree.search(**item)
    return time.time() - tic


def insertion(tree, data):
    tic = time.time()
    for item in data:
        tree.insert(**item)
    return time.time() - tic


def removal(tree, data):
    tic = time.time()
    for item in data:
        tree.remove(**item)
    return time.time() - tic


def load(tree, data):
    tic = time.time()
    tree.load(data)
    return time.time() - tic


def run(N_insert=None, N_remove=None, _load=None):
    from rbush import RBush
    from rbush.data import generate_data_items, generate_data_array

    N_insert = N_insert or N_INSERT
    N_remove = N_remove or N_REMOVE
    N_search = N_remove

    data_items = generate_data_items(N_insert, 1)
    data_array = generate_data_array(N_insert, 1)
    bboxes100 = generate_data_items(N_search, 10)
    bboxes10 = generate_data_items(N_search, 1)
    bboxes1 = generate_data_items(N_search, 0.01)

    if not _load:
        tree = RBush(MAX_ENTRIES)

        # insertion
        t_insertion = insertion(tree, data_items)
        print('{:d} insertions one-by-one: {:.5f}'.format(N_insert, t_insertion))

        # Search items 10%
        t_search100 = search(tree, bboxes100)
        print('{:d} searches in ~10%: {:.5f}'.format(N_search, t_search100))

        # Search items 1%
        t_search10 = search(tree, bboxes10)
        print('{:d} searches in ~1%: {:.5f}'.format(N_search, t_search10))

        # Search items 0.01%
        t_search1 = search(tree, bboxes1)
        print('{:d} searches in ~0.01%: {:.5f}'.format(N_search, t_search1))

        # removal
        t_removal = removal(tree, data_items[:1000])
        print('{:d} removals: {:.5f}'.format(N_search, t_removal))

    print('Bulk load:')

    tree = RBush(MAX_ENTRIES)

    # Bulk load
    t_bulk = load(tree, data_array)
    print('{:d} items bulk load: {:.5f}'.format(N_insert, t_bulk))

    # Search items 10%
    t_search100 = search(tree, bboxes100)
    print('{:d} searches in ~10%: {:.5f}'.format(N_search, t_search100))

    # Search items 1%
    t_search10 = search(tree, bboxes10)
    print('{:d} searches in ~1%: {:.5f}'.format(N_search, t_search10))

    # Search items 0.01%
    t_search1 = search(tree, bboxes1)
    print('{:d} searches in ~0.01%: {:.5f}'.format(N_search, t_search1))


def usage():
    print(' Usage:\n\t python benchmark.py [n_insert] [n_remove] [load]')
    print(" 'load' escapes insertion one-by-one")


if __name__ == '__main__':
    import sys

    _load = None
    if len(sys.argv) > 3:
        _load = sys.argv[3]
    try:
        N_remove = int(sys.argv[2]) if len(sys.argv) > 2 else None
        N_insert = int(sys.argv[1]) if len(sys.argv) > 1 else None
    except:
        usage()
        sys.exit(0)

    run(N_insert, N_remove, _load)
