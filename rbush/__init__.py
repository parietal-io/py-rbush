from .index import *

from collections import defaultdict
_node = defaultdict(None)

Box = ["minX","maxX","minY","maxY"]
Point = ["X","Y"]

def createBox(item):
    box = _node
    for l in Box:
        box[l] = item[l]
    return box

def pointBox(item):
    bbox = _node
    for l in Box:
        c = "X" if "X" in l else "Y"
        bbox[l] = item[c]
    return bbox
