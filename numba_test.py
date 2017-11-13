from numba import deferred_type,optional
from numba import int64
from numba import jitclass,njit,jit

list_type = deferred_type()

spec = [
    ('data',int64),
    ('next',optional(list_type))
]
@jitclass(spec)
class List(object):
    def __init__(self,data,next):
        self.data = data
        self.next = next

    def __str__(self):
        return '{!s}:{!r}'.format(self.data,self.next)

    def prepend(self, data):
        return List(data, self)

list_type.define(List.class_type.instance_type)

# @njit
def length(stack):
    i = 0
    while stack is not None:
        # print(i,stack)
        stack = stack.next
        i+=1
    return i

@jit
def remove(stack,index):
    prev = None
    if index == 0:
        stack = stack.next
    else:
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

def runme():
    from numpy.random import randint
    a = randint(0,100,10)
    # a = list(range(10,0,-1))

    list_ = None

    for n in a:
        if list_ is None:
            list_ = List(n,None)
        else:
            list_ = list_.prepend(n)
    # print('LEN:',length(list_))

    indexes = list(range(len(a)))
    # indexes = [2,0]
    for i in indexes[::-1]:
        list_ = remove(list_,i)
    # print('LEN:',length(list_))

if __name__ == '__main__':
    runme()
