import math

from collections import OrderedDict

import numba as nb

import numpy as np
INF = np.iinfo(np.int64).max


node_type = nb.deferred_type()
linkednode_type = nb.deferred_type()
stack_type = nb.deferred_type()


# Define the nodes of our tree
node_spec = OrderedDict()
node_spec['bbox'] = nb.float64[:]
node_spec['data'] = nb.optional(nb.float64)
node_spec['leaf'] = nb.optional(nb.boolean)
node_spec['height'] = nb.optional(nb.int16)
node_spec['children'] = nb.optional(stack_type)


@nb.jitclass(node_spec)
class Node(object):
    def __init__(self, bbox, data, leaf, height, children):
        self.bbox = bbox
        self.data = data
        self.leaf = leaf
        self.height = height
        self.children = children


node_type.define(Node.class_type.instance_type)


# Define a linked list for the nodes
linkednode_spec = OrderedDict()
linkednode_spec['data'] = node_type
linkednode_spec['next'] = nb.optional(linkednode_type)


@nb.jitclass(linkednode_spec)
class LinkedNode(object):
    def __init__(self, data, next):
        self.data = data
        self.next = next


linkednode_type.define(LinkedNode.class_type.instance_type)


# Encapsulate the linked list in a stack
stack_spec = OrderedDict()
stack_spec['head'] = nb.optional(linkednode_type)
stack_spec['size'] = nb.intp


@nb.jitclass(stack_spec)
class Stack(object):
    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, data):
        old = self.head
        new = LinkedNode(data, old)
        self.head = new
        self.size += 1

    def pop(self):
        old = self.head
        if old is None:
            raise ValueError("empty stack")
        else:
            self.head = old.next
            self.size -= 1
            return old.data

    def get(self, i):
        if i >= self.size:
            raise ValueError("out of size")
        cur = self.head
        j = 0
        while j < i:
            cur = cur.next
            j += 1
        return cur.data


stack_type.define(Stack.class_type.instance_type)


#
@nb.jit
def create_node(bbox, data=None, leaf=None, height=None, children=None, is_data_node=False):
    if children is None and is_data_node is False:
        children = Stack()
    node = Node(bbox, data, leaf, height, children)
    return node


# @nb.jit
def create_root(children=None, height=1, leaf=True):
    bbox = np.array([INF, INF, -INF, -INF], dtype=float)
    return create_node(bbox, leaf=leaf, height=height, children=children)


def create_item(bbox, data):
    bbox = np.asarray(bbox, dtype=float)
    return create_node(bbox, data=data, is_data_node=True)


MAXENTRIES = 9
MINENTRIES = int(9*0.4)

class RBush(object):

    def __init__(self, maxentries=None, minentries=None):
        self.maxentries = maxentries or MAXENTRIES
        self.minentries = minentries or MINENTRIES
        self.data = None
        self.clear()

    def clear(self):
        self._root = create_root()

#    @property
#    def xmin(self):
#        return xminf(self._root)
#
#    @property
#    def ymin(self):
#        return yminf(self._root)
#
#    @property
#    def xmax(self):
#        return xmaxf(self._root)
#
#    @property
#    def ymax(self):
#        return ymaxf(self._root)
#
#    @property
#    def height(self):
#        return heightf(self._root)
#
#    @property
#    def empty(self):
#        return len(childrenf(self._root)) == 0

    def insert(self, xmin, ymin, xmax, ymax, data=None):
        """
        Insert element(s)

        'xmin,ymin,xmax,ymax' may be arrays either numpy arrays (same size N),
        or scalars (to insert one item)

        Input:
         - xmin : scalar or array-like
         - ymin : scalar or array-like
         - xmax : scalar or array-like
         - ymax : scalar or array-like
         - data : None or array-like

        Output:
         - self : RBush
        """
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

        if data is None:
            data = [None]*len(xmin)

        if not len(xmin) == len(ymin) == len(xmax) == len(ymax) == len(data):
            msg = ("Error: Arguments 'xmin','ymin','xmax','ymax','data'"
                   "have different lengths")
            raise ValueError(msg)

        root = insert(self._root, xmin, ymin, xmax, ymax, data,
                      maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def load(self, arr, data=None):
        """
        Load 'arr' array into tree

        'arr' array  may be either a numpy array of shape (N,4), numpy record
        array or pandas dataframe with columns 'xmin,ymin,xmax,ymax', or
        a list of lists (internal lists being 4 elements long).

        If 'data' is given, it is expected to be an array with N elements

        Input:
         - arr  : numpy.ndarray of shape (N,4)
         - data : numpy.ndarray of shape (N,)

        Output:
         - self : RBush
        """
        if arr is None or len(arr) == 0:
            raise ValueError('Array must be non-zero length')

        if data is not None and len(data) != len(arr):
            msg = ("Error: Arguments 'arr','data' have different lengths")
            raise ValueError(msg)

        if not data:
            data = np.arange(len(arr))

        if not isinstance(arr, np.ndarray):
            msg = "expected a numpy.ndarray, instead {} was given".format(type(arr))
            raise ValueError(msg)

        ncols = arr.shape[1]
        if ncols < 4:
            msg = ("Error: 'arr' shape mismatch, was expecting 4 coluns")
            raise ValueError(msg)

        # change numba function to have "run_" prefix to set about self.load,
        # folks are reading the api docs or code
        root = run_load(self._root, arr,
                    maxentries=self.maxentries, minentries=self.minentries)

        self._root = root
        self.boxes = arr
        self.data = data
        return self

    def search(self, xmin, ymin, xmax, ymax):
        """
        Return items contained by or intersecting with 'xmin,ymin,xmax,ymax'
        """
        # change numba function to have "run_" prefix to set about self.load,
        # folks are reading the api docs or code
        #print(search.inspect_types())
        return run_search(self._root, xmin, ymin, xmax, ymax)


def run_load(root, data, maxentries, minentries):
    """
    Bulk insertion of items from 'data'

    'data' is expected to be a numerical array of (N,4) dimensions,
    or an array of named objects with columns 'xmin,ymin,xmax,ymax'
    """
    # If data is empty or None, do nothing
    if data is None or len(data) == 0:
        return root

    # If data is small ( < minimum entries), just insert one-by-one
    if len(data) < minentries:
        assert False
        if data.shape[1] == 5:
            xmin, ymin, xmax, ymax, data = data.T
        else:
            xmin, ymin, xmax, ymax = data.T
            data = [None]*len(xmin)
        return insert(root, xmin, ymin, xmax, ymax, data,
                      maxentries=maxentries, minentries=minentries)

    # recursively build the tree with the given data
    # from scratch using OMT algorithm
    node = build_tree(data, 0, len(data)-1, maxentries, minentries)

    if root.children.size == 0:
        # save as is if tree is empty
        root = node
#    elif (heightf(root) == heightf(node)):
#        # split root if trees have the same height
#        children = list()
#        children.append(root)
#        children.append(node)
#        bbox = calc_bbox(children)
#        root = create_node(bbox, children=children, leaf=False, height=heightf(node)+1)
#    else:
#        if heightf(root) < heightf(node):
#            # swap trees if inserted one is bigger
#            tmpNode = root
#            root = node
#            node = tmpNode
#        # insert the small tree into the large tree at appropriate level
#        level = heightf(root) - heightf(node) - 1
#        root = insert_node(root, node, level, True)
    else:
        assert False
    return root

def build_tree(data, first, last, maxentries, minentries, height=None):
    """
    Build RBush from 'data' items between 'first','last' (inclusive)
    """
    N = last - first + 1
    M = maxentries

    if N <= M:
        children = Stack()
        for i in range(first, last+1):
            item = create_item(data[i], i)
            children.push(item)
        bbox = calc_bbox(children)
        node = create_node(bbox, children=children, leaf=True, height=1)
        return node

    if height is None:
        # target height of the bulk-loaded tree
        height = math.ceil(math.log(N) / math.log(M))

        # target number of root entries to maximize storage utilization
        M = math.ceil(N / math.pow(M, height - 1))

    # split the data into M mostly square tiles
    N2 = math.ceil(N / M)
    N1 = N2 * math.ceil(math.sqrt(M))

    multiselect(data, first, last, N1, 0)

    children = Stack()
    for i in range(first, last+1, N1):
        last2 = min(i + N1 - 1, last)
        multiselect(data, i, last2, N2, 1)
        for j in range(i, last2+1, N2):
            last3 = min(j + N2 - 1, last2)
            # pack each entry recursively
            child = build_tree(data, first=j, last=last3,
                                       height=height - 1,
                                       maxentries=maxentries,
                                       minentries=minentries)
            children.push(child)

    bbox = calc_bbox(children)
    node = create_node(bbox, leaf=False, height=height, children=children)
    return node


def multiselect(data, first, last, n, column):
    stack = [first, last]
    mid = None
    while len(stack):
        first = stack.pop(0)
        last = stack.pop(0)
        if (last - first) <= n:
            continue
        mid = first + math.ceil((last - first) / n / 2) * n
        quicksort(data, first, last, column)
        stack.extend([first, mid, mid, last])


def quicksort(data, first, last, column):
    idx = np.argsort(data[first:last, column], kind='quicksort')
    idx += first


@nb.njit
def calc_bbox(children):
    xmin = INF
    xmax = -INF
    ymin = INF
    ymax = -INF
    for i in range(0, children.size):
        child = children.get(i)
        xmin = min(xmin, child.bbox[0])
        ymin = min(ymin, child.bbox[1])
        xmax = max(xmax, child.bbox[2])
        ymax = max(ymax, child.bbox[3])
    return np.array((xmin, ymin, xmax, ymax))


@nb.njit
def run_search(root_node, xmin, ymin, xmax, ymax):

    if root_node is None:
        raise ValueError('Root node must be non-null')

    nodes_to_search = Stack()
    nodes_to_search.push(root_node)

    items = Stack()
    while nodes_to_search.size > 0:

        node = nodes_to_search.pop()

        xminfv = node.bbox[0]
        yminfv = node.bbox[1]
        xmaxfv = node.bbox[2]
        ymaxfv = node.bbox[3]

        # intersects
        node_lower_bbox = xminfv <= xmax and yminfv <= ymax
        node_upper_bbox = xmaxfv >= xmin and ymaxfv >= ymin
        does_intersect = node_lower_bbox and node_upper_bbox

        if not does_intersect:
            continue

        # contains
        bbox_lower_node = xmin <= xminfv and ymin <= yminfv
        bbox_upper_node = xmaxfv <= xmax and ymaxfv <= ymax
        does_contain = bbox_lower_node and bbox_upper_node

        if not does_contain:
            if node.children is None:
                #items.push(node.data)
                items.push(node)
            else:
                for i in range(node.children.size):
                    child = node.children.get(i)
                    nodes_to_search.push(child)
        else:
            nodes = Stack()
            nodes.push(node)
            while nodes.size > 0:
                anode = nodes.pop()
                if anode.children is None:
                    #items.push(anode.data)
                    items.push(anode)
                elif anode.leaf:
                    for i in range(anode.children.size):
                        child = anode.children.get(i)
                        #items.push(child.data)
                        items.push(child)
                else:
                    for i in range(anode.children.size):
                        cnode = anode.children.get(i)
                        nodes.push(cnode)
    return items



