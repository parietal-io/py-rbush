from numba import deferred_type,optional
from numba import int32
from numba import jitclass

list_type = deferred_type()

node_type = deferred_type()
spec = [
    ('data',int32),
    ('children',optional(list_type))
]
@jitclass(spec)
class Node(object):
    def __init__(self,data):
        self.data = data
        self.children = None
node_type.define(Node.class_type.instance_type)


spec = [
    ('node',node_type),
    ('next',optional(list_type))
]
@jitclass(spec)
class List(object):
    def __init__(self,node,next):
        self.node = node
        self.next = next
list_type.define(List.class_type.instance_type)
