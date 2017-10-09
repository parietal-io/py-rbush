import quickselect

INFINITY = float('inf')

# Javascript arrays have a 'splice' method,
#  this is the equivalent for Python lists
def splice(list_,insert_position,remove_how_many,*items_to_insert):
    for i in range(remove_how_many):
        _= list_.pop(insert_position)
    for item in items_to_insert[::-1]:
        list_.insert(insert_position, item)
    return #list_

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
    def __init__(self,children):
        self.children = children

def createNode(children):
    '''
    Creates a node
    '''
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
    }
    return -1


# calculate node's bbox from bboxes of its children
# function calcBBox(node, toBBox) {
#     distBBox(node, 0, node.children.length, toBBox, node);
# }
def calcBBox(node, toBBox):
    distBBox(node, 0, len(node.children), toBBox, node);
}

## min bounding rectangle of node children from k to p-1
# function distBBox(node, k, p, toBBox, destNode) {
#     if (!destNode) destNode = createNode(null);
#     destNode.minX = Infinity;
#     destNode.minY = Infinity;
#     destNode.maxX = -Infinity;
#     destNode.maxY = -Infinity;
#
#     for (var i = k, child; i < p; i++) {
#         child = node.children[i];
#         extend(destNode, node.leaf ? toBBox(child) : child);
#     }
#
#     return destNode;
# }
def distBBox(node, k, p, toBBox, destNode):
    if not destNode:
        destNode = createNode(None);
    for i in range(k,p):
        child = node.children[i]
        #TODO: toBBox is a method of rbush(prototype), needs to implement
        otherNode = toBBox(child) if node.leaf else child
        extend(destNode, otherNode)
    return destNode


# function extend(a, b) {
#     a.minX = Math.min(a.minX, b.minX);
#     a.minY = Math.min(a.minY, b.minY);
#     a.maxX = Math.max(a.maxX, b.maxX);
#     a.maxY = Math.max(a.maxY, b.maxY);
#     return a;
# }
def extend(a, b):
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


# function enlargedArea(a, b) {
#     return (Math.max(b.maxX, a.maxX) - Math.min(b.minX, a.minX)) *
#            (Math.max(b.maxY, a.maxY) - Math.min(b.minY, a.minY));
# }
def enlargedArea(a, b):
    sect1 = max(b.maxX, a.maxX) - min(b.minX, a.minX)
    sect2 = max(b.maxY, a.maxY) - min(b.minY, a.minY)
    return sect1 * sect2


# function intersectionArea(a, b) {
#     var minX = Math.max(a.minX, b.minX),
#         minY = Math.max(a.minY, b.minY),
#         maxX = Math.min(a.maxX, b.maxX),
#         maxY = Math.min(a.maxY, b.maxY);
#
#     return Math.max(0, maxX - minX) *
#            Math.max(0, maxY - minY);
# }
def intersectionArea(a,b):
    minX = max(a.minX, b.minX)
    minY = max(a.minY, b.minY)
    maxX = min(a.maxX, b.maxY)
    maxY = min(a.maxY, b.maxY)
    return max(0, maxX - minX) * max(0, maxY - minY)

# function contains(a, b) {
#     return a.minX <= b.minX &&
#            a.minY <= b.minY &&
#            b.maxX <= a.maxX &&
#            b.maxY <= a.maxY;
# }
def contains(a,b):
    a_lower_b = a.minX <= b.minX and a.minY <= b.minY
    a_upper_b = b.maxX <= a.maxX and b.maxY <= a.maxY
    return a_lower_b and a_upper_b


# function intersects(a, b) {
#     return b.minX <= a.maxX &&
#            b.minY <= a.maxY &&
#            b.maxX >= a.minX &&
#            b.maxY >= a.minY;
# }
def intersects(a,b):
    b_lower_a = b.minX <= a.maxX and b.minY <= a.maxY
    b_upper_a = b.maxX >= a.minX and b.maxY >= a.minY
    return b_lower_a and b_upper_a


## sort an array so that items come in groups of n unsorted items, with groups sorted between each other;
## combines selection algorithm with binary divide & conquer approach
# function multiSelect(arr, left, right, n, compare) {
#     var stack = [left, right],
#         mid;
#
#     while (stack.length) {
#         right = stack.pop();
#         left = stack.pop();
#
#         if (right - left <= n) continue;
#
#         mid = left + Math.ceil((right - left) / n / 2) * n;
#         quickselect(arr, mid, left, right, compare);
#
#         stack.push(left, mid, mid, right);
#     }
# }
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


#XXX: Understand this function:
# function rbush(maxEntries, format) {
#     if (!(this instanceof rbush)) return new rbush(maxEntries, format);
#
#     // max entries in a node is 9 by default; min node fill is 40% for best performance
#     this._maxEntries = Math.max(4, maxEntries || 9);
#     this._minEntries = Math.max(2, Math.ceil(this._maxEntries * 0.4));
#
#     if (format) {
#         this._initFormat(format);
#     }
#
#     this.clear();
# }
def rbush(self, maxEntries, format_):
    if not isinstance(self,Rbush):
        return Rbush(maxEntries, format_);

    ## max entries in a node is 9 by default; min node fill is 40% for best performance
    self._maxEntries = max(4, maxEntries or 9);
    self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));

    if (format_):
        self._initFormat(format_);

    self.clear()


class Rbush(object):

    # I understand 'all' is the equivalent to __init__
    def __init__(self):
        return self._all(self.data, [])

    def _init(node, result):
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

    def insert(item):
        if item:
            self._insert(item, self.data.height - 1)
        return self

    def clear():
        self.data = createNode([])
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
        i = None
        len = None
        child = None
        targetNode = None
        area = None
        enlargement = None
        minArea = None
        minEnlargement = None

        while True:
            path.append(node)

            if node.leaf or (len(path)-1 == level):
                break

            minEnlargement = INFINITY
            minArea = INFINITY

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
                    if (enlargement === minEnlargement):
                        ## otherwise choose one with the smallest area
                        if (area < minArea):
                            minArea = area
                            targetNode = child

            node = targetNode or node.children[0]

        return node

    def _insert(item, level, isNode):
        toBBox = self.toBBox
        bbox = item if isNode else toBBox(item)
        insertPath = []

        ## find the best node for accommodating the item, saving all nodes along the path too
        node = self._chooseSubtree(bbox, self.data, level, insertPath)

        ## put the item into the node
        node.children.append(item)
        extend(node, bbox)

        ## split on node overflow; propagate upwards if necessary
        while level >= 0:
            if len(insertPath[level].children) > self._maxEntries:
                self._split(insertPath, level);
                level=level-1
            else:
                break

        ## adjust bboxes along the insertion path
        self._adjustParentBBoxes(bbox, insertPath, level);

    ## split overflowed node into two
    def _split(insertPath, level):
        node = insertPath[level]
        M = len(node.children)
        m = self._minEntries

        self._chooseSplitAxis(node, m, M)

        splitIndex = self._chooseSplitIndex(node, m, M)

        newNode = createNode(splice(node.children, splitIndex, node.children.length - splitIndex))
        newNode.height = node.height
        newNode.leaf = node.leaf

        calcBBox(node, self.toBBox)
        calcBBox(newNode, self.toBBox)

        if (level):
            insertPath[level - 1].children.append(newNode)
        else:
            self_splitRoot(node, newNode)

    def _splitRoot(node, newNode):
        ## split root node
        self.data = createNode([node, newNode])
        self.data.height = node.height + 1
        self.data.leaf = False
        calcBBox(self.data, self.toBBox);

    def _chooseSplitIndex(node, m, M):
        i = None
        bbox1 = None
        bbox2 = None
        overlap = None
        area = None
        minOverlap = None
        minArea = None
        index = None

        minArea = INFINITY
        minOverlap = INFINITY

        for i in range(m, M - m + 1):
            bbox1 = distBBox(node, 0, i, selftoBBox);
            bbox2 = distBBox(node, i, M, self.toBBox);

            overlap = intersectionArea(bbox1, bbox2);
            area = bboxArea(bbox1) + bboxArea(bbox2);

            ## choose distribution with minimum overlap
            if (overlap < minOverlap):
                minOverlap = overlap;
                index = i;

                minArea = area < minArea ? area : minArea;

            else:
                if (overlap == minOverlap):
                    ## otherwise choose distribution with minimum area
                    if (area < minArea):
                        minArea = area
                        index = i

        return index;

    ## sorts node children by the best axis for split
    def _chooseSplitAxis(node, m, M):
        compareMinX = self.compareMinX if node.leaf else compareNodeMinX
        compareMinY = self.compareMinY if node.leaf else compareNodeMinY
        xMargin = self._allDistMargin(node, m, M, compareMinX),
        yMargin = self._allDistMargin(node, m, M, compareMinY);

        ## if total distributions margin value is minimal for x, sort by minX,
        ## otherwise it's already sorted by minY
        if (xMargin < yMargin):
            node.children.sort(compareMinX)

    ## total margin of all possible split distributions where each node is at least m full
    def _allDistMargin(node, m, M, compare):
        node.children.sort(compare)
        toBBox = self.toBBox
        leftBBox = distBBox(node, 0, m, toBBox)
        rightBBox = distBBox(node, M - m, M, toBBox)
        margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)
        i = None
        child = None

        for i in range(m, M - m):
            child = node.children[i];
            extend(leftBBox, toBBox(child) if node.leaf else child);
            margin = margin + bboxMargin(leftBBox);

        for i in range(M-m-1, m-1, -1):
            child = node.children[i];
            extend(rightBBox, toBBox(child) if node.leaf else child);
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
