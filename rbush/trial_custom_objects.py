class Stack(object):
    def __init__(self, data, next=None):
        self.data = data
        self.next = next


class List(object):
    def __init__(self, data):
        self._stack = Stack(data, None)
        self._size = 1

    @property
    def size(self):
        return self._size

    def append(self, data):
        cursor = self._stack
        while cursor.next is not None:
            cursor = cursor.next
        cursor.next = Stack(data)
        self._size += 1

    def prepend(self, data):
        stack = self._stack
        self._stack = Stack(data, stack)
        self._size += 1

    def get(self, index=0):
        if index >= self.size:
            return None
        cursor = self._stack
        for i in range(index):
            cursor = cursor.next
        return cursor.data

    def pop(self, index=0):
        if index >= self.size:
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


def len(children):
    return children.size


def get(children, index):
    return children.get(index)
