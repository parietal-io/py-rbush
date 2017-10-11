import quickselect

import sys
INFINITY = sys.maxsize

# Javascript arrays have a 'splice' method,
#  this is the equivalent for Python lists
def splice(list_,insert_position,remove_how_many,*items_to_insert):
    removed_items = []
    for i in range(remove_how_many):
        removed_items.append( list_.pop(insert_position) )
    for item in items_to_insert[::-1]:
        list_.insert(insert_position, item)
    return removed_items

# function createNode(children) {
#     return {
#         children: children,
#         height: 1,
#         leaf: true,
#         minX: Infinity,
#         minY: Infinity,
#         maxX: -Infinity,
#         maxY: -Infinity
#     };
# }
class Node:
    '''Tree node'''
    height = 1
    leaf = True
    minX = INFINITY
    minY = INFINITY
    maxX = -INFINITY
    maxY = -INFINITY
    def __init__(self,children,data=None):
        self.children = children

def createNode(children):
    '''
    Create a node
    '''
    if not children:
        children = []
    return Node(children)


# function findItem(item, items, equalsFn) {
#     if (!equalsFn) return items.indexOf(item);
#
#     for (var i = 0; i < items.length; i++) {
#         if (equalsFn(item, items[i])) return i;
#     }
#     return -1;
# }
def findItem(item, items, equalsFn):
    if not equalsFn:
        return items.index(item)
    for i in range(0, len(items):
        #TODO equalsFn?
        if equalsFn(item, items[i]):
        return i

    return -1

def calcBBox(node):
    return distBBox(node, 0, len(node.children), node);


def distBBox(node, left_most_item, right_most_item, destNode=None):
    """Return a node enlarged by all children between left/right"""
    if not destNode:
        destNode = createNode(None);
    for i in range(left_most_item,right_most_item):
        child = node.children[i]
        _=extend(destNode, child)
    return destNode

def extend(a, b):
    """Return 'a' box enlarged by 'b'"""
    a.minX = min(a.minX, b.minX)
    a.minY = min(a.minY, b.minY)
    a.maxX = max(a.maxX, b.maxX)
    a.maxY = max(a.maxY, b.maxY)
    return a

# function compareNodeMinX(a, b) { return a.minX - b.minX; }
def compareNodeMinX(a, b):
    return a.minX - b.minX

# function compareNodeMinY(a, b) { return a.minY - b.minY; }
def compareNodeMinY(a, b):
    return a.minY - b.minY

# function bboxArea(a)   { return (a.maxX - a.minX) * (a.maxY - a.minY); }
def bboxArea(a):
    return (a.maxX - a.minX) * (a.maxY - a.minY)

# function bboxMargin(a) { return (a.maxX - a.minX) + (a.maxY - a.minY); }
def bboxMargin(a):
    return (a.maxX - a.minX) + (a.maxY - a.minY)


def enlargedArea(a, b):
    sect1 = max(b.maxX, a.maxX) - min(b.minX, a.minX)
    sect2 = max(b.maxY, a.maxY) - min(b.minY, a.minY)
    return sect1 * sect2

def intersectionArea(a,b):
    minX = max(a.minX, b.minX)
    minY = max(a.minY, b.minY)
    maxX = min(a.maxX, b.maxY)
    maxY = min(a.maxY, b.maxY)
    return max(0, maxX - minX) * max(0, maxY - minY)

def contains(a,b):
    a_lower_b = a.minX <= b.minX and a.minY <= b.minY
    a_upper_b = b.maxX <= a.maxX and b.maxY <= a.maxY
    return a_lower_b and a_upper_b


def intersects(a,b):
    b_lower_a = b.minX <= a.maxX and b.minY <= a.maxY
    b_upper_a = b.maxX >= a.minX and b.maxY >= a.minY
    return b_lower_a and b_upper_a


def multiSelect(arr, left, right, n, compare):
    from math import ceil
    stack = [left, right]
    mid = None
    #FIXME: I don't like the object being checked (i.e, 'stack') being
    #       modified inside of the loop...probably change that.
    while len(stack):
        right = stack.pop()
        left = stack.pop()
        if (right - left) <= n:
            continue
        mid = left + ceil((right - left) / n / 2) * n
        quickselect(arr, mid, left, right, compare)
        stack.push([left, mid, mid, right])


def rbush(self, maxEntries, format_):
    if not isinstance(self,Rbush):
        return Rbush(maxEntries, format_);

    ## max entries in a node is 9 by default; min node fill is 40% for best performance
    self._maxEntries = max(4, maxEntries or 9);
    self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));

    if (format_):
        self._initFormat(format_);

    self.clear()


import math

class Rbush(object):

    data = None

    def __init__(self,maxEntries,isPoint=False):
        ## max entries in a node is 9 by default; min node fill is 40% for best performance
        self._maxEntries = max(4, maxEntries or 9);
        self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));

        if (isPoint):
            self._initFormat();

    def insert(item):
        '''Insert an item'''
        assert hasattr(item,'minX') \
            and hasattr(item,'minY') \
            and hasattr(item,'maxX') \
            and hasattr(item,'maxY') \
            , "item is must have 'minX,minY,maxX,maxY attributes'"

        if item:
            self._insert(item, self.data.height - 1)
        return self

    def _insert(item, level, isNode=False):
        # bbox is *always* an item
        bbox = item if isNode else self.toBBox(item)

        insertPath = []

        ## find the best node for accommodating the item, saving all nodes along the path too
        node = self._chooseSubtree(bbox, self.data, level, insertPath)

        ## put the item into the node
        node.children.append(item)
        _=extend(node, bbox)

        ## split on node overflow; propagate upwards if necessary
        while level >= 0:
            if len(insertPath[level].children) > self._maxEntries:
                self._split(insertPath, level);
                level=level-1
            else:
                break

        ## adjust bboxes along the insertion path
        self._adjustParentBBoxes(bbox, insertPath, level);

    def clear():
        self.data = createNode([])
        return self

    # I understand 'all' is the equivalent to __init__
    def all(self):
        return self._all(self.data, [])

    def _all(node, result):
        nodesToSearch = []
        while node:
            if node.leaf:
                # result.push.apply(result, node.children);
                result.extend(node.children)
            else:
                nodesToSearch.extend(node.children)
            node = nodesToSearch.pop(-1)
        return result

    def search(self,bbox):
        node = self.data
        result = []
        toBBox = self.toBBox
        if not intersects(bbox, node):
            return result
        nodesToSearch = []
        i = None
        len_ = None
        child = None
        childBBox = None
        while node:
            len_ = len(node.children)
            for i in range(0,len_):
                child = node.children[i]
                childBBox = toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf:
                        result.append(child)
                    elif contains(bbox, childBBox):
                        self._all(child, result)
                    else:
                        nodesToSearch.append(child)
            node = nodesToSearch.pop() #XXX: Python does pop(0) by default; check if javascript is the same
        return result

    def collides(bbox):
        node = self.data
        toBBox = self.toBBox
        if not intersects(bbox, node):
            return false
        nodesToSearch = []
        i = None
        len_ = None
        child = None
        childBBox = None
        while node:
            len_ = len(node.children)
            for i in range(0,len_):
                child = node.children[i]
                childBBox = toBBox(child) if node.leaf else child
                if intersects(bbox, childBBox):
                    if node.leaf or contains(bbox, childBBox):
                        return true;
                    nodesToSearch.append(child)
            node = nodesToSearch.pop()
        return False

    def load(data):
        if not (data && len(data)):
            return self
        if (data.length < self_minEntries):
            len_ = len(data)
            for i in range(0,len_):
                self.insert(data[i]) #XXX this.insert? define 'insert' method for rbush
            return self

        ## recursively build the tree with the given data from scratch using OMT algorithm
        #XXX what is 'data' and what 'slice' does?
        node = self._build(data.slice(), 0, len(data) - 1, 0)

        #XXX looks like 'data' is a node...
        if not len(self.data.children):
            ## save as is if tree is empty
            self.data = node
        elif (self.data.height == node.height):
            ## split root if trees have the same height
            self._splitRoot(self.data, node)
        else:
            if (self.data.height < node.height):
                ## swap trees if inserted one is bigger
                tmpNode = self.data
                self.data = node
                node = tmpNode
            ## insert the small tree into the large tree at appropriate level
            self._insert(node, self.data.height - node.height - 1, true)
        return self

    def remove(item, equalsFn):
        if not item:
            return self

        node = self.data
        bbox = self.toBBox(item)
        path = []
        indexes = []
        i = None
        parent = None
        index = None
        goingUp = None

        ## depth-first iterative tree traversal
        while node or len(path):
            if not node: ## go up
                node = path.pop()
                parent = path[len(path) - 1]
                i = indexes.pop()
                goingUp = True
            if node.leaf: ## check current node
                index = findItem(item, node.children, equalsFn)
                if index != -1:
                    ## item found, remove the item and condense tree upwards
                    #XXX 'splice' method is a method for javascript array
                    # node.children.splice(index, 1)
                    splice(node.children, index, 1)
                    path.append(node)
                    self._condense(path)
                    return self

            if not goingUp and not node.leaf and contains(node, bbox): ## go down
                path.append(node)
                indexes.append(i)
                i = 0
                parent = node
                node = node.children[0]

            elif (parent): ## go right
                i=i+1
                node = parent.children[i]
                goingUp = False

            else:
                node = null ## nothing found

        return this

    def toBBox(item):
        '''
        Simply return 'item'
        '''
        # item is a (2D) box...
        return item

    compareMinX = compareNodeMinX
    compareMinY = compareNodeMinY

    #XXX 'toJSON' returns 'data'? That means that data is in 'json' format and is being dumpd
    def toJSON():
        return self.data

    def fromJSON(data):
        self.data = data
        return self

    def _build(items, left, right, height):
        N = right - left + 1
        M = self._maxEntries
        node = None

        if N <= M:
            ## reached leaf level; return leaf
            node = createNode(items[left : right + 1])
            calcBBox(node, self.toBBox)
            return node

        if not height:
            ## target height of the bulk-loaded tree
            height = math.ceil(math.log(N) / math.log(M))

            ## target number of root entries to maximize storage utilization
            M = math.ceil(N / math.pow(M, height - 1))

        node = createNode([])
        node.leaf = False
        node.height = height

        ## split the items into M mostly square tiles
        N2 = math.ceil(N / M)
        N1 = N2 * math.ceil(math.sqrt(M))
        i = None
        j = None
        right2 = None
        right3 = None

        multiSelect(items, left, right, N1, self.compareMinX)

        for i in range(left, right+1, N1):
            right2 = min(i + N1 - 1, right)
            multiSelect(items, i, right2, N2, self.compareMinY)
            for j in range(i, right2+1, N2):
                right3 = min(j + N2 - 1, right2)
                ## pack each entry recursively
                node.children.append(self._build(items, j, right3, height - 1))
        calcBBox(node, self.toBBox)
        return node

    def _chooseSubtree(bbox, node, level, path):
        '''
        Return the node closer to 'bbox'

        Traverse the subtree searching for the tightest path,
        the node at the end, closest to bbox is returned
        '''
        while True:
            path.append(node)
            if node.leaf or (len(path)-1 == level):
                break
            #XXX what is level==-1|0? node must be a leaf!
            assert not node.leaf and level > 0

            minEnlargement = INFINITY
            minArea = INFINITY

            targetNode = None
            len_ = len(node.children)
            for i in range(0, len_):
                child = node.children[i]
                area = bboxArea(child)
                enlargement = enlargedArea(bbox, child) - area

                ## choose entry with the least area enlargement
                if (enlargement < minEnlargement):
                    minEnlargement = enlargement
                    minArea = area if area < minArea else minArea
                    targetNode = child
                else:
                    if (enlargement == minEnlargement):
                        ## otherwise choose one with the smallest area
                        if (area < minArea):
                            minArea = area
                            targetNode = child

            node = targetNode or node.children[0]

        #NOTE: 'node' is returned, 'path' was modified (i.e, filled)
        return node


    ## split overflowed node into two
    def _split(self, insertPath, level):
        node = insertPath[level]

        M = len(node.children)
        m = self._minEntries

        self._chooseSplitAxis(node, m, M)

        splitIndex = self._chooseSplitIndex(node, m, M)

        numChildren = len(node.children) - splitIndex
        adopted = splice(node.children, splitIndex, numChildren)
        newNode = createNode(adopted)
        newNode.height = node.height
        newNode.leaf = node.leaf

        calcBBox(node)
        calcBBox(newNode)

        if level:
            insertPath[level-1].children.append(newNode)
        else:
            self._splitRoot(node, newNode)

    def _splitRoot(node, newNode):
        ## split root node
        self.data = createNode([node, newNode])
        self.data.height = node.height + 1
        self.data.leaf = False
        calcBBox(self.data);

    def _chooseSplitIndex(self,node):
        M = len(node.children)
        m = self._minEntries

        minArea = INFINITY
        minOverlap = INFINITY

        for i in range(m, M - m + 1):
            bbox1 = distBBox(node, 0, i);
            bbox2 = distBBox(node, i, M);

            overlap = intersectionArea(bbox1, bbox2);
            area = bboxArea(bbox1) + bboxArea(bbox2);

            ## choose distribution with minimum overlap
            if (overlap < minOverlap):
                minOverlap = overlap;
                index = i;
                minArea = are if area < minArea else minArea;

            else:
                if (overlap == minOverlap):
                    ## otherwise choose distribution with minimum area
                    if (area < minArea):
                        minArea = area
                        index = i

        return index;

    ## sorts node children by the best axis for split
    def _chooseSplitAxis(self,node):
        M = len(node.children)
        m = self._minEntries
        compareMinX = self.compareMinX if node.leaf else compareNodeMinX
        compareMinY = self.compareMinY if node.leaf else compareNodeMinY
        xMargin = self._allDistMargin(node, compareMinX),
        yMargin = self._allDistMargin(node, compareMinY);

        ## if total distributions margin value is minimal for x, sort by minX,
        ## otherwise it's already sorted by minY
        if (xMargin < yMargin):
            node.children.sort(compareMinX)

    ## total margin of all possible split distributions where each node is at least m full
    def _allDistMargin(self, node, compare):
        M = len(node.children)
        m = self._minEntries

        #NOTE the order of 'node.children' is changed in place by 'sort':
        node.children.sort(compare)

        leftBBox = distBBox(node, 0, m)#, toBBox)
        rightBBox = distBBox(node, M - m, M)#, toBBox)
        margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)

        for i in range(m, M - m):
            child = node.children[i];
            extend(leftBBox, child);
            margin = margin + bboxMargin(leftBBox);

        for i in range(M-m-1, m-1, -1):
            child = node.children[i];
            extend(rightBBox, child);
            margin = margin + bboxMargin(rightBBox);

        return margin;

    def _adjustParentBBoxes(bbox, path, level):
        ## adjust bboxes along the given tree path
        for i in range(level, -1, -1):
            extend(path[i], bbox);

    def _condense(path):
        ## go through the path, removing empty nodes and updating bboxes
        siblings = None
        for i in range(len(path)-1, -1; -1):
            if len(path[i].children) == 0:
                if (i > 0):
                    siblings = path[i - 1].children;
                    splice(siblings, siblings.indexOf(path[i]), 1);
                else:
                    self.clear();
            else:
                calcBBox(path[i], self.toBBox);

    def _initFormat(self):#format_):
        ## data format (minX, minY, maxX, maxY accessors)

        ## uses eval-type function compilation instead of just accepting a toBBox function
        ## because the algorithms are very sensitive to sorting functions performance,
        ## so they should be dead simple and without inner calls
        #compareArr = ['return a', ' - b', ';'];

        self.compareMinX = lambda a,b: a[0] - b[0]#new Function('a', 'b', compareArr.join(format_[0]));
        self.compareMinY = lambda a,b: a[1] - b[1]#new Function('a', 'b', compareArr.join(format_[1]));

        # self.toBBox = new Function('a',
        #     'return {minX: a' + format_[0] +
        #     ', minY: a' + format_[1] +
        #     ', maxX: a' + format_[2] +
        #     ', maxY: a' + format_[3] + '};');
        self.toBBox = lambda a: {minX: a[0], minY: a[1], maxX: a[0], maxY: a[1]}
