import numba as nb
import numpy as np
INF = np.iinfo(np.int64).max


node_type = nb.deferred_type()
stack_type = nb.deferred_type()

node_spec = [
    ('bbox', nb.int64[:]),
    ('data', nb.optional(nb.int32)),
    ('leaf', nb.optional(nb.boolean)),
    ('height', nb.optional(nb.int16)),
    ('children', nb.optional(stack_type))
]
@nb.jitclass(node_spec)
class Node(object):
    def __init__(self, bbox, data, leaf, height, children):
        self.bbox = bbox
        self.data = data
        self.leaf = leaf
        self.height = height
        self.children = children

node_type.define(Node.class_type.instance_type)


stack_spec = [
        ('node', node_type),
        ('next', nb.optional(stack_type)),
        ('valid', nb.boolean)
]
@nb.jitclass(stack_spec)
class Stack(object):
    def __init__(self, node, next):
        self.node = node
        self.next = next
        self.valid = True

stack_type.define(Stack.class_type.instance_type)

@nb.jit
def push(node, stack=None):
    return Stack(node, stack)

@nb.jit
def get(stack, i):
    ind = 0
    while stack is not None:
        if ind == i:
            return stack
        stack = stack.next
        ind+=1
    return stack

@nb.jit
def length(stack):
    cnt = 0
    while stack is not None and stack.valid == True:
        cnt+=1
        stack = stack.next
    return cnt


def create_node(bbox, data=None, leaf=None, height=None, children=None):
    node = Node(bbox, data, leaf, height, children)
    return node


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
    node1.children = push(item0, node1.children)
    item1 = create_node(data[1], data=1)
    node1.children = push(item1, node1.children)

    bbox2 = np.array([3,5,3,5], dtype=int)
    node2 = create_node(bbox2, leaf=True)
    item2 = create_node(data[2], data=2)
    node2.children = push(item2, node2.children)

    bbox3 = np.array([5,9,5,9], dtype=int)
    node3 = create_node(bbox3, leaf=True)
    item3 = create_node(data[3], data=3)
    node3.children = push(item3, node3.children)
    item4 = create_node(data[4], data=4)
    node3.children = push(item4, node3.children)
    item5 = create_node(data[5], data=5)
    node3.children = push(item5, node3.children)

    root = create_root(leaf=False)
    root.children = push(node1, root.children)
    root.children = push(node2, root.children)
    root.children = push(node3, root.children)

    return root


@nb.jit
def get_all(root_node):
    nodes_to_search = [root_node]
    items = []
    while len(nodes_to_search) > 0:
        print(len(nodes_to_search))

        node = nodes_to_search.pop()
        if not node.leaf:
            for i in range(length(node.children)):
                child = get(node.children, i)
                nodes_to_search.append(child.node)
        else:
            for i in range(length(node.children)):
                item = get(node.children, i)
                items.append(item.node.data)
    return items


def runme():
    root = create_tree()
    data = get_all(root)
    print(data)

if __name__ == '__main__':
    runme()
