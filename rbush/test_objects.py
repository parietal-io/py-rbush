from collections import namedtuple
import numba

# 'timeit' to see (roughly) what are the timings to create basic objects...

class A(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

def create_object():
    return A(1,1)


b_type = numba.deferred_type()
spec = [('x', numba.int32),
        ('y', numba.int32)]
@numba.jitclass(spec)
class B(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
b_type.define(B.class_type.instance_type)

def create_numba():
    return B(1,1)


C = namedtuple('C', ['x', 'y'])

def create_tuple():
    return B(1,1)
