from ._python import *
# from ._numba import *
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

        if data is None:
            data = [None]*len(xmin)

        if not len(xmin) == len(ymin) == len(xmax) == len(ymax) == len(data):
            msg = ("Error: Arguments 'xmin','ymin','xmax','ymax','data'"
                   "have different lengths")
            print(msg)
            return root

        root = insert(self._root, xmin, ymin, xmax, ymax, data,
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
        if data is not None and len(data) != len(arr):
            msg = ("Error: Arguments 'arr','data' have different lengths")
            print(msg)
            return root

        ncols = arr.shape[1]
        if ncols < 4:
            msg = ("Error: 'arr' shape mismatch, was expecting 4 coluns")
            print(msg)
            return root

        if data is not None:
            arr = np.concatenate([arr[:,:4], data], axis=1)
        else:
            if ncols == 4:
                data = np.empty((len(arr), 1), dtype=object)
                arr = np.concatenate([arr, data], axis=1)

        root = load(self._root, arr,
                    maxentries=self.maxentries, minentries=self.minentries)
        self._root = root
        return self

    def load_dataframe(self, df):
        """
        Load a pandas dataframe
        """
        cols = ['xmin', 'ymin', 'xmax', 'ymax']
        cols.extend(c for c in df.columns if c not in cols)
        df = df.reindex_axis(cols, axis=1, copy=False)

        return self.load(np.asarray(df))

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
