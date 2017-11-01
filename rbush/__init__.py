import math
from collections import namedtuple

from .quickselect import quickselect

# import sys
# INF = sys.maxsize
import numpy
INF = numpy.inf


from numba import njit
from numba import jitclass
from numba import deferred_type, optional
from numba import float64,int16,int32,char,boolean

stack_type = deferred_type()

node_type = deferred_type()
node_spec = [
    ('xmin',float64),
    ('ymin',float64),
    ('xmax',float64),
    ('ymax',float64),
    ('data',optional(int32)),
    ('leaf',optional(boolean)),
    ('height',optional(int16)),
    ('children',optional(stack_type))
]
@jitclass(node_spec)
class RBushNode(object):

    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.data = None
        self.leaf = None
        self.height = None
        self.children = None
node_type.define(RBushNode.class_type.instance_type)

stack_spec = [
    ('data', node_type),
    ('next', optional(stack_type))
]
@jitclass(stack_spec)
class Stack(object):
    def __init__(self, data, next):
        self.data = data
        self.next = next

stack_type.define(Stack.class_type.instance_type)

@njit
def push(stack, data):
    return Stack(data, stack)

def length(stack):
    i = 0
    while stack:
        stack = stack.next
        i+=1
    return i
# @njit
# def pop(stack):
#     return stack.next
# @njit
# def make_stack(data):
#     return push(None, data)

# from numba.types.containers import List
# from numba import void


# spec = [
#     ('xmin',float64),
#     ('ymin',float64),
#     ('xmax',float64),
#     ('ymax',float64),
#     ('data',int32),
# ]
# @jitclass(spec)
# class RBushItem(object):
#
#     def __init__(self, xmin, ymin, xmax, ymax, data):
#         self.xmin = xmin
#         self.ymin = ymin
#         self.xmax = xmax
#         self.ymax = ymax
#         self.data = data
#
#     # def __eq__(self, other):
#     #     return self.xmin == other.xmin \
#     #         and self.ymin == other.ymin \
#     #         and self.xmax == other.xmax \
#     #         and self.ymax == other.ymax
#
# item_type = deferred_type()
# item_type.define(RBushItem.class_type.instance_type)
#
# # RBushItemTuple = namedtuple('RBushItemTuple', ['xmin', 'ymin', 'xmax',
# #                                                'ymax', 'data'])
#
#
# spec = [
#     ('xmin',float64),
#     ('ymin',float64),
#     ('xmax',float64),
#     ('ymax',float64),
# ]
# @jitclass(spec)
# class RBushBox(object):
#
#     def __init__(self, xmin, ymin, xmax, ymax):
#         self.xmin = xmin
#         self.ymin = ymin
#         self.xmax = xmax
#         self.ymax = ymax
#
# box_type = deferred_type()
# box_type.define(RBushBox.class_type.instance_type)

# RBushBoxTuple = namedtuple('RBushTuple', ['xmin', 'ymin', 'xmax', 'ymax'])




RBushItem = RBushNode
RBushBox = RBushNode


def createNode(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
                    leaf=True, height=1, children=None):
    '''
    Create a node (leaf,parent or bbox)
    '''
    node = RBushNode(xmin, ymin, xmax, ymax)
    node.leaf = leaf
    node.height = height
    node.children = children
    return node


def createItem(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF, data=None):
    '''
    Create an item
    '''
    item = RBushItem(xmin, ymin, xmax, ymax)
    item.data = data
    return item

def createBox(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF):
    '''
    Create an item
    '''
    return RBushBox(xmin, ymin, xmax, ymax)


def toBBoxNode(item):
    '''
    Simply return 'item'
    '''
    if isinstance(item, dict):
        item = itemFromDict(item)
    return createBox(item.xmin, item.ymin, item.xmax, item.ymax)


def itemToDict(item):
    return dict(xmin=item.xmin,
                ymin=item.ymin,
                xmax=item.xmax,
                ymax=item.ymax,
                data=item.data)


def itemFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushItem), print(type(item))
        return item
    data = item.get('data', None)
    return createItem(item['xmin'], item['ymin'], item['xmax'], item['ymax'],
                      data)


def boxFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushBox), print(type(item))
        return item
    return createBox(item['xmin'], item['ymin'], item['xmax'], item['ymax'])


def nodeFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushNode), print(type(item))
        return item
    return createNode(item['xmin'], item['ymin'], item['xmax'], item['ymax'],
                      leaf=item.leaf,
                      height=item.height,
                      children=item.children)


def splice(list_, insert_position, remove_how_many, *items_to_insert):
    removed_items = []
    for i in range(remove_how_many):
        removed_items.append(list_.pop(insert_position))
    for item in items_to_insert[::-1]:
        list_.insert(insert_position, item)
    return removed_items


def findItem(item, items, equalsFn=None):
    item = itemFromDict(item)
    if not equalsFn:
        return items.index(item) if item in items else None
    for i in range(0, len(items)):
        if equalsFn(item, items[i]):
            return i
    return None


# TODO: EASY JIT
def extend(a, b):
    """Return 'a' box enlarged by 'b'"""
    a.xmin = min(a.xmin, b.xmin)
    a.ymin = min(a.ymin, b.ymin)
    a.xmax = max(a.xmax, b.xmax)
    a.ymax = max(a.ymax, b.ymax)
    return a

def compareNodexmin(a):
    return a.xmin  # - b.xmin


def compareNodeymin(a):
    return a.ymin  # - b.ymin


def bboxArea(a):
    return (a.xmax - a.xmin) * (a.ymax - a.ymin)

def bboxMargin(a):
    return (a.xmax - a.xmin) + (a.ymax - a.ymin)


def enlargedArea(a, b):
    sect1 = max(b.xmax, a.xmax) - min(b.xmin, a.xmin)
    sect2 = max(b.ymax, a.ymax) - min(b.ymin, a.ymin)
    return sect1 * sect2


def intersectionArea(a, b):
    xmin = max(a.xmin, b.xmin)
    ymin = max(a.ymin, b.ymin)
    xmax = min(a.xmax, b.ymax)
    ymax = min(a.ymax, b.ymax)
    return max(0, xmax - xmin) * max(0, ymax - ymin)


def contains(a, b):
    a_lower_b = a.xmin <= b.xmin and a.ymin <= b.ymin
    a_upper_b = b.xmax <= a.xmax and b.ymax <= a.ymax
    return a_lower_b and a_upper_b


def intersects(a, b):
    b_lower_a = b.xmin <= a.xmax and b.ymin <= a.ymax
    b_upper_a = b.xmax >= a.xmin and b.ymax >= a.ymin
    return b_lower_a and b_upper_a


def multiSelect(items, left, right, n, compare):
    stack = [left, right]
    mid = None
    while len(stack):
        right = stack.pop()
        left = stack.pop()
        if (right - left) <= n:
            continue
        mid = left + math.ceil((right - left) / n / 2) * n
        quickselect(items, mid, left, right, compare)
        stack.extend([left, mid, mid, right])


def chooseSubtree(bbox, node, level, path):
    '''
    Return the node closer to 'bbox'

    Traverse the subtree searching for the tightest path,
    the node at the end, closest to bbox is returned

    '''
    while True:
        print(node)
        path.append(node)

        print(node.leaf,path,level)
        if node.leaf or (len(path)-1 == level):
            break

        minEnlargement = INF
        minArea = INF

        targetNode = None
        for child in node.children:
            print(child)
        # while part is not None:
        #     child = part.data
            area = bboxArea(child)
            enlargement = enlargedArea(bbox, child) - area

            # choose entry with the least area enlargement
            if (enlargement < minEnlargement):
                minEnlargement = enlargement
                minArea = area if area < minArea else minArea
                targetNode = child
            else:
                if (enlargement == minEnlargement):
                    # otherwise choose one with the smallest area
                    if (area < minArea):
                        minArea = area
                        targetNode = child
            # part = part.next

        node = targetNode or node.children[0]

    # NOTE: 'node' is returned, 'path' was modified (i.e, filled)
    return node


def adjustParentBBoxes(bbox, path, level):
    # adjust bboxes along the given tree path
    for i in range(level, -1, -1):
        extend(path[i], bbox)


class Rbush(object):

    _defaultMaxEntries = 9

    def __init__(self, maxEntries=None, axes_format=None):
        '''max entries in a node is 9 by default;
        min node fill is 40% for best performance'''

        self._maxEntries = max(4, maxEntries or self._defaultMaxEntries)
        self._minEntries = max(2, math.ceil(self._maxEntries * 0.4))
        # self._initFormat(axes_format)
        self.data = createNode()

    def __eq__(self, other):
        return self.toJSON() == other.toJSON()

    def __str__(self):
        return self.toJSON()

    def copy(self):
        new = Rbush(self._maxEntries, self._format)
        new.fromJSON(self.toJSON())
        assert new == self
        return new

    def insert(self, item=None, xmin=None, ymin=None, xmax=None, ymax=None):
        '''Insert an item'''
        if not any([xmin is None, ymin is None, xmax is None, ymax is None]):

            try:
                len(xmin)
                len(ymin)
                len(xmax)
                len(ymax)
            except TypeError as e:
                # not iterable
                xmin = [xmin]
                ymin = [ymin]
                xmax = [xmax]
                ymax = [ymax]

            if not len(xmin) == len(ymin) == len(xmax) == len(ymax):
                msg = ("Error: Arguments 'xmin','ymin',"
                       "'xmax','ymax' have different lengths")
                print(msg)
                return self

            items = []
            for i in range(len(xmin)):
                items.append(createItem(xmin[i], ymin[i], xmax[i], ymax[i], None))
            self.load(items)

        if item:
            item = itemFromDict(item)
            self._insert(item, self.data.height - 1)

        return self

    def _insert(self, item, level, isNode=False):
        #
        root = self.data
        bbox = self.toBBox(item) if not isNode else item

        insertPath = []

        # find the best node for accommodating the item,
        # saving all nodes along the path too
        node = chooseSubtree(bbox, root, level, insertPath)

        # put the item into the node
        node.children = push(node.children,item)
        extend(node, bbox)

        # split on node overflow; propagate upwards if necessary
        while level >= 0:
            if length(insertPath[level].children) > self._maxEntries:
                self._split(insertPath, level)
                level = level - 1
            else:
                break

        # adjust bboxes along the insertion path
        adjustParentBBoxes(bbox, insertPath, level)

    # split overflowed node into two def _split(self, insertPath, level):
    def _split(self, insertPath, level):

        m = self._minEntries
        node = insertPath[level]

        self.chooseSplitAxis(node, m)

        splitIndex = self.chooseSplitIndex(node, m)
        # If an optimal index was not found, split at the minEntries
        splitIndex = splitIndex or m

        numChildren = len(node.children) - splitIndex
        adopted = splice(node.children, splitIndex, numChildren)
        newNode = createNode(height=node.height,leaf=node.leaf,children=adopted)

        # Update the sizes (limits) of each box
        self.calcBBox(node)
        self.calcBBox(newNode)

        if level:
            insertPath[level-1].children.append(newNode)
        else:
            self._splitRoot(node, newNode)

    def chooseSplitAxis(self, node, minEntries):
        '''
        Sort node's children by the best axis for split

        The best axis is defined based on a estimate of
        "density", the more compact axis goes split.
        '''
        # m = self._minEntries
        # comparexmin = compareNodexmin
        # compareymin = compareNodeymin
        xMargin = self.allDistMargin(node, self.comparexmin, minEntries)
        yMargin = self.allDistMargin(node, self.compareymin, minEntries)

        # if total distributions margin value is minimal for x, sort by xmin,
        # otherwise it's already sorted by ymin
        if (xMargin < yMargin):
            node.children.sort(key=self.comparexmin)

    # total margin of all possible split distributions
    # where each node is at least m full
    def allDistMargin(self, node, compare, minEntries):
        '''
        Return the size of all combinations of bounding-box to split
        '''
        M = len(node.children)
        m = minEntries

        # The sorting of (children) nodes according to an axis,
        # "compare-X/Y", guides the search for where to split
        node.children.sort(key=compare)

        leftBBox = self.distBBox(node, 0, m)
        rightBBox = self.distBBox(node, M - m, M)
        margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)

        for i in range(m, M - m):
            child = node.children[i]
            extend(leftBBox, child)
            margin = margin + bboxMargin(leftBBox)

        for i in range(M-m-1, m-1, -1):
            child = node.children[i]
            extend(rightBBox, child)
            margin = margin + bboxMargin(rightBBox)

        return margin

    def chooseSplitIndex(self, node, minEntries):
        '''
        Return the index (children) where to split

        Split position tries to minimize (primarily) the boxes overlap
        and, secondly, the area cover by each combination of boxes.
        '''
        M = len(node.children)
        m = minEntries

        minArea = INF
        minOverlap = INF

        index = None
        for i in range(m, M - m + 1):
            bbox1 = self.distBBox(node, 0, i)
            bbox2 = self.distBBox(node, i, M)

            overlap = intersectionArea(bbox1, bbox2)
            area = bboxArea(bbox1) + bboxArea(bbox2)

            # choose distribution with minimum overlap
            if (overlap < minOverlap):
                minOverlap = overlap
                index = i
                minArea = area if area < minArea else minArea

            else:
                if (overlap == minOverlap):
                    # otherwise choose distribution with minimum area
                    if (area < minArea):
                        minArea = area
                        index = i

        return index

    def _splitRoot(self, node, newNode):
        # split root node
        newRoot = createNode(leaf = False,
                             height = node.height + 1,
                             children=[node, newNode])
        self.calcBBox(newRoot)
        self.data = newRoot

    def clear(self):
        self.data = createNode()

    def all(self):
        all_ = self._all(self.data, [])
        items = []
        for item in all_:
            items.append(itemToDict(item))
        return items

    def _all(self, node, result):
        nodesToSearch = []
        while node:
            l = []
            child = node.children
            while child:
                l.append(child.data)
                child = child.next
            if node.leaf:
                result.extend(l)
            else:
                nodesToSearch.extend(l)
            node = nodesToSearch.pop() if len(nodesToSearch) else None
        return result

    def search(self, bbox):
        node = self.data
        result = []

        if isinstance(bbox, dict):
            bbox = boxFromDict(bbox)

        if not intersects(bbox, node):
            return result

        nodesToSearch = []
        while node:
            len_ = len(node.children)
            for i in range(0, len_):
                child = node.children[i]
                childBBox = self.toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf:
                        result.append(child)
                    elif contains(bbox, childBBox):
                        self._all(child, result)
                    else:
                        nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        items = []
        for item in result:
            items.append(itemToDict(item))
        return items

    def collides(self, bbox):
        node = self.data

        if isinstance(bbox, dict):
            bbox = boxFromDict(bbox)

        if not intersects(bbox, node):
            return False

        nodesToSearch = []
        while node:
            len_ = len(node.children)
            for i in range(0, len_):
                child = node.children[i]
                childBBox = self.toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf or contains(bbox, childBBox):
                        return True
                    nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        return False

    def load(self, data):
        # If data is empty or None, do nothing
        if not (data and len(data)):
            return self

        # If data is small ( < minimum entries), just insert one-by-one
        len_ = len(data)
        if (len_ < self._minEntries):
            for i in range(0, len_):
                self.insert(data[i])
            return self

        items = []
        for item in data:
            items.append(itemFromDict(item))
        data = items

        # recursively build the tree with the given data
        # from scratch using OMT algorithm
        node = self._build(data, 0, len(data) - 1, 0)

        if not len(self.data.children):
            # save as is if tree is empty
            self.data = node
        elif (self.data.height == node.height):
            # split root if trees have the same height
            self._splitRoot(self.data, node)
        else:
            if (self.data.height < node.height):
                # swap trees if inserted one is bigger
                tmpNode = self.data
                self.data = node
                node = tmpNode
            # insert the small tree into the large tree at appropriate level
            self._insert(node, self.data.height - node.height - 1, True)
        return self

    def remove(self, item, equalsFn=None):
        if not item:
            return self

        node = self.data
        bbox = self.toBBox(item)
        path = []
        indexes = []
        goingUp = False
        parent = None
        i = None

        # depth-first iterative tree traversal
        while node or len(path):

            if not node:  # go up
                node = path.pop()
                parent = path[len(path) - 1] if len(path) else None
                i = indexes.pop() if len(indexes) else None
                goingUp = True

            if node.leaf:  # check current node
                index = findItem(item, node.children, equalsFn)
                if index is not None:
                    # item found, remove the item and condense tree upwards
                    splice(node.children, index, 1)
                    path.append(node)
                    self._condense(path)
                    return self

            # go down
            if not goingUp and not node.leaf and contains(node, bbox):
                path.append(node)
                if i is not None:
                    indexes.append(i)
                i = 0
                parent = node
                node = node.children[0]

            elif parent:  # go right
                i += 1
                try:
                    node = parent.children[i]
                except IndexError as e:
                    node = None
                goingUp = False

            else:
                node = None  # nothing found
        return self

    def toBBox(self, item):
        return toBBoxNode(item)

    def calcBBox(self, node):
        """Update node sizes after its children"""
        return self.distBBox(node, 0, len(node.children), node)

    def distBBox(self, node, left_child, right_child, destNode=None):
        """Return a node enlarged by all children between left/right"""
        destNode = createNode() if destNode is None else destNode
        for i in range(left_child, right_child):
            child = node.children[i]
            extend(destNode, self.toBBox(child) if node.leaf else child)
        return destNode

    def comparexmin(self, a):
        return compareNodexmin(a)

    def compareymin(self, a):
        return compareNodeymin(a)

    def toDict(self):
        return nodeToJSON(self.data)

    def toJSON(self):
        import json
        return json.dumps(self.toDict())

    def fromDict(self, dict):
        return nodeFromJSON(dict)

    def fromJSON(self, data):
        import json
        self.data = self.fromDict(json.loads(data))

    def _build(self, items, left, right, height):
        N = right - left + 1
        M = self._maxEntries
        node = None

        if N <= M:
            # reached leaf level; return leaf
            node = createNode(children=items[left: right + 1])
            self.calcBBox(node)
            return node

        if not height:
            # target height of the bulk-loaded tree
            height = math.ceil(math.log(N) / math.log(M))

            # target number of root entries to maximize storage utilization
            M = math.ceil(N / math.pow(M, height - 1))

        node = createNode()
        node.leaf = False
        node.height = height

        # split the items into M mostly square tiles
        N2 = math.ceil(N / M)
        N1 = N2 * math.ceil(math.sqrt(M))

        multiSelect(items, left, right, N1, self.comparexmin)

        for i in range(left, right+1, N1):
            right2 = min(i + N1 - 1, right)
            multiSelect(items, i, right2, N2, self.compareymin)
            for j in range(i, right2+1, N2):
                right3 = min(j + N2 - 1, right2)
                # pack each entry recursively
                node.children.append(self._build(items, j, right3, height - 1))
        self.calcBBox(node)

        return node

    def _condense(self, path):
        # go through the path, removing empty nodes and updating bboxes
        siblings = None
        for i in range(len(path)-1, -1, -1):
            if len(path[i].children) == 0:
                if (i > 0):
                    siblings = path[i - 1].children
                    splice(siblings, siblings.index(path[i]), 1)
                else:
                    self.clear()
            else:
                self.calcBBox(path[i])

    def _initFormat(self, format_):
        # data format (xmin, ymin, xmax, ymax accessors)
        self._format = format_
        if not format_:
            return None

        self.comparexmin = lambda a: a[format_[0]]
        self.compareymin = lambda a: a[format_[1]]

        self.toBBox = lambda a: RBushBox(a[format_[0]], a[format_[1]],
                                         a[format_[2]], a[format_[3]])




def nodeToJSON(node):
    # content = { k:str(v) for k,v in vars(node).items() }
    content = dict( xmin=node.xmin,
                    ymin=node.ymin,
                    xmax=node.xmax,
                    ymax=node.ymax )
    if node.children is not None:
        content['leaf'] = node.leaf
        content['height'] = node.height
        children = []
        child = node.children
        while child:
            children.append(nodeToJSON(child.data))
            child = child.next
        content['children'] = children
    else:
        content['data'] = node.data
    return content

def nodeFromJSON(dict_):
    # content = { k:str(v) for k,v in vars(node).items() }
    try:
        children = []
        for child in dict_['children']:
            children.append(nodeFromJSON(child))
        node = createNode(dict_['xmin'],
                          dict_['ymin'],
                          dict_['xmax'],
                          dict_['ymax'],
                          dict_['leaf'],
                          dict_['height'],
                          children)
    except Exception as e:
        node = createItem(dict_['xmin'],
                          dict_['ymin'],
                          dict_['xmax'],
                          dict_['ymax'],
                          dict_.get('data', None))
    return node
