# from ._python import *

import numpy as np
import numba as nb

# INF = np.iinfo(np.int64).max
INF = np.inf

# node_type = nb.deferred_type()
# list_type = nb.deferred_type()
# stack_type = nb.deferred_type()
#
# node_spec = [
#     ('xmin', nb.float64),
#     ('ymin', nb.float64),
#     ('xmax', nb.float64),
#     ('ymax', nb.float64),
#     ('data', nb.optional(nb.int32)),
#     ('leaf', nb.optional(nb.boolean)),
#     # ('height', nb.optional(nb.int16)),
#     ('children', nb.optional(list_type))
# ]
# @nb.jitclass(node_spec)
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
# node_type.define(RBushNode.class_type.instance_type)


def create_node(xmin=INF, ymin=INF, xmax=-INF, ymax=-INF,
                data=None, leaf=None, height=None, children=None):
    node = RBushNode(xmin, ymin, xmax, ymax)
    node.data = data
    node.leaf = leaf
    node.height = height
    node.children = children
    return node


# stack_spec = [
#     ('data', node_type),
#     ('next', nb.optional(stack_type))
# ]
# @nb.jitclass(stack_spec)
class Stack(object):
    def __init__(self, data, next):
        self.data = data
        self.next = next
# stack_type.define(Stack.class_type.instance_type)


# list_spec = [
#     ('_size', nb.int32),
#     ('_stack', nb.optional(stack_type))
# ]
# @nb.jitclass(list_spec)
class List(object):
    def __init__(self):
        self._size = 0
        self._stack = None

    def size(self):
        return self._size

    def append(self, data):
        if self._stack is None:
            self._stack = Stack(data, None)
        else:
            cursor = self._stack
            while cursor.next is not None:
                cursor = cursor.next
            cursor.next = Stack(data, None)
        self._size += 1

    def prepend(self, data):
        stack = self._stack
        self._stack = Stack(data, stack)
        self._size += 1

    # def append(self, data):
    #     stack = self._stack
    #     self._stack = Stack(data, stack)
    #     self._size += 1

    def get(self, index=0):
        if index >= self.size():
            return None
        cursor = self._stack
        for i in range(index):
            cursor = cursor.next
        return cursor.data

    def pop(self, index=0):
        if index >= self.size():
            return None
        cursor = self._stack
        if index == 0:
            self._stack = cursor.next
        else:
            parent = None
            for i in range(index):
                cursor = cursor.next
                parent = cursor
            parent.next = cursor.next
        self._size -= 1
        return cursor.data

    def sort(self, key=None):
        self._stack = sort(self._stack, key)

# list_type.define(List.class_type.instance_type)


def list():
    return List()


def len(children):
    return children.size()


def get(children, index):
    return children.get(index)
###################
### NOT WORKING ###
###################
def sort(stack, key=None):
    len_ = length(stack)
    if len_==1:
        return stack
    halfsize = int(len_/2)
    odd = int(len_%2)
    _,right = splice(stack,0,halfsize)
    _,left = splice(stack,halfsize,halfsize+odd)
    left = sort(left)
    right = sort(right)
    out = None
    i = 0
    j = 0
    while i<length(left) and j<length(right):
        iv = get(left,i)
        jv = get(right,j)
        if compare(iv) <= compare(jv):
            out = push(out,iv)
            i+=1
        else:
            out = push(out,jv)
            j+=1
    while i < length(left):
        iv = get(left,i)
        out = push(out,iv)
        i+=1
    while j < length(right):
        jv = get(right,j)
        out = push(out,jv)
        j+=1
    return out
