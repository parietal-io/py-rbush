import sys
from rbush import RBush

Infinity = sys.maxsize


def default_compare(a):
    return a['xmin'] + a['ymin'] + a['xmax'] + a['ymax']


def some_data(n):
    data = []
    for i in range(0, n):
        data.append({'xmin': i, 'ymin': i, 'xmax': i, 'ymax': i})
    return data


def arr_to_bbox(arr):
    return dict(
                xmin=arr[0],
                ymin=arr[1],
                xmax=arr[2],
                ymax=arr[3],
                data=None
                )


arr = [[0, 0, 0, 0], [10, 10, 10, 10], [20, 20, 20, 20], [25, 0, 25, 0],
       [35, 10, 35, 10], [45, 20, 45, 20], [0, 25, 0, 25], [10, 35, 10, 35],
       [20, 45, 20, 45], [25, 25, 25, 25], [35, 35, 35, 35], [45, 45, 45, 45],
       [50, 0, 50, 0], [60, 10, 60, 10], [70, 20, 70, 20], [75, 0, 75, 0],
       [85, 10, 85, 10], [95, 20, 95, 20], [50, 25, 50, 25], [60, 35, 60, 35],
       [70, 45, 70, 45], [75, 25, 75, 25], [85, 35, 85, 35], [95, 45, 95, 45],
       [0, 50, 0, 50], [10, 60, 10, 60], [20, 70, 20, 70], [25, 50, 25, 50],
       [35, 60, 35, 60], [45, 70, 45, 70], [0, 75, 0, 75], [10, 85, 10, 85],
       [20, 95, 20, 95], [25, 75, 25, 75], [35, 85, 35, 85], [45, 95, 45, 95],
       [50, 50, 50, 50], [60, 60, 60, 60], [70, 70, 70, 70], [75, 50, 75, 50],
       [85, 60, 85, 60], [95, 70, 95, 70], [50, 75, 50, 75], [60, 85, 60, 85],
       [70, 95, 70, 95], [75, 75, 75, 75], [85, 85, 85, 85], [95, 95, 95, 95]]

data = list(map(arr_to_bbox, arr))

arr2 = [[-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity]]
empty_data = list(map(arr_to_bbox, arr2))


def sorted_equal(a, b, compare=None):
    compare = compare if compare else default_compare
    return a[:].sort(key=compare) == b[:].sort(key=compare)


def test_insert_remove_item():
    item = dict(xmin=0, ymin=10, xmax=20, ymax=30)
    tree = RBush()
    tree.insert(item)
    assert all([tree.xmin == item['xmin'],
                tree.ymin == item['ymin'],
                tree.xmax == item['xmax'],
                tree.ymax == item['ymax']])
    tree.remove(item)
    assert isinstance(tree, RBush)


def test_root_split():
    maxEntries = 9
    items = some_data(9+1)
    tree = RBush(maxEntries)
    for i, item in enumerate(items):
        tree.insert(item)
    assert tree.height == 2


# t('constructor accepts a format argument to customize the data format',
# def test_format_argument():
#     tree = RBush(4, ['minLng', 'minLat', 'maxLng', 'maxLat'])
#     assert tree.toBBox({'minLng': 1, 'minLat': 2, 'maxLng': 3, 'maxLat': 4}),
#                     {'xmin': 1, 'ymin': 2, 'xmax': 3, 'ymax': 4}
#                     )


# t('constructor uses 9 max entries by default',
def test_default_maxEntries():
    tree = RBush()
    tree.load(some_data(9))
    assert tree.toDict()['height'] == 1

    tree2 = RBush()
    tree2.load(some_data(10))
    assert tree2.toDict()['height'] == 2


def test_load():
    tree = RBush(4)
    tree.load(data)
    assert sorted_equal(tree.all(), data)


# t('#load uses standard insertion when given a low number of items',
def test_dataLoad_fewMethod():
    tree = RBush(8)
    tree.load(data)
    tree.load(data[0:3])

    tree2 = RBush(8)
    tree2.load(data)
    tree2.insert(data[0])
    tree2.insert(data[1])
    tree2.insert(data[2])

    assert tree.toDict() == tree2.toDict()


# t('#load does nothing if loading empty data',
def test_data_load_empty():
    tree = RBush()
    tree.load([])
    assert tree.toDict() == RBush().toDict()


# t('#load handles the insertion of maxEntries + 2 empty bboxes',
def test_data_load_empty_maxEntries():
    tree = RBush(4)
    tree.load(empty_data)

    assert tree.toDict()['height'] == 2
    assert sorted_equal(tree.all(), empty_data)


# t('#insert handles the insertion of maxEntries + 2 empty bboxes',
def test_data_insert_empty_maxEntries():
    tree = RBush(4)

    for datum in empty_data:
        tree.insert(datum)

    assert tree.toDict()['height'] == 2
    assert sorted_equal(tree.all(), empty_data)


# t('#load properly splits tree root when merging trees of the same height',
def test_split_root_on_merge():
    tree = RBush(4)
    tree.load(data)
    tree.load(data)

    assert tree.toDict()['height'] == 4
    data.extend(data)
    assert sorted_equal(tree.all(), data)


def test_merge_trees():
    smaller = some_data(10)
    tree1 = RBush(4)
    tree1.load(data)
    tree1.load(smaller)

    tree2 = RBush(4)
    tree2.load(smaller)
    tree2.load(data)

    assert tree1.toDict()['height'] == tree2.toDict()['height']
    assert sorted_equal(tree1.all(), data + smaller)
    assert sorted_equal(tree2.all(), data + smaller)


# search finds matching points in the tree given a bbox
def test_find_matching_bbox():

    tree = RBush(4)
    tree.load(data)
    result = tree.search({'xmin': 40, 'ymin': 20, 'xmax': 80, 'ymax': 70})

    compare_data = [
        [70, 20, 70, 20], [75, 25, 75, 25], [45, 45, 45, 45],
        [50, 50, 50, 50], [60, 60, 60, 60], [70, 70, 70, 70],
        [45, 20, 45, 20], [45, 70, 45, 70], [75, 50, 75, 50],
        [50, 25, 50, 25], [60, 35, 60, 35], [70, 45, 70, 45]
    ]

    compare_data = list(map(arr_to_bbox, compare_data))

    assert sorted_equal(result, compare_data)


# collides returns true when search finds matching points'
def test_find_collision():
    tree = RBush(4)
    tree.load(data)
    result = tree.collides({'xmin': 40, 'ymin': 20, 'xmax': 80, 'ymax': 70})
    assert result


# search returns an empty array if nothing found
def test_find_empty_result():
    tree = RBush(4)
    tree.load(data)
    # result = tree.search([200, 200, 210, 210])
    result = tree.search(arr_to_bbox([200, 200, 210, 210]))
    assert result == []


# collides returns false if nothing found
def test_find_no_collision():
    tree = RBush(4)
    tree.load(data)
    # result = tree.collides([200, 200, 210, 210])
    result = tree.collides(arr_to_bbox([200, 200, 210, 210]))

    assert not result


# t('#all returns all points in the tree',
def test_retrieve_all():

    tree = RBush(4)
    tree.load(data)
    result = tree.all()

    assert sorted_equal(result, data)
    bbox = {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}
    assert sorted_equal(tree.search(bbox), data)


# t('#toDict & #fromJSON exports and imports search tree in JSON format',
def test_json_io():
    tree = RBush(4)
    tree.load(data)
    tree2 = RBush(4)
    tree2.fromJSON(tree.toJSON())

    items = tree.all()
    items2 = tree2.all()
    assert sorted_equal(items, items2)


# t('#insert adds an item to an existing tree correctly',
def test_insert_item():
    items = list(map(arr_to_bbox,
                     [[0, 0, 0, 0],
                      [1, 1, 1, 1],
                      [2, 2, 2, 2],
                      [3, 3, 3, 3],
                      [1, 1, 2, 2]]))

    tree = RBush(4)
    tree.load(items[0:3])

    tree.insert(items[3])
    assert tree.toDict()['height'] == 1
    assert sorted_equal(tree.all(), items[0:4])

    tree.insert(items[4])
    assert tree.toDict()['height'] == 2
    assert sorted_equal(tree.all(), items)


# t('#insert does nothing if given undefined',
def test_insert_none():
    tree = RBush()
    tree.load(data)
    tree2 = RBush()
    tree2.load(data)

    tree2.insert()
    tree2.insert({})
    assert tree == tree2


# t('#insert forms a valid tree if items are inserted one by one',
def test_insert_items():
    tree = RBush(4)

    for i in range(0, len(data)):
        tree.insert(data[i])

    tree2 = RBush(4)
    tree2.load(data)

    assert tree.toDict()['height'] - tree2.toDict()['height'] <= 1
    assert sorted_equal(tree.all(), tree2.all())


# Insert vectors of coordinates
def test_insert_numpy_vectors():
    numitems = 100
    import numpy as np
    xmin = np.random.randint(0, 100, numitems)
    ymin = np.random.randint(0, 100, numitems)
    xmax = xmin + np.random.randint(0, 100, numitems)
    ymax = ymin + np.random.randint(0, 100, numitems)

    tree = RBush()
    tree.insert(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
    assert len(tree.all()) == numitems


# t('#remove removes items correctly',
def test_remove_items():
    tree = RBush(4)
    tree.load(data)

    len_ = len(data)

    tree.remove(data[0])
    tree.remove(data[1])
    tree.remove(data[2])

    tree.remove(data[len_ - 1])
    tree.remove(data[len_ - 2])
    tree.remove(data[len_ - 3])

    assert sorted_equal(data[3: len_-3], tree.all())


# t('#remove does nothing if nothing found',
def test_remove_nothing():
    tree = RBush()
    tree.load(data)
    tree2 = RBush()
    tree2.load(data)
    tree2.remove(arr_to_bbox([13, 13, 13, 13]))
    assert tree == tree2


# t('#remove does nothing if given undefined',
# def remove_none():
#     assert RBush().load(data) == RBush().load(data).remove()


# t('#remove accepts an equals function',
# def test_remove_function():
#     import json
#     tree = RBush(4)
#     tree.load(data)
#
#     item = {'xmin': 20, 'ymin': 70, 'xmax': 20, 'ymax': 70, 'foo': 'bar'}
#
#     tree.insert(item)
#     tree.remove(item, lambda a,b: a['foo'] == b['foo'])
#
#     sorted_equal(tree.all(), data)


# remove brings the tree to a clear state when removing everything one by one
def test_clean_tree():
    tree = RBush(4)
    tree.load(data)

    # js = tree.toJSON()

    for i in range(0, len(data)):
        tree.remove(data[i])

    assert tree.toDict() == RBush(4).toDict()


# clear should clear all the data in the tree
def test_clear_tree():
    tree = RBush(4)
    tree.load(data)
    tree.clear()

    assert tree.toDict() == RBush(4).toDict()


# should have chainable api
def test_chain():
    tree = RBush()
    tree.load(data)
    tree.insert(data[0])
    tree.remove(data[0])
