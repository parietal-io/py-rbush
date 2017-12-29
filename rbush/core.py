from ._utils import RBJSONEncoder as _jsenc
from .tree import *

MAXENTRIES = 9
MINENTRIES = int(9*0.4)


class RBush(object):
    def __init__(self, maxentries=None, minentries=None):
        self.maxentries = maxentries or MAXENTRIES
        self.minentries = minentries or MINENTRIES
        self.clear()

    def clear(self):
        self._root = create_root()

    @property
    def xmin(self):
        return xminf(self._root)

    @property
    def ymin(self):
        return yminf(self._root)

    @property
    def xmax(self):
        return xmaxf(self._root)

    @property
    def ymax(self):
        return ymaxf(self._root)

    @property
    def height(self):
        return heightf(self._root)

    @property
    def empty(self):
        return len(childrenf(self._root)) == 0

    def insert(self, xmin, ymin, xmax, ymax, data=None):
        """
        Insert element(s)

        'xmin,ymin,xmax,ymax' may be arrays either numpy arrays (same size N),
        or scalars (to insert one item)

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
            return self

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
         - arr  : numpy.ndarray of shape (N,4)
         - data : numpy.ndarray of shape (N,)

        Output:
         - self : RBush
        """
        if arr is None or len(arr) == 0:
            raise ValueError('Array must be non-zero length')

        if data is not None and len(data) != len(arr):
            msg = ("Error: Arguments 'arr','data' have different lengths")
            raise ValueError(msg)

        if not isinstance(arr, np.ndarray):
            msg = "expected a numpy.ndarray, instead {} was given".format(type(arr))
            raise ValueError(msg)

        ncols = arr.shape[1]
        if ncols < 4:
            msg = ("Error: 'arr' shape mismatch, was expecting 4 coluns")
            raise ValueError(msg)

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
        items = retrieve_all_items(self._root)
        return map(np.asarray, zip(*items))

    def search(self, xmin, ymin, xmax, ymax):
        """
        Return items contained by or intersecting with 'xmin,ymin,xmax,ymax'
        """
        items = search(self._root, xmin, ymin, xmax, ymax)
        return map(np.asarray, zip(*items))

    def remove(self, xmin, ymin, xmax, ymax):
        """
        Remove and return removed items matching 'xmin,ymin,xmax,ymax'
        """
        items = remove(self._root, xmin, ymin, xmax, ymax)
        if self.empty:
            self.clear()
        return items

    def to_json(self, indent=2):
        return to_json(self._root, indent)


def to_json(node, indent=None):
    cont = to_dict(node)
    import json
    return json.dumps(cont, indent=indent, cls=_jsenc)


def to_dict(node):
    content = dict(xmin=xminf(node),
                   ymin=yminf(node),
                   xmax=xmaxf(node),
                   ymax=ymaxf(node))
    content['leaf'] = leaff(node)
    content['height'] = heightf(node)
    children = []
    if leaff(node) is False:
        for i in range(len(childrenf(node))):
            child = get(childrenf(node), i)
            children.append(to_dict(child))
    else:
        for i in range(len(childrenf(node))):
            child = get(childrenf(node), i)
            children.append(child)
    content['children'] = children
    return content
