import sys
INF = sys.maxsize

import math

from importlib import reload
import quickselect
reload(quickselect)
quickselect = quickselect.quickselect

_node = dict(
    minX = INF,
    minY = INF,
    maxX = -INF,
    maxY = -INF,
    leaf = True,
    height = 1,
    # data = None,
    children = None
)

Point = dict(
    X = None,
    y = None
)

def createNode(children=[],data=None):
    '''
    Create a node (leaf,parent or bbox)
    '''
    # assert (children is None) != (data is None)
    node = _node.copy()
    node['children'] = children
    # node['data'] = data
    # node['leaf'] = children is None
    return node

def toBBox(item):
    '''
    Simply return 'item'
    '''
    # For the time being, I'll create a node and put item as its child
    # and call it a leaf...soon I'll figure out the best thing to do...
    node = createNode(data=item)
    node['minX'] = item['minX']
    node['minY'] = item['minY']
    node['maxX'] = item['maxX']
    node['maxY'] = item['maxY']
    return node

# Javascript arrays have a 'splice' method,
#  this is the equivalent for Python lists
def splice(list_,insert_position,remove_how_many,*items_to_insert):
    removed_items = []
    for i in range(remove_how_many):
        removed_items.append( list_.pop(insert_position) )
    for item in items_to_insert[::-1]:
        list_.insert(insert_position, item)
    return removed_items

def findItem(item, items, equalsFn=None):
    if not equalsFn:
        return items.index(item)
    for i in range(0, len(items)):
        #TODO equalsFn?
        if equalsFn(item, items[i]):
            return i
    return -1

def calcBBox(node):
    """Update node sizes after its children"""
    return distBBox(node, 0, len(node['children']), node);


def distBBox(node, left_child, right_child, destNode=None):
    """Return a node enlarged by all children between left/right"""
    destNode = createNode() if destNode is None else destNode
    for i in range(left_child,right_child):
        extend(destNode, node['children'][i])
    return destNode

def extend(a, b):
    """Return 'a' box enlarged by 'b'"""
    a['minX'] = min(a['minX'], b['minX'])
    a['minY'] = min(a['minY'], b['minY'])
    a['maxX'] = max(a['maxX'], b['maxX'])
    a['maxY'] = max(a['maxY'], b['maxY'])
    return a

# function compareNodeMinX(a, b) { return a['minX'] - b['minX']; }
def compareNodeMinX(a):
    return a['minX']# - b['minX']

# function compareNodeMinY(a, b) { return a['minY'] - b['minY']; }
def compareNodeMinY(a):
    return a['minY']# - b['minY']

# function bboxArea(a)   { return (a['maxX'] - a['minX']) * (a['maxY'] - a['minY']); }
def bboxArea(a):
    return (a['maxX'] - a['minX']) * (a['maxY'] - a['minY'])

# function bboxMargin(a) { return (a['maxX'] - a['minX']) + (a['maxY'] - a['minY']); }
def bboxMargin(a):
    return (a['maxX'] - a['minX']) + (a['maxY'] - a['minY'])


def enlargedArea(a, b):
    sect1 = max(b['maxX'], a['maxX']) - min(b['minX'], a['minX'])
    sect2 = max(b['maxY'], a['maxY']) - min(b['minY'], a['minY'])
    return sect1 * sect2

def intersectionArea(a,b):
    minX = max(a['minX'], b['minX'])
    minY = max(a['minY'], b['minY'])
    maxX = min(a['maxX'], b['maxY'])
    maxY = min(a['maxY'], b['maxY'])
    return max(0, maxX - minX) * max(0, maxY - minY)

def contains(a,b):
    a_lower_b = a['minX'] <= b['minX'] and a['minY'] <= b['minY']
    a_upper_b = b['maxX'] <= a['maxX'] and b['maxY'] <= a['maxY']
    return a_lower_b and a_upper_b


def intersects(a,b):
    b_lower_a = b['minX'] <= a['maxX'] and b['minY'] <= a['maxY']
    b_upper_a = b['maxX'] >= a['minX'] and b['maxY'] >= a['minY']
    return b_lower_a and b_upper_a


def multiSelect(items, left, right, n, compare):
    stack = [left, right]
    mid = None
    #FIXME: I don't like the object being checked (i.e, 'stack') being
    #       modified inside of the loop...probably change that.
    while len(stack):
        right = stack.pop()
        left = stack.pop()
        if (right - left) <= n:
            continue
        mid = left + math.ceil((right - left) / n / 2) * n
        quickselect(items, mid, left, right, compare)
        stack.extend([left, mid, mid, right])


# def rbush(self, maxEntries, format_):
#     if not isinstance(self,Rbush):
#         return Rbush(maxEntries, format_);
#
#     ## max entries in a node is 9 by default; min node fill is 40% for best performance
#     self._maxEntries = max(4, maxEntries or 9);
#     self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));
#
#     if (format_):
#         self._initFormat(format_);
#
#     self.clear()


def chooseSubtree(bbox, node, level, path):
    '''
    Return the node closer to 'bbox'

    Traverse the subtree searching for the tightest path,
    the node at the end, closest to bbox is returned
    '''
    while True:

        path.append(node)

        if node['leaf'] or (len(path)-1 == level):
            break

        minEnlargement = INF
        minArea = INF

        targetNode = None
        len_ = len(node['children'])
        for i in range(0, len_):
            child = node['children'][i]
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

        node = targetNode or node['children'][0]

    #NOTE: 'node' is returned, 'path' was modified (i.e, filled)
    return node

def adjustParentBBoxes(bbox, path, level):
    ## adjust bboxes along the given tree path
    for i in range(level, -1, -1):
        extend(path[i],bbox);


## total margin of all possible split distributions where each node is at least m full
def allDistMargin(node, compare, minEntries):
    '''
    Return the "size of all combinations of bounding-box to split
    '''
    M = len(node['children'])
    m = minEntries

    # The sorting of (children) nodes according to an axis,
    # "compare-X/Y", guides the search for where to split
    node['children'].sort(key=compare)

    leftBBox = distBBox(node, 0, m)
    rightBBox = distBBox(node, M - m, M)
    margin = bboxMargin(leftBBox) + bboxMargin(rightBBox)

    for i in range(m, M - m):
        child = node['children'][i];
        extend(leftBBox, child);
        margin = margin + bboxMargin(leftBBox);

    for i in range(M-m-1, m-1, -1):
        child = node['children'][i];
        extend(rightBBox, child);
        margin = margin + bboxMargin(rightBBox);

    return margin;

def chooseSplitAxis(node, minEntries):
    '''
    Sort node's children by the best axis for split

    The best axis is defined based on a estimate of
    "density", the more compact axis goes split.
    '''
    M = len(node['children'])
    # m = self._minEntries
    compareMinX = compareNodeMinX
    compareMinY = compareNodeMinY
    xMargin = allDistMargin(node, compareMinX, minEntries)
    yMargin = allDistMargin(node, compareMinY, minEntries)

    ## if total distributions margin value is minimal for x, sort by minX,
    ## otherwise it's already sorted by minY
    if (xMargin < yMargin):
        node['children'].sort(compareMinX)

def chooseSplitIndex(node, minEntries):
    '''
    Return the index (children) where to split

    Split position tries to minimize (primarily) the boxes overlap
    and, secondly, the area cover by each combination of boxes.
    '''
    M = len(node['children'])
    m = minEntries

    minArea = INF
    minOverlap = INF

    for i in range(m, M - m + 1):
        bbox1 = distBBox(node, 0, i);
        bbox2 = distBBox(node, i, M);

        overlap = intersectionArea(bbox1, bbox2);
        area = bboxArea(bbox1) + bboxArea(bbox2);

        ## choose distribution with minimum overlap
        if (overlap < minOverlap):
            minOverlap = overlap;
            index = i;
            minArea = area if area < minArea else minArea;

        else:
            if (overlap == minOverlap):
                ## otherwise choose distribution with minimum area
                if (area < minArea):
                    minArea = area
                    index = i

    return index;



class Rbush(object):

    def __init__(self,maxEntries,toPoint=False):
        ## max entries in a node is 9 by default; min node fill is 40% for best performance
        self._maxEntries = max(4, maxEntries or 9);
        self._minEntries = max(2, math.ceil(self._maxEntries * 0.4));
        self.data = createNode(children=[])

        if (toPoint):
            self._initFormat();

    def insert(self,item):
        '''Insert an item'''
        assert  'minX' in item \
            and 'minY' in item \
            and 'maxX' in item \
            and 'maxY' in item \
            , "item is must have 'minX,minY,maxX,maxY' attributes"

        if self.data['children']:
            self._insert(item, self.data['height'] - 1)
        else:
            self._createRoot(item)

        # import pprint
        # print(pprint.pprint(self.data))

    def _createRoot(self,item):
        # node = createNode(data=item)
        root = createNode(children=[item])
        root['height'] = 1
        root['leaf'] = True
        calcBBox(root);
        self.data = root

    def _insert(self, item, level, isNode=False):
        #
        root = self.data
        bbox = toBBox(item) if not isNode else item
        assert isinstance(bbox,root.__class__)

        insertPath = []

        ## find the best node for accommodating the item, saving all nodes along the path too
        node = chooseSubtree(bbox, root, level, insertPath)

        ## put the item into the node
        node['children'].append(item)
        # node['children'].append(bbox)
        extend(node,bbox)

        ## split on node overflow; propagate upwards if necessary
        while level >= 0:
            if len(insertPath[level]['children']) > self._maxEntries:
                self._split(insertPath, level)
                level=level-1
            else:
                break

        ## adjust bboxes along the insertion path
        adjustParentBBoxes(bbox, insertPath, level)

    ## split overflowed node into two
    def _split(self, insertPath, level):

        m = self._minEntries
        node = insertPath[level]
        M = len(node['children'])

        chooseSplitAxis(node, m)

        splitIndex = chooseSplitIndex(node, m)

        numChildren = len(node['children']) - splitIndex
        adopted = splice(node['children'], splitIndex, numChildren)
        newNode = createNode( children=adopted )
        newNode['height'] = node['height']
        newNode['leaf'] = node['leaf']
        # assert not node['leaf'], "a leaf should not have children!"

        # Update the sizes (limits) of each box
        calcBBox(node)
        calcBBox(newNode)

        if level:
            insertPath[level-1]['children'].append(newNode)
        else:
            self._splitRoot(node, newNode)

    def _splitRoot(self, node, newNode):
        ## split root node
        newRoot = createNode([node, newNode])
        newRoot['height'] = node['height'] + 1
        newRoot['leaf'] = False
        calcBBox(newRoot);
        self.data = newRoot

    def clear(self):
        self.data = createNode()

    # I understand 'all' is the equivalent to __init__
    def all(self):
        return self._all(self.data, [])

    def _all(self, node, result):
        nodesToSearch = []
        while node:
            if node['leaf']:
                # result.push.apply(result, node['children']);
                result.extend(node['children'])
                # result.append(node['data'])
            else:
                nodesToSearch.extend(node['children'])
            node = nodesToSearch.pop() if len(nodesToSearch) else None
        return result

    def search(self,bbox):
        node = self.data
        result = []

        if not intersects(bbox, node):
            return result

        nodesToSearch = []
        while node:
            len_ = len(node['children'])
            for i in range(0,len_):
                child = node['children'][i]
                childBBox = toBBox(child) if node['leaf'] else child
                if intersects(bbox, childBBox):
                    if node['leaf']:
                        result.append(child)
                    elif contains(bbox, childBBox):
                        self._all(child, result)
                    else:
                        nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None
        return result

    def collides(self,bbox):
        node = self.data
        if not intersects(bbox, node):
            return false

        nodesToSearch = []
        while node:
            len_ = len(node['children'])
            for i in range(0,len_):
                child = node['children'][i]
                childBBox = toBBox(child) if node['leaf'] else child
                if intersects(bbox, childBBox):
                    if node['leaf'] or contains(bbox, childBBox):
                        return True;
                    nodesToSearch.append(child)
            node = nodesToSearch.pop() if len(nodesToSearch) else None
        return False

    def load(self,data):
        if not (data and len(data)):
            return False
        len_ = len(data)
        if (len_ < self._minEntries):
            for i in range(0,len_):
                self.insert(data[i])
            return True

        ## recursively build the tree with the given data from scratch using OMT algorithm
        node = self._build(data[:], 0, len(data) - 1, 0)

        if not len(self.data['children']):
            ## save as is if tree is empty
            self.data = node
        elif (self.data['height'] == node['height']):
            ## split root if trees have the same height
            self._splitRoot(self.data, node)
        else:
            if (self.data['height'] < node['height']):
                ## swap trees if inserted one is bigger
                tmpNode = self.data
                self.data = node
                node = tmpNode
            ## insert the small tree into the large tree at appropriate level
            self._insert(node, self.data['height'] - node['height'] - 1, True)
        return True

    def remove(self, item, equalsFn=None):
        if not item:
            return None

        node = self.data
        bbox = toBBox(item)
        path = []
        indexes = []
        goingUp = False
        parent = None

        ## depth-first iterative tree traversal
        while node or len(path):
            if not node: ## go up
                node = path.pop()
                parent = path[len(path) - 1]
                i = indexes.pop()
                goingUp = True
            if node['leaf']: ## check current node
                index = findItem(item, node['children'], equalsFn)
                if index != -1:
                    ## item found, remove the item and condense tree upwards
                    # node['children'].splice(index, 1)
                    splice(node['children'], index, 1)
                    path.append(node)
                    self._condense(path)
                    return self

            if not goingUp and not node['leaf'] and contains(node, bbox): ## go down
                path.append(node)
                indexes.append(i)
                i = 0
                parent = node
                node = node['children'][0]

            elif (parent): ## go right
                i=i+1
                node = parent['children'][i]
                goingUp = False

            else:
                node = None ## nothing found

        return this

    # def toBBox(self,item):
    #     '''
    #     Simply return 'item'
    #     '''
    #     # item is a (2D) box...
    #     return toBBox(item)

    compareMinX = compareNodeMinX
    compareMinY = compareNodeMinY

    #XXX 'toJSON' returns 'data'? That means that data is in 'json' format and is being dumpd
    def toJSON(self):
        return self.data

    def fromJSON(data):
        self.data = data

    def _build(self, items, left, right, height):
        N = right - left + 1
        M = self._maxEntries
        node = None

        if N <= M:
            ## reached leaf level; return leaf
            node = createNode(items[left : right + 1])
            calcBBox(node)
            return node

        if not height:
            ## target height of the bulk-loaded tree
            height = math.ceil(math.log(N) / math.log(M))

            ## target number of root entries to maximize storage utilization
            M = math.ceil(N / math.pow(M, height - 1))

        node = createNode([])
        node['leaf'] = False
        node['height'] = height

        ## split the items into M mostly square tiles
        N2 = math.ceil(N / M)
        N1 = N2 * math.ceil(math.sqrt(M))

        multiSelect(items, left, right, N1, compareNodeMinX)

        for i in range(left, right+1, N1):
            right2 = min(i + N1 - 1, right)
            multiSelect(items, i, right2, N2, compareNodeMinY)
            for j in range(i, right2+1, N2):
                right3 = min(j + N2 - 1, right2)
                ## pack each entry recursively
                node['children'].append(self._build(items, j, right3, height - 1))
        calcBBox(node)
        return node



    def _condense(self,path):
        ## go through the path, removing empty nodes and updating bboxes
        siblings = None
        for i in range(len(path)-1, -1, -1):
            if len(path[i]['children']) == 0:
                if (i > 0):
                    siblings = path[i - 1]['children'];
                    splice(siblings, siblings.index(path[i]), 1);
                else:
                    self.clear();
            else:
                calcBBox(path[i]);

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
