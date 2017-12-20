import pytest
import sys
import numpy as np
from rbush import RBush
from rbush import to_dict

Infinity = sys.maxsize


def some_data(n):
    data = []
    for i in range(0, n):
        data.append({'xmin': i, 'ymin': i, 'xmax': i, 'ymax': i})
    return data


def arr_to_bbox(arr):
    return dict(xmin=arr[0],
                ymin=arr[1],
                xmax=arr[2],
                ymax=arr[3])


def arr_to_columns(darr):
    return dict(xmin=darr[:, 0],
                ymin=darr[:, 1],
                xmax=darr[:, 2],
                ymax=darr[:, 3])


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

data_items = list(map(arr_to_bbox, arr))

data_array = np.array(arr)

data_columns = arr_to_columns(data_array)

arr2 = [[-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity],
        [-Infinity, -Infinity, Infinity, Infinity]]

empty_items = list(map(arr_to_bbox, arr2))

empty_array = np.array(arr2)

empty_columns = arr_to_columns(empty_array)


def default_compare(a):
    return a['xmin'] + a['ymin'] + a['xmax'] + a['ymax']


def sorted_equal(a, b, compare=None):
    compare = compare if compare else default_compare
    return a[:].sort(key=compare) == b[:].sort(key=compare)


# TESTS ======================================================================
#
def test_insert_remove_item():
    item = dict(xmin=0, ymin=10, xmax=20, ymax=30)
    tree = RBush()
    tree.insert(**item)
    assert all([tree.xmin == item['xmin'],
                tree.ymin == item['ymin'],
                tree.xmax == item['xmax'],
                tree.ymax == item['ymax']])
    tree.remove(**item)
    assert len(tree.all()) == 0


def test_root_split():
    maxEntries = 9
    items = some_data(9+1)
    tree = RBush(maxEntries)
    for i, item in enumerate(items):
        tree.insert(**item)
    assert tree.height == 2


def test_default_maxentries():
    # constructor uses 9 max entries by default
    tree = RBush()
    tree.load(arr[:9])
    assert tree.height == 1

    tree2 = RBush()
    tree2.load(arr[:10])
    assert tree2.height == 2


def test_load():
    tree = RBush(4)
    tree.load(arr)
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, data_items)


def test_load_numpy():
    tree = RBush(4)
    tree.load(data_array)
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, data_items)


def test_load_few():
    tree = RBush(8, 4)
    tree.load(data_array[:20])
    tree.load(data_array[0:3])

    tree2 = RBush(8, 4)
    tree2.load(data_array[:20])
    tree2.insert(*data_array[0])
    tree2.insert(*data_array[1])
    tree2.insert(*data_array[2])

    assert tree.to_json() == tree2.to_json()


def test_data_load_empty():
    tree = RBush()
    tree.load([])
    assert tree.to_json() == RBush().to_json()


# t('#load handles the insertion of maxEntries + 2 empty bboxes',
def test_data_load_empty_maxEntries():
    tree = RBush(4)
    tree.load(empty_array)

    assert tree.height == 2
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, empty_items)


# t('#insert handles the insertion of maxEntries + 2 empty bboxes',
def test_data_insert_empty_maxEntries():
    tree = RBush(4)

    for datum in empty_items:
        tree.insert(**datum)

    assert tree.height == 2
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, empty_items)


def test_split_root_on_merge():
    tree = RBush(4)
    tree.load(data_array)
    tree.load(data_array)

    assert tree.height == 4
    data_items.extend(data_items)
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, data_items)


def test_merge_trees():
    smaller = data_array[:10]
#    data_items = data_items + data_items[:10]
    data_items.extend(data_items[:10])

    tree1 = RBush(4)
    tree1.load(data_array)
    tree1.load(smaller)

    tree2 = RBush(4)
    tree2.load(smaller)
    tree2.load(data_array)

    assert tree1.height == tree2.height

    items1 = [to_dict(n) for n in tree1.all()]
    assert sorted_equal(items1, data_items)
    items2 = [to_dict(n) for n in tree2.all()]
    assert sorted_equal(items2, data_items)


def test_find_matching_bbox():
    # 'search' finds items intersecting and inside the given bbox
    tree = RBush(4)
    tree.load(data_array)
    result = tree.search(xmin=40, ymin=20, xmax=80, ymax=70)

    compare_data = [
        [70, 20, 70, 20], [75, 25, 75, 25], [45, 45, 45, 45],
        [50, 50, 50, 50], [60, 60, 60, 60], [70, 70, 70, 70],
        [45, 20, 45, 20], [45, 70, 45, 70], [75, 50, 75, 50],
        [50, 25, 50, 25], [60, 35, 60, 35], [70, 45, 70, 45]
    ]

    compare_data = list(map(arr_to_bbox, compare_data))

    items = [to_dict(n) for n in result]
    assert sorted_equal(items, compare_data)


# # collides returns true when search finds matching points'
# def test_find_collision():
#     tree = RBush(4)
#     tree.load(data)
#     result = tree.collides({'xmin': 40, 'ymin': 20, 'xmax': 80, 'ymax': 70})
#     assert result


def test_find_empty_result():
    tree = RBush(4)
    tree.load(data_array)

    result = tree.search(200, 200, 210, 210)
    assert result == []


# # collides returns false if nothing found
# def test_find_no_collision():
#     tree = RBush(4)
#     tree.load(data)
#     # result = tree.collides([200, 200, 210, 210])
#     result = tree.collides(arr_to_bbox([200, 200, 210, 210]))
#
#     assert not result


def test_retrieve_all():

    tree = RBush(4)
    tree.load(data_array)

    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, data_items)

    bbox = {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}
    items = [to_dict(n) for n in tree.search(**bbox)]
    assert sorted_equal(items, data_items)


# # t('#toDict & #fromJSON exports and imports search tree in JSON format',
# def test_json_io():
#     tree = RBush(4)
#     tree.load(data)
#     tree2 = RBush(4)
#     tree2.fromJSON(tree.toJSON())
#
#     items = tree.all()
#     items2 = tree2.all()
#     assert sorted_equal(items, items2)


def test_insert_item():
    data = [[0, 0, 0, 0],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [1, 1, 2, 2]]
    items = list(map(arr_to_bbox, data))

    tree = RBush(4)
    tree.load(data[0:3])

    tree.insert(*data[3])
    assert tree.height == 1
    result = [to_dict(n) for n in tree.all()]
    assert sorted_equal(result, items[0:4])

    tree.insert(**items[4])
    assert tree.height == 2
    result = [to_dict(n) for n in tree.all()]
    assert sorted_equal(result, items)


def test_insert_none():
    # 'insert' raises exception if empty input
    tree = RBush()
    tree.load(data_array)

    with pytest.raises(TypeError):
        tree.insert()


# t('#insert forms a valid tree if items are inserted one by one',
def test_insert_items():
    tree1 = RBush(4)
    for i in range(len(data_array)):
        tree1.insert(*data_array[i])

    tree2 = RBush(4)
    tree2.load(data_array)

    assert 0 <= tree1.height - tree2.height <= 1
    items1 = [to_dict(n) for n in tree1.all()]
    items2 = [to_dict(n) for n in tree2.all()]
    assert sorted_equal(items1, items2)


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


def test_remove_items():
    tree = RBush(4)
    tree.load(data_array)

    assert tree.height > 1

    len_ = len(data_array)
    items_removed = []
    items_removed.extend(tree.remove(*data_array[0]))
    items_removed.extend(tree.remove(*data_array[1]))
    items_removed.extend(tree.remove(*data_array[2]))

    items_removed.extend(tree.remove(*data_array[len_ - 1]))
    items_removed.extend(tree.remove(*data_array[len_ - 2]))
    items_removed.extend(tree.remove(*data_array[len_ - 3]))

    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(data_items[3: len_-3], items)

    items_rem = [to_dict(n) for n in items_removed]
    assert sorted_equal(data_items[len_-3: 3], items_rem)


def test_remove_nothing():
    # 'remove' does nothing if nothing found
    tree1 = RBush()
    tree1.load(data_array)
    tree2 = RBush()
    tree2.load(data_array)
    tree2.remove(13, 13, 13, 13)
    assert tree1.to_json() == tree2.to_json()


# remove brings the tree to a clear state when removing everything one by one
def test_clean_tree():
    tree = RBush(4)
    tree.load(data_array)

    for i in range(len(data_array)):
        tree.remove(*data_array[i])

    assert tree.height == 1
    assert tree.to_json() == RBush(4).to_json()


# clear should clear all the data in the tree
def test_clear_tree():
    tree = RBush(4)
    tree.load(data_array)
    tree.clear()

    assert tree.to_json() == RBush(4).to_json()


# should have chainable api
def test_chain():
    tree = RBush()
    tree.load(data_array).insert(*data_array[0]).remove(*data_array[0])
    items = [to_dict(n) for n in tree.all()]
    assert sorted_equal(items, data_items)


def test_tree_data():
    data = data_array
    t = RBush()
    t.load(data)
    bboxes = np.asarray([[i.xmin, i.ymin, i.xmax, i.ymax] for i in t.all()])
    ad = np.asarray([data.min(axis=0),data.max(axis=0),data.mean(axis=0)], int)
    ab = np.asarray([bboxes.min(axis=0),bboxes.max(axis=0),bboxes.mean(axis=0)], int)
    assert np.array_equal(ad,ab)


# t('constructor accepts a format argument to customize the data format',
# def test_format_argument():
#     tree = RBush(4, ['minLng', 'minLat', 'maxLng', 'maxLat'])
#     assert tree.toBBox({'minLng': 1, 'minLat': 2, 'maxLng': 3, 'maxLat': 4}),
#                     {'xmin': 1, 'ymin': 2, 'xmax': 3, 'ymax': 4}
#                     )


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
