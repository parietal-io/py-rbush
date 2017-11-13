import sys
Infinity = sys.maxsize

import unittest

from rbush import RBush
Rbush = RBush

# def defaultCompare(a, b):
#     return (a.xmin - b.xmin) or (a.ymin - b.ymin) or (a.xmax - b.xmax) or (a.ymax - b.ymax);
def defaultCompare(a):
    return a['xmin'] + a['ymin'] + a['xmax'] + a['ymax']


def someData(n):
    data = [];
    for i in range(0, n):
        data.append({'xmin': i, 'ymin': i, 'xmax': i, 'ymax': i});
    return data;


def arrToBBox(arr):
    return dict(
                xmin = arr[0],
                ymin = arr[1],
                xmax = arr[2],
                ymax = arr[3],
                data = None
                )


data = list( map( arrToBBox,
    [[0,0,0,0],   [10,10,10,10],[20,20,20,20],[25,0,25,0],
    [35,10,35,10],[45,20,45,20],[0,25,0,25],  [10,35,10,35],
    [20,45,20,45],[25,25,25,25],[35,35,35,35],[45,45,45,45],
    [50,0,50,0],  [60,10,60,10],[70,20,70,20],[75,0,75,0],
    [85,10,85,10],[95,20,95,20],[50,25,50,25],[60,35,60,35],
    [70,45,70,45],[75,25,75,25],[85,35,85,35],[95,45,95,45],
    [0,50,0,50],  [10,60,10,60],[20,70,20,70],[25,50,25,50],
    [35,60,35,60],[45,70,45,70],[0,75,0,75],  [10,85,10,85],
    [20,95,20,95],[25,75,25,75],[35,85,35,85],[45,95,45,95],
    [50,50,50,50],[60,60,60,60],[70,70,70,70],[75,50,75,50],
    [85,60,85,60],[95,70,95,70],[50,75,50,75],[60,85,60,85],
    [70,95,70,95],[75,75,75,75],[85,85,85,85],[95,95,95,95]]
    ))

emptyData = list( map( arrToBBox,
    [[-Infinity, -Infinity, Infinity, Infinity],
    [-Infinity, -Infinity, Infinity, Infinity],
    [-Infinity, -Infinity, Infinity, Infinity],
    [-Infinity, -Infinity, Infinity, Infinity],
    [-Infinity, -Infinity, Infinity, Infinity],
    [-Infinity, -Infinity, Infinity, Infinity]]
    ));


def sortedEqual(t, a, b, compare=None):
    compare = compare if compare else defaultCompare;
    # t.same(a.slice().sort(compare), b.slice().sort(compare));
    t.assertEqual(a[:].sort(key=compare), b[:].sort(key=compare));

class TestRbush(unittest.TestCase):

    def test_insert_remove_item(t):
        item = dict(xmin=0,ymin=10,xmax=20,ymax=30)
        tree = RBush()
        tree.insert(item)
        t.assertTrue(all([ tree.xmin == item['xmin'],
                           tree.ymin == item['ymin'],
                           tree.xmax == item['xmax'],
                           tree.ymax == item['ymax'] ]))
        tree.remove(item)
        t.assertEqual(tree, RBush())

    def test_root_split(t):
        maxEntries = 9
        items = someData(9+1)
        tree = RBush(maxEntries)
        for i,item in enumerate(items):
            tree.insert(item)
        t.assertTrue(tree.height == 2)


    # t('constructor accepts a format argument to customize the data format',
    # def test_format_argument(t):
    #     tree = Rbush(4, ['minLng', 'minLat', 'maxLng', 'maxLat']);
    #     t.assertEqual(tree.toBBox({'minLng': 1, 'minLat': 2, 'maxLng': 3, 'maxLat': 4}),
    #                     {'xmin': 1, 'ymin': 2, 'xmax': 3, 'ymax': 4}
    #                     );


    # t('constructor uses 9 max entries by default',
    def test_default_maxEntries(t):
        tree = Rbush()
        tree.load(someData(9));
        t.assertEqual(tree.toDict()['height'], 1);

        tree2 = Rbush()
        tree2.load(someData(10));
        t.assertEqual(tree2.toDict()['height'], 2);


    # t('#toBBox, #comparexmin, #compareymin can be overriden to allow custom data structures',
    # def test_custom_dataStructures(t):
    #     tree = Rbush(4);
    #     tree.toBBox = lambda item: {'xmin': item['minLng'],
    #                                 'ymin': item['minLat'],
    #                                 'xmax': item['maxLng'],
    #                                 'ymax': item['maxLat'] };
    #     tree.comparexmin = lambda a: a['minLng']# - b['minLng'];
    #     tree.compareymin = lambda a: a['minLat']# - b['minLat'];
    #
    #     data = [
    #         {'minLng': -115, 'minLat':  45, 'maxLng': -105, 'maxLat':  55},
    #         {'minLng':  105, 'minLat':  45, 'maxLng':  115, 'maxLat':  55},
    #         {'minLng':  105, 'minLat': -55, 'maxLng':  115, 'maxLat': -45},
    #         {'minLng': -115, 'minLat': -55, 'maxLng': -105, 'maxLat': -45}
    #     ];
    #
    #     tree.load(data);
    #
    #     # def byLngLat(a, b):
    #     #     return a['minLng'] - b['minLng'] or a['minLat'] - b['minLat'];
    #     def byLngLat(a):
    #         return a['minLng'] + a['minLat']
    #
    #     sortedEqual(t, tree.search({'xmin': -180, 'ymin': -90, 'xmax': 180, 'ymax': 90}), [
    #         {'minLng': -115, 'minLat':  45, 'maxLng': -105, 'maxLat':  55},
    #         {'minLng':  105, 'minLat':  45, 'maxLng':  115, 'maxLat':  55},
    #         {'minLng':  105, 'minLat': -55, 'maxLng':  115, 'maxLat': -45},
    #         {'minLng': -115, 'minLat': -55, 'maxLng': -105, 'maxLat': -45}
    #     ], byLngLat);
    #
    #     sortedEqual(t, tree.search({'xmin': -180, 'ymin': -90, 'xmax': 0, 'ymax': 90}), [
    #         {'minLng': -115, 'minLat':  45, 'maxLng': -105, 'maxLat':  55},
    #         {'minLng': -115, 'minLat': -55, 'maxLng': -105, 'maxLat': -45}
    #     ], byLngLat);
    #
    #     sortedEqual(t, tree.search({'xmin': 0, 'ymin': -90, 'xmax': 180, 'ymax': 90}), [
    #         {'minLng': 105, 'minLat':  45, 'maxLng': 115, 'maxLat':  55},
    #         {'minLng': 105, 'minLat': -55, 'maxLng': 115, 'maxLat': -45}
    #     ], byLngLat);
    #
    #     sortedEqual(t, tree.search({'xmin': -180, 'ymin': 0, 'xmax': 180, 'ymax': 90}), [
    #         {'minLng': -115, 'minLat': 45, 'maxLng': -105, 'maxLat': 55},
    #         {'minLng':  105, 'minLat': 45, 'maxLng':  115, 'maxLat': 55}
    #     ], byLngLat);
    #
    #     sortedEqual(t, tree.search({'xmin': -180, 'ymin': -90, 'xmax': 180, 'ymax': 0}), [
    #         {'minLng':  105, 'minLat': -55, 'maxLng':  115, 'maxLat': -45},
    #         {'minLng': -115, 'minLat': -55, 'maxLng': -105, 'maxLat': -45}
    #     ], byLngLat);


    # t('#load bulk-loads the given data given max node entries and forms a proper search tree',
    def test_dataLoad_sort(t):
        tree = Rbush(4)
        tree.load(data);
        sortedEqual(t, tree.all(), data);


    # t('#load uses standard insertion when given a low number of items',
    def test_dataLoad_fewMethod(t):
        tree = Rbush(8)
        tree.load(data)
        tree.load(data[0:3]);

        tree2 = Rbush(8)
        tree2.load(data)
        tree2.insert(data[0])
        tree2.insert(data[1])
        tree2.insert(data[2]);

        t.assertEqual(tree.toDict(), tree2.toDict());


    # t('#load does nothing if loading empty data',
    def test_data_load_empty(t):
        tree = Rbush()
        tree.load([]);
        t.assertEqual(tree.toDict(), Rbush().toDict());


    # t('#load handles the insertion of maxEntries + 2 empty bboxes',
    def test_data_load_empty_maxEntries(t):
        tree = Rbush(4)
        tree.load(emptyData);

        t.assertEqual(tree.toDict()['height'], 2);
        sortedEqual(t, tree.all(), emptyData);


    # t('#insert handles the insertion of maxEntries + 2 empty bboxes',
    def test_data_insert_empty_maxEntries(t):
        tree = Rbush(4);

        for datum in emptyData:
            tree.insert(datum);

        t.assertEqual(tree.toDict()['height'], 2);
        sortedEqual(t, tree.all(), emptyData);


    # t('#load properly splits tree root when merging trees of the same height',
    def test_split_root_on_merge(t):
        tree = Rbush(4)
        tree.load(data)
        tree.load(data);

        t.assertEqual(tree.toDict()['height'], 4);
        data.extend(data)
        sortedEqual(t, tree.all(), data);


    # t('#load properly merges data of smaller or bigger tree heights', function (t):
    def test_merge_trees(t):
        smaller = someData(10);
        tree1 = Rbush(4)
        tree1.load(data)
        tree1.load(smaller);

        tree2 = Rbush(4)
        tree2.load(smaller)
        tree2.load(data);

        t.assertEqual(tree1.toDict()['height'], tree2.toDict()['height']);

        sortedEqual(t, tree1.all(), data + smaller);
        sortedEqual(t, tree2.all(), data + smaller);


    #t('#search finds matching points in the tree given a bbox',
    def test_find_matching_bbox(t):

        tree = Rbush(4)
        tree.load(data);
        result = tree.search({'xmin': 40, 'ymin': 20, 'xmax': 80, 'ymax': 70});

        sortedEqual(t, result, list(map(arrToBBox,
        [
            [70,20,70,20],[75,25,75,25],[45,45,45,45],
            [50,50,50,50],[60,60,60,60],[70,70,70,70],
            [45,20,45,20],[45,70,45,70],[75,50,75,50],
            [50,25,50,25],[60,35,60,35],[70,45,70,45]
        ]
        )));


    #t('#collides returns true when search finds matching points',
    def test_find_collision(t):
        tree = Rbush(4)
        tree.load(data);
        result = tree.collides({'xmin': 40, 'ymin': 20, 'xmax': 80, 'ymax': 70});

        t.assertTrue(result);


    #t('#search returns an empty array if nothing found',
    def test_find_empty_result(t):
        tree = Rbush(4)
        tree.load(data)
        # result = tree.search([200, 200, 210, 210]);
        result = tree.search(arrToBBox([200, 200, 210, 210]));

        t.assertEqual(result, []);


    #t('#collides returns false if nothing found',
    def test_find_no_collision(t):
        tree = Rbush(4)
        tree.load(data)
        # result = tree.collides([200, 200, 210, 210]);
        result = tree.collides(arrToBBox([200, 200, 210, 210]));

        t.assertEqual(result, False);


    #t('#all returns all points in the tree',
    def test_retrieve_all(t):

        tree = Rbush(4)
        tree.load(data);
        result = tree.all();

        sortedEqual(t, result, data);
        sortedEqual(t, tree.search({'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}), data);


    #t('#toDict & #fromJSON exports and imports search tree in JSON format',
    def test_json_io(t):
        tree = Rbush(4)
        tree.load(data);
        tree2 = Rbush(4)
        tree2.fromJSON(tree.toJSON());

        items = tree.all()
        items2 = tree2.all()
        sortedEqual(t, items, items2);


    #t('#insert adds an item to an existing tree correctly',
    def test_insert_item(t):
        items = list( map( arrToBBox,
            [[0, 0, 0, 0],
             [1, 1, 1, 1],
             [2, 2, 2, 2],
             [3, 3, 3, 3],
             [1, 1, 2, 2]]
        ));

        tree = Rbush(4)
        tree.load(items[0:3]);

        tree.insert(items[3]);
        t.assertEqual(tree.toDict()['height'], 1);
        sortedEqual(t, tree.all(), items[0:4]);

        tree.insert(items[4]);
        t.assertEqual(tree.toDict()['height'], 2);
        sortedEqual(t, tree.all(), items);


    #t('#insert does nothing if given undefined',
    def test_insert_none(t):
        tree = Rbush()
        tree.load(data)
        tree2 = Rbush()
        tree2.load(data)

        tree2.insert()
        tree2.insert({})
        t.assertEqual(tree,tree2);


    #t('#insert forms a valid tree if items are inserted one by one',
    def test_insert_items(t):
        tree = Rbush(4);

        for i in range(0, len(data)):
            tree.insert(data[i]);

        tree2 = Rbush(4)
        tree2.load(data);

        t.assertTrue(tree.toDict()['height'] - tree2.toDict()['height'] <= 1);

        sortedEqual(t, tree.all(), tree2.all());


    # Insert vectors of coordinates
    def test_insert_numpy_vectors(t):
        numitems = 100
        import numpy as np
        xmin = np.random.randint(0,100,numitems)
        ymin = np.random.randint(0,100,numitems)
        xmax = xmin + np.random.randint(0,100,numitems)
        ymax = ymin + np.random.randint(0,100,numitems)

        tree = Rbush()
        tree.insert(xmin=xmin,ymin=ymin,xmax=xmax,ymax=ymax)
        len(tree.all())==numitems

    #t('#remove removes items correctly',
    def test_remove_items(t):
        tree = Rbush(4)
        tree.load(data);

        len_ = len(data);

        tree.remove(data[0]);
        tree.remove(data[1]);
        tree.remove(data[2]);

        tree.remove(data[len_ - 1]);
        tree.remove(data[len_ - 2]);
        tree.remove(data[len_ - 3]);

        sortedEqual(t, data[3 : len_-3], tree.all());


    #t('#remove does nothing if nothing found',
    def test_remove_nothing(t):
        tree = Rbush()
        tree.load(data)
        tree2 = Rbush()
        tree2.load(data)
        tree2.remove(arrToBBox([13, 13, 13, 13]))
        t.assertEqual(tree,tree2);


    #t('#remove does nothing if given undefined',
    # def remove_none(t):
    #     t.assertEqual(
    #         Rbush().load(data),
    #         Rbush().load(data).remove());
    #     t.end();


    #t('#remove accepts an equals function',
    # def test_remove_function(t):
    #     import json
    #     tree = Rbush(4)
    #     tree.load(data);
    #
    #     item = {'xmin': 20, 'ymin': 70, 'xmax': 20, 'ymax': 70, 'foo': 'bar'};
    #
    #     tree.insert(item);
    #     tree.remove(item, lambda a,b: a['foo'] == b['foo'])
    #
    #     sortedEqual(t, tree.all(), data);


    #t('#remove brings the tree to a clear state when removing everything one by one',
    def test_clean_tree(t):
        tree = Rbush(4)
        tree.load(data);

        # js = tree.toJSON()

        for i in range(0, len(data)):
            tree.remove(data[i]);
        # t.assertEqual(tree.toJSON(), js);
        t.assertEqual(tree.toDict(), Rbush(4).toDict());


    #t('#clear should clear all the data in the tree',
    def test_clear_tree(t):
        tree = Rbush(4)
        tree.load(data);
        tree.clear()

        t.assertEqual(
            tree.toDict(),
            Rbush(4).toDict());


    #t('should have chainable API',
    def test_chain(t):
        tree = Rbush()
        tree.load(data)
        tree.insert(data[0])
        try:
            tree.remove(data[0])
        except Exception as e:
            t.fail("Rbush.remove() raised exception {}".format(e))


if __name__ == '__main__':
    unittest.main()
