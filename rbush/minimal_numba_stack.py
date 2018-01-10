from collections import OrderedDict

import numba as nb

import numpy as np
INF = np.iinfo(np.int64).max


node_type = nb.deferred_type()
linkednode_type = nb.deferred_type()
stack_type = nb.deferred_type()


# Define the nodes of our tree
node_spec = OrderedDict()
node_spec['bbox'] = nb.int64[:]
node_spec['data'] = nb.optional(nb.int64)
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
def create_node(bbox, data=None, leaf=None, height=None, children=None):
    if children is None:
        children = Stack()
    node = Node(bbox, data, leaf, height, children)
    return node


# @nb.jit
def create_root(children=None, height=1, leaf=True):
    bbox = np.array([INF, INF, -INF, -INF], dtype=int)
    return create_node(bbox, leaf=leaf, height=height, children=children)


def create_tree():
    data = np.asarray([[1,2,1,2],
                       [2,3,2,3],
                       [3,5,3,5],
                       [5,7,6,8],
                       [5,6,5,6],
                       [6,8,6,8]], dtype=int)

    bbox1 = np.array([1,3,1,3], dtype=int)
    node1 = create_node(bbox1, leaf=True)
    item0 = create_node(data[0], data=0)
    node1.children.push(item0)
    item1 = create_node(data[1], data=1)
    node1.children.push(item1)

    bbox2 = np.array([3,5,3,5], dtype=int)
    node2 = create_node(bbox2, leaf=True)
    item2 = create_node(data[2], data=2)
    node2.children.push(item2)

    bbox3 = np.array([5,9,5,9], dtype=int)
    node3 = create_node(bbox3, leaf=True)
    item3 = create_node(data[3], data=3)
    node3.children.push(item3)
    item4 = create_node(data[4], data=4)
    node3.children.push(item4)
    item5 = create_node(data[5], data=5)
    node3.children.push(item5)

    root = create_root(leaf=False)
    root.children.push(node1)
    root.children.push(node2)
    root.children.push(node3)

    return root


@nb.njit
def get_all(root_node):

    nodes_to_search = Stack()
    nodes_to_search.push(root_node)

    items = Stack()
    while nodes_to_search.size > 0:
        # print(nodes_to_search.size)

        node = nodes_to_search.pop()

        if not node.leaf:
            for i in range(node.children.size):
                child = node.children.get(i)

                nodes_to_search.push(child)

        else:
            for i in range(node.children.size):
                item = node.children.get(i)
                items.push(item)

    return items


def runme():
    from time import time
    root = create_tree()
    items = get_all(root)

    tic = time()
    for _ in range(100):
        # root = create_tree()
        items = get_all(root)
    tac = time()
    print("Time:", tac-tic)

    data = []
    for _ in range(items.size):
        item = items.pop()
        data.append(item.data)
    print(data)


if __name__ == '__main__':
    runme()
