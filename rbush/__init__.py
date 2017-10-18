# from index import *

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

def createNode(children=None,data=None):
    node = _node.copy()
    for l in Box:
        node[l] = item[l]
    node['height'] = 1
    node['leaf'] = not children
    node['children'] = children
    node['data'] = data
    return node
