from __future__ import print_function, absolute_import

from .quickselect import quickselect

import math

from numba import njit, jit
from numba import jitclass
from numba import deferred_type, optional
from numba import float64, int16, int32, boolean

import numpy as np
INF = np.inf

stack_type = deferred_type()

node_type = deferred_type()
node_spec = [
    ('xmin', float64),
    ('ymin', float64),
    ('xmax', float64),
    ('ymax', float64),
    ('data', optional(int32)),
    ('leaf', optional(boolean)),
    ('height', optional(int16)),
    ('children', optional(stack_type))
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


# @profile
# @njit
def insert(stack, index, item):
    child = stack
    cursor = None
    i = 0
    while child is not None:
        if index == i:
            break
        i = i+1
        cursor = child
        child = child.next
    # assert child is not None, "Error: index {:d} out of range".format(index)
    new = push(child, item)
    cursor.next = new
    return stack


# @profile
# @jit
def remove(stack, index):
    if index >= length(stack):
        return stack
    if index == 0:
        return stack.next
    child = stack
    i = 0
    while child is not None:
        if index == i:
            break
        i = i+1
        prev = child
        child = child.next
    prev.next = child.next
    # ? del child ?
    return stack


@jit
def length(stack):
    i = 0
    while stack is not None:
        stack = stack.next
        i += 1
    return i


def default_compare(a):
    return a.xmin


# @profile
# @jit
def sort(stack, compare=None):
    compare = compare or default_compare
    len_ = length(stack)
    if len_ == 1:
        return stack
    halfsize = int(len_/2)
    odd = int(len_ % 2)
    _, right = splice(stack, 0, halfsize)
    _, left = splice(stack, halfsize, halfsize+odd)
    left = sort(left)
    right = sort(right)
    out = None
    i = 0
    j = 0
    while i < length(left) and j < length(right):
        iv = get(left, i)
        jv = get(right, j)
        if compare(iv) <= compare(jv):
            out = push(out, iv)
            i += 1
        else:
            out = push(out, jv)
            j += 1
    while i < length(left):
        iv = get(left, i)
        out = push(out, iv)
        i += 1
    while j < length(right):
        jv = get(right, j)
        out = push(out, jv)
        j += 1
    return out


# @profile
@njit
def get(stack, index):
    i = 0
    child = stack
    while child is not None:
        if index == i:
            break
        i = i+1
        child = child.next
    # assert child is not None, "Error: index {:d} out of range".format(index)
    return child.data


# @profile
@njit
def index(stack, item):
    child = stack
    i = 0
    while child is not None:
        data = child.data
        if item.xmin == data.xmin and item.ymin == data.ymin \
           and item.xmax == data.xmax and item.ymax == data.ymax:
            return i
        i += 1
        child = child.next
    return None


# @profile
# @jit
def createNode(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
               leaf=True, height=1, children=None):
    '''
    Create a node (leaf,parent or bbox)
    '''
    node = RBushNode(xmin, ymin, xmax, ymax)
    node.leaf = leaf
    node.height = height
    if children:
        for child in children:
            node.children = push(node.children, child)
    else:
        node.children = None
    return node


# @profile
# @njit
def createItem(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF, data=None):
    '''
    Create an item
    '''
    item = RBushNode(xmin, ymin, xmax, ymax)
    item.data = data
    return item


# @profile
# @njit
def createBox(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF):
    '''
    Create an item
    '''
    return RBushNode(xmin, ymin, xmax, ymax)


# @profile
# @jit
def toBBoxNode(item):
    '''
    Simply return 'item'
    '''
    if isinstance(item, dict):
        item = itemFromDict(item)
    return createBox(item.xmin, item.ymin, item.xmax, item.ymax)


# @profile
# @jit
def itemToDict(item):
    return dict(xmin=item.xmin,
                ymin=item.ymin,
                xmax=item.xmax,
                ymax=item.ymax,
                data=item.data)


# @profile
# @jit
def itemFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushNode), print(type(item))
        return item
    data = item.get('data', None)
    return createItem(item['xmin'], item['ymin'], item['xmax'], item['ymax'],
                      data)


# @profile
# @jit
def boxFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushNode), print(type(item))
        return item
    return createBox(item['xmin'], item['ymin'], item['xmax'], item['ymax'])


# @profile
# @njit
def nodeFromDict(item):
    if not isinstance(item, dict):
        assert isinstance(item, RBushNode), print(type(item))
        return item
    return createNode(item['xmin'], item['ymin'], item['xmax'], item['ymax'],
                      leaf=item.leaf,
                      height=item.height,
                      children=item.children)


# @profile
# @jit
def splice(list_, insert_position, remove_how_many, *items_to_insert):
    removed_items = []
    for i in range(remove_how_many):
        item = get(list_, insert_position)
        list_ = remove(list_, insert_position)
        removed_items.append(item)
    for item in items_to_insert[::-1]:
        list_ = insert(list_, insert_position, item)
    return removed_items, list_


# @profile
@jit
def findItem(item, items, equalsFn=None):
    item = itemFromDict(item)
    if not equalsFn:
        return index(items, item)
    for i in range(0, length(items)):
        if equalsFn(item, get(items, i)):
            return i
    return None


# @profile
@njit
def extend(a, b):
    """Return 'a' box enlarged by 'b'"""
    a.xmin = min(a.xmin, b.xmin)
    a.ymin = min(a.ymin, b.ymin)
    a.xmax = max(a.xmax, b.xmax)
    a.ymax = max(a.ymax, b.ymax)
    return a


# @profile
def compareNodexmin(a):
    return a.xmin  # - b.xmin


# @profile
def compareNodeymin(a):
    return a.ymin  # - b.ymin


# @profile
@njit
def bboxArea(a):
    return (a.xmax - a.xmin) * (a.ymax - a.ymin)


# @profile
@njit
def bboxMargin(a):
    return (a.xmax - a.xmin) + (a.ymax - a.ymin)


# @profile
@njit
def enlargedArea(a, b):
    sect1 = max(b.xmax, a.xmax) - min(b.xmin, a.xmin)
    sect2 = max(b.ymax, a.ymax) - min(b.ymin, a.ymin)
    return sect1 * sect2


# @profile
@njit
def intersectionArea(a, b):
    xmin = max(a.xmin, b.xmin)
    ymin = max(a.ymin, b.ymin)
    xmax = min(a.xmax, b.ymax)
    ymax = min(a.ymax, b.ymax)
    return max(0, xmax - xmin) * max(0, ymax - ymin)


# @profile
@njit
def contains(a, b):
    a_lower_b = a.xmin <= b.xmin and a.ymin <= b.ymin
    a_upper_b = b.xmax <= a.xmax and b.ymax <= a.ymax
    return a_lower_b and a_upper_b


# @profile
@njit
def intersects(a, b):
    b_lower_a = b.xmin <= a.xmax and b.ymin <= a.ymax
    b_upper_a = b.xmax >= a.xmin and b.ymax >= a.ymin
    return b_lower_a and b_upper_a


# @profile
@jit
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


# @profile
# @jit
def chooseSubtree(bbox, node, level, path):
    '''
    Return the node closer to 'bbox'

    Traverse the subtree searching for the tightest path,
    the node at the end, closest to bbox is returned

    '''
    while True:
        path.append(node)

        if node.leaf or (len(path)-1 == level):
            break

        minEnlargement = INF
        minArea = INF

        targetNode = None
        child = node.children
        while child is not None:
            area = bboxArea(child.data)
            enlargement = enlargedArea(bbox, child.data) - area

            # choose entry with the least area enlargement
            if (enlargement < minEnlargement):
                minEnlargement = enlargement
                minArea = area if area < minArea else minArea
                targetNode = child.data
            else:
                if (enlargement == minEnlargement):
                    # otherwise choose one with the smallest area
                    if (area < minArea):
                        minArea = area
                        targetNode = child.data
            child = child.next

        node = targetNode or node.children.data

    # NOTE: 'node' is returned, 'path' was modified (i.e, filled)
    return node


# @profile
# @njit
def adjustParentBBoxes(bbox, path, level):
    # adjust bboxes along the given tree path
    for i in range(level, -1, -1):
        extend(path[i], bbox)


# @profile
# @jit
def nodeToDict(node):
    # content = { k:str(v) for k,v in vars(node).items() }
    content = dict(xmin=node.xmin,
                   ymin=node.ymin,
                   xmax=node.xmax,
                   ymax=node.ymax)
    if node.children is not None:
        content['leaf'] = node.leaf
        content['height'] = node.height
        children = []
        child = node.children
        while child is not None:
            children.append(nodeToDict(child.data))
            child = child.next
        content['children'] = children
    else:
        content['data'] = node.data
    return content


# @profile
# @jit
def nodeToJSON(node, indent=None):
    cont = nodeToDict(node)
    import json
    return json.dumps(cont, indent=indent)


# @profile
# @jit
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


class RBush(object):

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
        new = RBush(self._maxEntries, self._format)
        new.fromJSON(self.toJSON())
        assert new == self
        return new

    @property
    def xmin(self):
        return self.data.xmin

    @property
    def ymin(self):
        return self.data.ymin

    @property
    def xmax(self):
        return self.data.xmax

    @property
    def ymax(self):
        return self.data.ymax

    @property
    def height(self):
        return self.data.height

    # @njit
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
                items.append(createItem(xmin[i], ymin[i],
                                        xmax[i], ymax[i], None))
            self.load(items)

        if item:
            item = itemFromDict(item)
            self._insert(item, self.data.height - 1)

        return self

    # @njit
    def _insert(self, item, level, isNode=False):
        #
        root = self.data
        bbox = self.toBBox(item) if not isNode else item

        insertPath = []

        # find the best node for accommodating the item,
        # saving all nodes along the path too
        node = chooseSubtree(bbox, root, level, insertPath)

        # put the item into the node
        node.children = push(node.children, item)
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
        numChildren = length(node.children) - splitIndex
        adopted, node.children = splice(node.children, splitIndex, numChildren)
        newNode = createNode(height=node.height,
                             leaf=node.leaf,
                             children=adopted)
        # Update the sizes (limits) of each box
        self.calcBBox(node)
        self.calcBBox(newNode)

        if level:
            node = insertPath[level-1]
            node.children = push(node.children, newNode)
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
            node.children = sort(node.children, compare=self.comparexmin)

    # total margin of all possible split distributions
    # where each node is at least m full
    def allDistMargin(self, node, compare, minEntries):
        '''
        Return the size of all combinations of bounding-box to split
        '''
        assert isinstance(node, RBushNode)

        M = length(node.children)
        m = minEntries

        # The sorting of (children) nodes according to an axis,
        # "compare-X/Y", guides the search for where to split
        node.children = sort(node.children, compare=compare)

        leftBBox = self.distBBox(node, 0, m)
        rightBBox = self.distBBox(node, M - m, M)
        margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)

        for i in range(m, M - m):
            child = get(node.children, i)
            extend(leftBBox, child)
            margin = margin + bboxMargin(leftBBox)

        for i in range(M-m-1, m-1, -1):
            child = get(node.children, i)
            extend(rightBBox, child)
            margin = margin + bboxMargin(rightBBox)

        return margin

    def chooseSplitIndex(self, node, minEntries):
        '''
        Return the index (children) where to split

        Split position tries to minimize (primarily) the boxes overlap
        and, secondly, the area cover by each combination of boxes.
        '''
        M = length(node.children)
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
        newRoot = createNode(leaf=False,
                             height=node.height + 1,
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
            while child is not None:
                l.append(child.data)
                child = child.next
            if node.leaf:
                result.extend(l)
            else:
                nodesToSearch.extend(l)
            node = nodesToSearch.pop() if len(nodesToSearch) else None
        return result


# @njit
    def search(self, bbox):
        node = self.data
        result = []

        if isinstance(bbox, dict):
            bbox = boxFromDict(bbox)

        if not intersects(bbox, node):
            return result

        nodesToSearch = []
        while node:
            child = node.children
            while child is not None:
                if node.leaf:
                    childBBox = self.toBBox(child.data)
                else:
                    childBBox = child.data

                if intersects(bbox, childBBox):
                    if node.leaf:
                        result.append(child.data)
                    elif contains(bbox, childBBox):
                        self._all(child.data, result)
                    else:
                        nodesToSearch.append(child.data)
                child = child.next
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
            child = node.children
            while child is not None:
                # len_ = length(node.children)
                # for i in range(0, len_):
                #     child = node.children[i]
                if node.leaf:
                    childBBox = self.toBBox(child.data)
                else:
                    childBBox = child.data
                if intersects(bbox, childBBox):
                    if node.leaf or contains(bbox, childBBox):
                        return True
                    nodesToSearch.append(child.data)
                child = child.next
            node = nodesToSearch.pop() if len(nodesToSearch) else None

        return False

    # @njit
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

        if not length(self.data.children):
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

            if node is None:  # go up
                node = path.pop()
                parent = path[len(path) - 1] if len(path) else None
                i = indexes.pop() if len(indexes) else None
                goingUp = True

            if node.leaf:  # check current node
                index = findItem(item, node.children, equalsFn)
                if index is not None:
                    # item found, remove the item and condense tree upwards
                    rem, node.children = splice(node.children, index, 1)
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
                node = node.children.data

            elif parent:  # go right
                i += 1
                # try:
                if length(parent.children) > i:
                    node = get(parent.children, i)
                # except IndexError as e:
                #     node = None
                else:
                    node = None
                goingUp = False

            else:
                node = None  # nothing found
        return self

    def toBBox(self, item):
        return toBBoxNode(item)

    def calcBBox(self, node):
        """Update node sizes after its children"""
        auxNode = self.distBBox(node, 0, length(node.children))
        node.xmin = auxNode.xmin
        node.ymin = auxNode.ymin
        node.xmax = auxNode.xmax
        node.ymax = auxNode.ymax
        return node

    def distBBox(self, node, left_child, right_child, destNode=None):
        """Return a node enlarged by all children between left/right"""
        destNode = createNode() if destNode is None else destNode
        for i in range(left_child, right_child):
            child = get(node.children, i)
            assert child
            # if not child:
            #     continue
            extend(destNode, self.toBBox(child) if node.leaf else child)
        return destNode

    def comparexmin(self, a):
        return compareNodexmin(a)

    def compareymin(self, a):
        return compareNodeymin(a)

    def toDict(self):
        return nodeToDict(self.data)

    def toJSON(self, indent=None):
        import json
        return json.dumps(self.toDict(), indent=indent)

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
                node.children = push(node.children,
                                     self._build(items, j, right3, height - 1))
        self.calcBBox(node)

        return node

    def _condense(self, path):
        # go through the path, removing empty nodes and updating bboxes
        siblings = None
        for i in range(len(path)-1, -1, -1):
            if length(path[i].children) == 0:
                if i > 0:
                    siblings = path[i - 1].children
                    ind = index(siblings, path[i])
                    rem, siblings = splice(siblings, ind, 1)
                    path[i - 1].children = siblings
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

        self.toBBox = lambda a: RBushNode(a[format_[0]], a[format_[1]],
                                          a[format_[2]], a[format_[3]])
