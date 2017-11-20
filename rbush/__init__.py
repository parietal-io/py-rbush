from .core import *
from .tree import *

MAXENTRIES = 9
MINENTRIES = int(9*0.4)


class RBush(object):
    def __init__(self, maxentries=None, minentries=None):
        self.maxentries = maxentries or MAXENTRIES
        self.minentries = minentries or MINENTRIES
        self._root = self._create_root()

    def _create_root(self):
        children = list()
        return create_node(leaf=True, height=1, children=children)

    def insert(self, xmin, ymin, xmax, ymax, data=0):
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

        if not len(xmin) == len(ymin) == len(xmax) == len(ymax):
            msg = ("Error: Arguments 'xmin','ymin',"
                   "'xmax','ymax' have different lengths")
            print(msg)
            return self

        root = insert(self._root, xmin, ymin, xmax, ymax,  # data,
                      maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def load(self, data_array):
        root = load(self._root, data_array,
                    maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def all(self):
        return retrieve_all_items(self._root)

    def search(self, xmin, ymin, xmax, ymax):
        return search(self._root, xmin, ymin, xmax, ymax)
