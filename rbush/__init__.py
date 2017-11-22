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

    def insert(self, xmin, ymin, xmax, ymax, data=None):
        """
        Insert element(s) in the tree

        'xmin,ymin,xmax,ymax' (and data) may be arrays, if so, `RBush.load`
        function is used instead. As in `RBush.load`, if 'data' is given it
        must be an array with length equal to 'xmin,ymin,xmax,ymax'.

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

        if not len(xmin) == len(ymin) == len(xmax) == len(ymax):
            msg = ("Error: Arguments 'xmin','ymin',"
                   "'xmax','ymax' have different lengths")
            print(msg)
            return self

        root = insert(self._root, xmin, ymin, xmax, ymax,  # data,
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
         - arr  : numerical array-like of shape (N,4)
         - data : array-like of shape (N,)

        Output:
         - self : RBush
        """
        root = load(self._root, arr,
                    maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def all(self):
        """
        Return a list of all items (leaves) from RBush
        """
        return retrieve_all_items(self._root)

    def search(self, xmin, ymin, xmax, ymax):
        """
        Return items contained by or intersecting with 'xmin,ymin,xmax,ymax'
        """
        return search(self._root, xmin, ymin, xmax, ymax)
