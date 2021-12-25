from numbers import Integral
import operator

def _bitcount(val):
    return bin(val).count("1")

BRANCH_FACTOR = 32
BIT_MASK = BRANCH_FACTOR - 1
SHIFT = _bitcount(BIT_MASK)


def compare_pvector(v, other, operator):
    return operator(v.tolist(), other.tolist() if isinstance(other, PythonPVector) else other)


def _index_or_slice(index, stop):
    if stop is None:
        return index
    return slice(index, stop)


class PythonPVector(object):
    __slots__ = ('_count', '_shift', '_root', '_tail', '_tail_offset', '__weakref__')

    def __new__(cls, count, shift, root, tail):
        self = super(PythonPVector, cls).__new__(cls)
        self._count = count
        self._shift = shift
        self._root = root
        self._tail = tail
        self._tail_offset = self._count - len(self._tail)
        return self

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.start is None and index.stop is None and index.step is None:
                return self
            return _EMPTY_PVECTOR.extend(self.tolist()[index])

        if index < 0:
            index += self._count

        return PythonPVector._node_for(self, index)[index & BIT_MASK]

    def __add__(self, other):
        return self.extend(other)

    def __iter__(self):
        return iter(self.tolist())

    def _fill_list(self, node, shift, the_list):
        if shift:
            shift -= SHIFT
            for n in node:
                self._fill_list(n, shift, the_list)
        else:
            the_list.extend(node)

    def tolist(self):
        the_list = []
        self._fill_list(self._root, self._shift, the_list)
        the_list.extend(self._tail)
        return the_list

    def _totuple(self):
        return tuple(self.tolist())

    def __hash__(self):
        return hash(self._totuple())

    def set(self, i, val):
        if not isinstance(i, Integral):
            raise TypeError("Not index")

        if i < 0:
            i += self._count

        if 0 <= i < self._count:
            if i >= self._tail_offset:
                new_tail = list(self._tail)
                new_tail[i & BIT_MASK] = val
                return PythonPVector(self._count, self._shift, self._root, new_tail)

            return PythonPVector(self._count, self._shift, self._do_set(self._shift, self._root, i, val), self._tail)

        if i == self._count:
            return self.append(val)

        raise IndexError("Index out of range: %s" % (i,))

    def _do_set(self, level, node, i, val):
        ret = list(node)
        if level == 0:
            ret[i & BIT_MASK] = val
        else:
            sub_index = (i >> level) & BIT_MASK  # >>>
            ret[sub_index] = self._do_set(level - SHIFT, node[sub_index], i, val)

        return ret

    @staticmethod
    def _node_for(pvector_like, i):
        if 0 <= i < pvector_like._count:
            if i >= pvector_like._tail_offset:
                return pvector_like._tail

            node = pvector_like._root
            for level in range(pvector_like._shift, 0, -SHIFT):
                node = node[(i >> level) & BIT_MASK]  # >>>

            return node

        raise IndexError("Index out of range: %s" % (i,))

    def _create_new_root(self):
        new_shift = self._shift
        if (self._count >> SHIFT) > (1 << self._shift): # >>>
            new_root = [self._root, self._new_path(self._shift, self._tail)]
            new_shift += SHIFT
        else:
            new_root = self._push_tail(self._shift, self._root, self._tail)

        return new_root, new_shift

    def append(self, val):
        if len(self._tail) < BRANCH_FACTOR:
            new_tail = list(self._tail)
            new_tail.append(val)
            return PythonPVector(self._count + 1, self._shift, self._root, new_tail)
        new_root, new_shift = self._create_new_root()
        return PythonPVector(self._count + 1, new_shift, new_root, [val])

    def _new_path(self, level, node):
        if level == 0:
            return node

        return [self._new_path(level - SHIFT, node)]

    def _mutating_insert_tail(self):
        self._root, self._shift = self._create_new_root()
        self._tail = []

    def _mutating_fill_tail(self, offset, sequence):
        max_delta_len = BRANCH_FACTOR - len(self._tail)
        delta = sequence[offset:offset + max_delta_len]
        self._tail.extend(delta)
        delta_len = len(delta)
        self._count += delta_len
        return offset + delta_len

    def _mutating_extend(self, sequence):
        offset = 0
        sequence_len = len(sequence)
        while offset < sequence_len:
            offset = self._mutating_fill_tail(offset, sequence)
            if len(self._tail) == BRANCH_FACTOR:
                self._mutating_insert_tail()

        self._tail_offset = self._count - len(self._tail)

    def extend(self, obj):
        l = obj.tolist() if isinstance(obj, PythonPVector) else list(obj)
        if l:
            new_vector = self.append(l[0])
            new_vector._mutating_extend(l[1:])
            return new_vector

        return self

    def _push_tail(self, level, parent, tail_node):
        ret = list(parent)

        if level == SHIFT:
            ret.append(tail_node)
            return ret

        sub_index = ((self._count - 1) >> level) & BIT_MASK  # >>>
        if len(parent) > sub_index:
            ret[sub_index] = self._push_tail(level - SHIFT, parent[sub_index], tail_node)
            return ret

        ret.append(self._new_path(level - SHIFT, tail_node))
        return ret

    def index(self, value, *args, **kwargs):
        return self.tolist().index(value, *args, **kwargs)

    def count(self, value):
        return self.tolist().count(value)

    def delete(self, index, stop=None):
        l = self.tolist()
        del l[_index_or_slice(index, stop)]
        return _EMPTY_PVECTOR.extend(l)

    def remove(self, value):
        l = self.tolist()
        l.remove(value)
        return _EMPTY_PVECTOR.extend(l)

_EMPTY_PVECTOR = PythonPVector(0, SHIFT, [], [])
def pvector(iterable=()):
    return _EMPTY_PVECTOR.extend(iterable)

def v(*elements):
    return pvector(elements)