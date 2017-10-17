
#/*eslint key-spacing: 0, comma-spacing: 0 */

import unittest

def sortedEqual(t, a, b, compare):
    compare = compare || defaultCompare;
    # t.same(a.slice().sort(compare), b.slice().sort(compare));
    t.equal(a.slice().sort(compare), b.slice().sort(compare));


def defaultCompare(a, b):
    return (a.minX - b.minX) || (a.minY - b.minY) || (a.maxX - b.maxX) || (a.maxY - b.maxY);


def someData(n):
    data = [];
    for i in range(0, n):
        data.append({minX: i, minY: i, maxX: i, maxY: i});
    return data;


def arrToBBox(arr):
    return {
        minX: arr[0],
        minY: arr[1],
        maxX: arr[2],
        maxY: arr[3]
    };


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

# t('constructor accepts a format argument to customize the data format',
def format_argument(t):
    tree = rbush(4, ['.minLng', '.minLat', '.maxLng', '.maxLat']);
    t.equal(tree.toBBox({minLng: 1, minLat: 2, maxLng: 3, maxLat: 4}),
                        {minX: 1, minY: 2, maxX: 3, maxY: 4});
    t.end();

# t('constructor uses 9 max entries by default',
def default_maxEntries(t):
    tree = Rbush()
    tree.load(someData(9));
    t.equal(tree.toJSON()['height'], 1);

    tree2 = Rbush()
    tree2.load(someData(10));
    t.equal(tree2.toJSON()['height'], 2);
    t.end();

# t('#toBBox, #compareMinX, #compareMinY can be overriden to allow custom data structures',
def custom_dataStructures(t):
    tree = rbush(4);
    tree.toBBox = lambda item: {minX: item.minLng,
                                minY: item.minLat,
                                maxX: item.maxLng,
                                maxY: item.maxLat };
    tree.compareMinX = lambda (a, b): a.minLng - b.minLng;
    tree.compareMinY = lambda (a, b): a.minLat - b.minLat;

    data = [
        {minLng: -115, minLat:  45, maxLng: -105, maxLat:  55},
        {minLng:  105, minLat:  45, maxLng:  115, maxLat:  55},
        {minLng:  105, minLat: -55, maxLng:  115, maxLat: -45},
        {minLng: -115, minLat: -55, maxLng: -105, maxLat: -45}
    ];

    tree.load(data);

    def byLngLat(a, b):
        return a.minLng - b.minLng || a.minLat - b.minLat;

    sortedEqual(t, tree.search({minX: -180, minY: -90, maxX: 180, maxY: 90}), [
        {minLng: -115, minLat:  45, maxLng: -105, maxLat:  55},
        {minLng:  105, minLat:  45, maxLng:  115, maxLat:  55},
        {minLng:  105, minLat: -55, maxLng:  115, maxLat: -45},
        {minLng: -115, minLat: -55, maxLng: -105, maxLat: -45}
    ], byLngLat);

    sortedEqual(t, tree.search({minX: -180, minY: -90, maxX: 0, maxY: 90}), [
        {minLng: -115, minLat:  45, maxLng: -105, maxLat:  55},
        {minLng: -115, minLat: -55, maxLng: -105, maxLat: -45}
    ], byLngLat);

    sortedEqual(t, tree.search({minX: 0, minY: -90, maxX: 180, maxY: 90}), [
        {minLng: 105, minLat:  45, maxLng: 115, maxLat:  55},
        {minLng: 105, minLat: -55, maxLng: 115, maxLat: -45}
    ], byLngLat);

    sortedEqual(t, tree.search({minX: -180, minY: 0, maxX: 180, maxY: 90}), [
        {minLng: -115, minLat: 45, maxLng: -105, maxLat: 55},
        {minLng:  105, minLat: 45, maxLng:  115, maxLat: 55}
    ], byLngLat);

    sortedEqual(t, tree.search({minX: -180, minY: -90, maxX: 180, maxY: 0}), [
        {minLng:  105, minLat: -55, maxLng:  115, maxLat: -45},
        {minLng: -115, minLat: -55, maxLng: -105, maxLat: -45}
    ], byLngLat);

    t.end();


# t('#load bulk-loads the given data given max node entries and forms a proper search tree',
def dataLoad_sort(t):
    tree = rbush(4)
    tree.load(data);
    sortedEqual(t, tree.all(), data);
    t.end();

# t('#load uses standard insertion when given a low number of items',
def dataLoad_fewMethod(t):
    tree = rbush(8)
    tree.load(data)
    tree.load(data[0, 3]);

    tree2 = rbush(8)
    tree2.load(data)
    tree2.insert(data[0])
    tree2.insert(data[1])
    tree2.insert(data[2]);

    t.equal(tree.toJSON(), tree2.toJSON());
    t.end();

# t('#load does nothing if loading empty data',
def data_load_empty(t):
    tree = rbush()
    tree.load([]);
    t.equal(tree.toJSON(), Rbush().toJSON());
    t.end();

# t('#load handles the insertion of maxEntries + 2 empty bboxes',
def data_load_empty_maxEntries(t):
    tree = rbush(4)
    tree.load(emptyData);

    t.equal(tree.toJSON().height, 2);
    sortedEqual(t, tree.all(), emptyData);

    t.end();

# t('#insert handles the insertion of maxEntries + 2 empty bboxes',
def data_insert_empty_maxEntries(t):
    tree = rbush(4);

    for datum in emptyData:
        tree.insert(datum);

    t.equal(tree.toJSON().height, 2);
    sortedEqual(t, tree.all(), emptyData);

    t.end();

# t('#load properly splits tree root when merging trees of the same height',
def split_root_on_merge(t):
    tree = rbush(4)
    tree.load(data)
    tree.load(data);

    t.equal(tree.toJSON().height, 4);
    sortedEqual(t, tree.all(), data.extend(data));

    t.end();

# t('#load properly merges data of smaller or bigger tree heights', function (t):
def merge_trees(t):
    smaller = someData(10);

    tree1 = rbush(4)
    tree1.load(data)
    tree1.load(smaller);

    tree2 = rbush(4)
    tree2    .load(smaller)
    tree2    .load(data);

    t.equal(tree1.toJSON().height, tree2.toJSON().height);

    sortedEqual(t, tree1.all(), data.concat(smaller));
    sortedEqual(t, tree2.all(), data.concat(smaller));

    t.end();
});

#t('#search finds matching points in the tree given a bbox',
def find_matching_bbox(t):

    tree = rbush(4).load(data);
    result = tree.search({minX: 40, minY: 20, maxX: 80, maxY: 70});

    sortedEqual(t, result, list(map(arrToBBox,
    [
        [70,20,70,20],[75,25,75,25],[45,45,45,45],
        [50,50,50,50],[60,60,60,60],[70,70,70,70],
        [45,20,45,20],[45,70,45,70],[75,50,75,50],
        [50,25,50,25],[60,35,60,35],[70,45,70,45]
    ]
    )));

    t.end();


#t('#collides returns true when search finds matching points',
def find_collision(t):
    tree = rbush(4).load(data);
    result = tree.collides({minX: 40, minY: 20, maxX: 80, maxY: 70});

    t.true(result);

    t.end();


#t('#search returns an empty array if nothing found',
def find_empty_result(t):
    result = rbush(4).load(data).search([200, 200, 210, 210]);

    t.same(result, []);
    t.end();


#t('#collides returns false if nothing found',
def find_no_collision(t):
    result = rbush(4).load(data).collides([200, 200, 210, 210]);

    t.same(result, false);
    t.end();


#t('#all returns all points in the tree',
def retrieve_all(t):

    tree = rbush(4).load(data);
    result = tree.all();

    sortedEqual(t, result, data);
    sortedEqual(t, tree.search({minX: 0, minY: 0, maxX: 100, maxY: 100}), data);

    t.end();

#t('#toJSON & #fromJSON exports and imports search tree in JSON format',
def json_io(t):
    tree = rbush(4).load(data);
    tree2 = rbush(4).fromJSON(tree.data);

    sortedEqual(t, tree.all(), tree2.all());
    t.end();


#t('#insert adds an item to an existing tree correctly',
def insert_item(t):
    items = list( map( arrToBBox,
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [2, 2, 2, 2],
         [3, 3, 3, 3],
         [1, 1, 2, 2]]
    ));

    tree = rbush(4).load(items.slice(0, 3));

    tree.insert(items[3]);
    t.equal(tree.toJSON().height, 1);
    sortedEqual(t, tree.all(), items.slice(0, 4));

    tree.insert(items[4]);
    t.equal(tree.toJSON().height, 2);
    sortedEqual(t, tree.all(), items);

    t.end();


#t('#insert does nothing if given undefined',
def insert_none(t):
    t.equal(
        rbush().load(data),
        rbush().load(data).insert());
    t.end();
});

#t('#insert forms a valid tree if items are inserted one by one',
def insert_items(t):
    tree = rbush(4);

    for i in range(0, len(data)):
        tree.insert(data[i]);

    tree2 = rbush(4).load(data);

    t.ok(tree.toJSON()['height'] - tree2.toJSON()['height'] <= 1);

    sortedEqual(t, tree.all(), tree2.all());
    t.end();


#t('#remove removes items correctly',
def remove_items(t):
    tree = rbush(4).load(data);

    len_ = len(data);

    tree.remove(data[0]);
    tree.remove(data[1]);
    tree.remove(data[2]);

    tree.remove(data[len_ - 1]);
    tree.remove(data[len_ - 2]);
    tree.remove(data[len_ - 3]);

    sortedEqual(t, data[3 : len_-3], tree.all());
    t.end();


#t('#remove does nothing if nothing found',
def remove_nothing(t):
    t.same(
        rbush().load(data),
        rbush().load(data).remove([13, 13, 13, 13]));
    t.end();


#t('#remove does nothing if given undefined',
# def remove_none(t):
#     t.same(
#         rbush().load(data),
#         rbush().load(data).remove());
#     t.end();


#t('#remove brings the tree to a clear state when removing everything one by one',
def clean_tree(t):
    tree = rbush(4).load(data);

    for i in range(0, len(data)):
        tree.remove(data[i]);

    t.same(tree.toJSON(), rbush(4).toJSON());
    t.end();


#t('#remove accepts an equals function',
def remove_function(t):
    tree = rbush(4).load(data);

    item = {minX: 20, minY: 70, maxX: 20, maxY: 70, foo: 'bar'};

    tree.insert(item);
    tree.remove(JSON.parse(JSON.stringify(item)),
        lambda (a, b): a.foo == b.foo;

    sortedEqual(t, tree.all(), data);
    t.end();


#t('#clear should clear all the data in the tree',
def clear_tree(t):
    t.same(
        rbush(4).load(data).clear().toJSON(),
        rbush(4).toJSON());
    t.end();


#t('should have chainable API',
def chain(t):
    t.doesNotThrow( rbush()
                    .load(data)
                    .insert(data[0])
                    .remove(data[0]);
    );
    t.end();
