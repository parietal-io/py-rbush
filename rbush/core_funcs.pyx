# cython: linetrace=True
# cython: binding=True

cimport cython

import itertools

from libc.float cimport DBL_MAX as Dfloat_max, DBL_MIN as Dfloat_min

ctypedef double Dfloat
ctypedef unsigned Duint

cdef class _Node(object):
    cdef:
        _Node parent
        list records
        bint is_leaf

    def __cinit__(self, _Node parent):
        self.parent = parent
        self.records = list()

    cdef _Node copy(self, _Node parent):
        cdef:
            _Node ret
        ret = _Node(parent)
        ret.records = [ (<_Record>rec).copy(ret) for rec in self.records ]
        ret.is_leaf = self.is_leaf
        return ret

    cdef inline void common_boundaries(self, Dfloat *target):
        common_boundaries(self.records, target)

    cdef inline _Record choose_subtree_least_enlargement(self, _Record ir):
        cdef:
            Dfloat least_enlargement, enlagrgement, current_area, target_area
            Dfloat combined_rectangle[4]
            _Record current_record, target
            list records

        init_Dfloat4(combined_rectangle)

        target_area = least_enlargement = Dfloat_max
        records = [ir, None]

        for current_record in self.records:
            current_area = area(current_record.coords)

            records[1] = current_record

            common_boundaries(records, combined_rectangle)
            enlagrgement = area(combined_rectangle) - current_area

            if enlagrgement < least_enlargement:
                target = current_record
                target_area = area(current_record.coords)
                least_enlargement = enlagrgement
            elif enlagrgement == least_enlargement and current_area < target_area:
                target = current_record
                least_enlargement = target_area = current_area

        return target

    cdef void find_overlapping_leafs_recursive(self, list result, Dfloat *coords):
        cdef:
            _InnerRecord record

        if self.is_leaf:
            result.append(self)
        else:
            for record in self.records:
                if record.overlaps(coords):
                    record.child.find_overlapping_leafs_recursive(result, coords)

    cdef void addChild(self, _Node node):
        cdef:
            _InnerRecord ir

        node.parent = self
        ir = _InnerRecord(node)
        node.common_boundaries(ir.coords)
        self.records.append(ir)

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        content = dict(is_leaf=self.is_leaf)
        records = list()
        for r in self.records:
            records.append(r.to_dict())
        content['records'] = records
        return content

cdef class _Record:
    cdef:
        Dfloat coords[4]

    cdef inline bint overlaps(self, Dfloat *rect):
        return self.coords[0] < rect[2] and self.coords[2] > rect[0] \
               and self.coords[1] < rect[3] and self.coords[3] > rect[1]

    cdef inline void copy_coords_to(self, Dfloat *coords):
        for i in range(4):
            coords[i] = self.coords[i]

    cdef _Record copy(self, _Node newparent):
        raise NotImplemented

cdef class _ChildRecord(_Record):
    cdef:
        object identifier

    def __init__(self, object identifier):
        self.identifier = identifier

    cdef _Record copy(self, _Node newparent):
        cdef:
            _ChildRecord ret

        ret = _ChildRecord(self.identifier)
        self.copy_coords_to(ret.coords)
        return ret

    def to_dict(self):
        content = dict(identifier=self.identifier, coords=self.coords)
        return content

cdef class _InnerRecord(_Record):
    cdef:
        _Node child

    def __cinit__(self, _Node child):
        self.child = child

    cdef _Record copy(self, _Node newparent):
        cdef:
            _InnerRecord ret

        ret = _InnerRecord(self.child.copy(newparent))
        self.copy_coords_to(ret.coords)
        return ret

    def to_dict(self):
        content = dict(coords=self.coords)
        content['child'] = self.child.to_dict()
        return content

# cdef class RTree

def create_root():
    cdef:
        _Node root
    root = _Node(None)
    root.is_leaf = True
    return root


@cython.profile(False)
def insert(_Node root, object coords, object key, int M_Cap, int m_cap):
    '''Insert an item.

    @param key: an object to insert, where all keys should be unique (regarding !=)
    @param coords: 2D coordinates
    '''

    cdef:
        _ChildRecord cr
        _Node L

    if not isinstance(coords, (list, tuple)):
        raise TypeError('coordinates as list or tuple expected, got %s' % coords.__class__)
    if not len(coords) == 4:
        raise TypeError('len(coords) must be 4, length is %d' % len(coords))

    cr = _ChildRecord(key)
    tuple_to_array(coords, cr.coords)

    L = _ChooseLeaf(root, cr)

    root_aux = insert_at_node(cr, L, M_Cap, m_cap)

    # self._node_cnt += 1

    if root_aux is not None:
        return root_aux
    return root


@cython.profile(False)
cdef inline _Node _ChooseLeaf(_Node root, _Record ir):
    cdef:
        _Node N
        _InnerRecord F

    N = root
    while True:
        if N.is_leaf:
            break
        r = N.choose_subtree_least_enlargement(ir)
        N = (<_InnerRecord>r).child
    return N

cdef inline _Record choose_subtree_least_enlargement(_Node anode, _Record ir):
    cdef:
        Dfloat least_enlargement, enlargement, current_area, target_area
        Dfloat combined_rectangle[4]
        _Record current_record, target
        list records

    init_Dfloat4(combined_rectangle)

    target_area = least_enlargement = Dfloat_max
    records = [ir, None]

    for current_record in anode.records:
        current_area = area(current_record.coords)

        records[1] = current_record

        common_boundaries(records, combined_rectangle)
        enlargement = area(combined_rectangle) - current_area

        if enlargement < least_enlargement:
            target = current_record
            target_area = area(current_record.coords)
            least_enlargement = enlargement
        elif enlargement == least_enlargement and current_area < target_area:
            target = current_record
            target_area = current_area
            least_enlargement = current_area

    return target


@cython.profile(False)
cdef inline _Node insert_at_node(_Record r, _Node L, int M_cap, int m_cap):
    cdef:
        _Node LL
        _Node root # new root, in case we need

    # Right now, LL and root are pretty redundant, but will change soon
    LL = None
    root = None

    if is_full(M_cap, L):
        LL = SplitNode(L, r, m_cap)
    else:
        L.records.append(r)

    L, LL = _AdjustTree(L, LL, M_cap, m_cap)

    if LL != None:
        root = _Node(None)
        root.addChild(L)
        root.addChild(LL)
        # tree._leaf_level += 1

    return root

cdef inline _InnerRecord parent_record(_Node node):
    cdef:
        _InnerRecord e

    for e in node.parent.records:
        if e.child == node:
            return e

cdef inline bint is_full(int M_cap, _Node node):
    return len(node.records) == M_cap

@cython.profile(False)
cdef inline tuple _AdjustTree(_Node L, _Node LL, int M_cap, int m_cap):
    cdef:
        _Node N, NN, P
        _Record EN, e

    N = L
    NN = LL

    while N.parent != None:
        P = N.parent

        # search for the entry in parent of N that holds N
        EN = parent_record(N)

        assert EN != None, 'no parent entry holds the child'

        N.common_boundaries(EN.coords)

        if NN != None:
            ENN = _InnerRecord(NN)
            NN.common_boundaries(ENN.coords)
            if not is_full(M_cap, P):
                P.records.append(ENN)
                NN = None
            else:
                NN = SplitNode(P, ENN, m_cap)

        N = P

    return (N, NN)

@cython.profile(False)
cdef _Node SplitNode(_Node node, _Record ir, int m_cap):
    cdef:
        list remaining
        _Node newnode
        unsigned remaining_count
        _InnerRecord r

    remaining = node.records
    remaining.append(ir)
    node.records = list()

    newnode = _Node(node.parent)

    PickSeeds(node, remaining, newnode)

    remaining_count = len(remaining)
    while remaining_count > 0:
        if len(node.records) + remaining_count - 1 < m_cap:
            node.records.extend(remaining)
            break
        if len(newnode.records) + remaining_count - 1 < m_cap:
            newnode.records.extend(remaining)
            break

        PickNext(node, remaining, newnode)
        remaining_count -= 1

    if node.is_leaf:
        newnode.is_leaf = True
    else:
        # child records are inner records - re-set parent of them to newnode
        for r in newnode.records:
            r.child.parent = newnode

    return newnode

cdef int PickSeeds(_Node node, list remaining, _Node newnode) except -1:
    cdef:
        Dfloat d, d_max
        Dfloat E1_E2[4]
        Dfloat J, a_E1, a_E2
        _Record E1_ret, E2_ret
        list combi

    init_Dfloat4(E1_E2)

    combi = [None, None]
    d_max = -Dfloat_max

    for E1, E2 in itertools.combinations(remaining, 2):

        combi[0] = E1
        combi[1] = E2

        common_boundaries(combi, E1_E2)
        J = area(E1_E2)
        a_E1 = area((<_Record>E1).coords)
        a_E2 = area((<_Record>E2).coords)
        d = J - a_E1 - a_E2

        if d > d_max:
            E1_ret = E1
            E2_ret = E2

    remaining.remove(E1_ret)
    remaining.remove(E2_ret)

    node.records = [E1_ret]
    newnode.records = [E2_ret]

    return 0

cdef inline int PickNext(_Node node, list remaining, _Node newnode) except -1:
    cdef:
        Dfloat area_group_L, area_group_LL
        Dfloat d1_next, d2_next # for QS3 decision
        Dfloat d1, d2, d_diff, d_diff_max
        Dfloat coords[4]
        _Record E_next, E, r

    area_group_L = 0
    area_group_LL = 0
    d1_next = 0
    d2_next = 0
    init_Dfloat4(coords)

    if len(remaining) == 1:
        E_next = remaining.pop()
    else:
        for r in node.records:
            area_group_L += area(r.coords)

        for r in newnode.records:
            area_group_LL += area(r.coords)

        d_diff_max = -Dfloat_min

        node.records.append(None)
        newnode.records.append(None)

        for E in remaining:

            # temporary add E to self.records / newnode.records as parameter for common_boundires()
            # -> don't init a new list of records
            node.records[-1] = E
            newnode.records[-1] = E

            common_boundaries(node.records, coords)
            d1 = area(coords) - area_group_L

            common_boundaries(newnode.records, coords)
            d2 = area(coords) - area_group_LL

            d_diff = d1 - d2
            d_diff = d_diff if d_diff >= 0 else -d_diff # abs diff

            if d_diff > d_diff_max:
                d_diff_max = d_diff
                E_next = E

                d1_next = d1
                d2_next = d2

        node.records.pop()
        newnode.records.pop()

        remaining.remove(E_next)

    # QS3
    if d1_next < d2_next:
        node.records.append(E_next)
    elif d1_next > d2_next:
        newnode.records.append(E_next)
    elif len(node.records) > len(newnode.records):
        newnode.records.append(E_next)
    else:
        node.records.append(E_next)





def search(tree, object coords):
    '''Search overlapping items.

    @param coords: list or tuple of four values that make a rectangle
    @return: a list of identifiers whose coordinates overlap with coords
    '''
    cdef:
        _Node node
        _ChildRecord cr
        Dfloat coords_a[4]
        list leafnodes, result

    if not isinstance(coords, (list, tuple)):
        raise TypeError('coordinates as list or tuple expected, got %s' % coords.__class__)

    if len(coords) != 4:
        raise TypeError('len(coords) must be 4, len is %d' % len(coords))

    tuple_to_array(coords, coords_a)

    leafnodes = find_overlapping_leafs(tree, coords_a)

    result = []
    for node in leafnodes:
        assert node.is_leaf
        for cr in node.records:
            if cr.overlaps(coords_a):
                result.append(cr.identifier)

    return result


cdef list find_overlapping_leafs(_Node root, Dfloat *coords):
    cdef:
        _Record rec
        list result

    # don't know the whole surrounding rectangle of root, ask records for overlapping
    for rec in root.records:
        if rec.overlaps(coords):
            break
    else:
        return []

    result = list()
    root.find_overlapping_leafs_recursive(result, coords)
    return result

cdef void tuple_to_array(object t, Dfloat *coords):
    for i in range(4):
        coords[i] = <Dfloat>t[i]
    #make_order(coords)

cdef inline void make_order(Dfloat *coords):
    cdef Dfloat switch
    if coords[0] > coords[2]:
        switch = coords[0]
        coords[0] = coords[2]
        coords[2] = switch
    if coords[1] > coords[3]:
        switch = coords[1]
        coords[1] = coords[3]
        coords[3] = switch

cdef inline void init_Dfloat4(Dfloat *f):
    # array initialization - compiler cries if we don't do that
    f[0] = 0
    f[1] = 0
    f[2] = 0
    f[3] = 0

cdef inline Dfloat area(Dfloat *coords):
    return (coords[2] - coords[0]) * (coords[3] - coords[1])

cdef inline void common_boundaries(list records, Dfloat *target):
    cdef:
        Dfloat *coords
        _Record r

    target[0] = target[1] = Dfloat_max
    target[2] = target[3] = -Dfloat_min
    for r in records:
        coords = r.coords
        target[0] = min(target[0], coords[0])
        target[1] = min(target[1], coords[1])
        target[2] = max(target[2], coords[2])
        target[3] = max(target[3], coords[3])
