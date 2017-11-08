from numba import deferred_type,optional
from numba import int32
from numba import jitclass,njit,jit

list_type = deferred_type()

spec = [
    ('data',int32),
    ('next',optional(list_type))
]
@jitclass(spec)
class List(object):
    def __init__(self,data,next):
        self.data = data
        self.next = next
list_type.define(List.class_type.instance_type)

@njit
def length(stack):
    i = 0
    while stack is not None:
        stack = stack.next
        i+=1
    return i

# @njit(optional(list_type,int32))
@njit
def remove(stack,index):
    # if index >= length(stack):
    #     return None
    if index == 0:
        return stack.next
    cur = stack
    i = 0
    while cur is not None:
        if index == i:
            break
        i = i+1
        prev = cur
        cur = cur.next
    prev.next = cur.next
    return stack

@njit
def push(stack, data):
    return List(data, stack)


if __name__ == '__main__':
    from numpy.random import randint
    from numpy.random import shuffle
    a = randint(0,100,10)

    list_ = None

    for n in a:
        list_ = push(list_,n)
    print(length(list_))

    indexes = list(range(len(a)))
    for i in indexes[::-1]:
        list_ = remove(list_,i)
    print(length(list_))
