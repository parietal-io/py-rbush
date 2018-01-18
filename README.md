This library is extremely alpha.  DO NOT USE for anything besides test / dev. We are still optimizing the library...so hold off for now.
-------

# Mission
The mission of RBush is to provide a performant, thread-safe RTree implementation for Python which
does not have `libspatialindex` or `geos` as a dependencies.

# Installation
```bash
conda install -c parietal.io rbush
```

# py-rbush
Python port of JS rbush library

## Tests

To run the (unit) tests, type:

```bash
$ pytest rbush
```

or

```python
>>> import rbush
>>> rbush.test()
```


## Performance

As in [JS rbush](https://github.com/mourner/rbush),
the following sample performance test was done by generating
random uniformly distributed rectangles of ~0.01% area and setting `maxEntries` to `16`
(see `benchmark.py` script).
Performed with Python 3.6.1 on a Intel-i7 1.9GHz.

Test                         | RBush(naive) | RBush(numba,v0.0.1) | RBush(numpy,v0.0.2)
---------------------------- | ------------ | ------------------- | -------------------
insert 1M items one by one   | 224.9s       | 834.8s              | 251.4s
1000 searches of 0.01% area  | 5.30s        | 79.1s               | 7.5s
1000 searches of 1% area     | 13.5s        | 277.6s              | 8.1s
1000 searches of 10% area    | 47.6s        | 935.7s              | 16.5s
remove 1000 items one by one | 2.61s        | 9.56s               | 7.3s
bulk-insert 1M items         | 63.7s        | 101.1s              | 25.1s


## Changelog

### 0.0.2 -- Dec 12, 2017

* `insert` accepts arrays for `xmin, xmax, ymin, ymax`
* `load` receives a numpy array
