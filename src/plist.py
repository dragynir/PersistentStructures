from numbers import Integral



class ListFatNode(object):
    __slots__ = ('nodes', '__weakref__', '_cached_hash')

    MAX_SIZE = 2

    def __new__(cls):
        self = super(ListFatNode, cls).__new__(cls)
        self.nodes = []
        return self

    def add(self, node):
        self.nodes.append(node)

    def find_node(self, version_node):

        it = version_node

        while it is not None:
            any_nodes = list(filter(lambda n: n.version == it.version, self.nodes))

            if any_nodes:
                return any_nodes[0]
            else:
                it = it.parent

        assert False, "Unreached version"

    def is_full(self):
        return len(self.nodes) == ListFatNode.MAX_SIZE

    def update_right(self, right_node, version_node):
        node = self.find_node(version_node)
        new_node = node.copy()
        new_node.version = version_node.version

        new_node.right_node = right_node

        if self.is_full():
            new_f = ListFatNode()
            new_f.add(new_node)

            if node.left_node:
                new_node.left_node = node.left_node.update_right(new_f, version_node)
            else:
                version_node.front = new_f

            return new_f

        self.add(new_node)

        return self

    def update_left(self, left_node, version_node):

        node = self.find_node(version_node)
        new_node = node.copy()
        new_node.version = version_node.version

        new_node.left_node = left_node

        if self.is_full():
            new_f = ListFatNode()
            new_f.add(new_node)

            if node.right_node:
                new_node.right_node = node.right_node.update_left(new_f, version_node)
            else:
                version_node.back = new_f

            return new_f

        self.add(new_node)

        return self





class ListNode(object):
    __slots__ = ('left_node', 'right_node', 'value', 'version', '__weakref__', '_cached_hash')

    def __new__(cls, left_node, right_node, value, version):
        self = super(ListNode, cls).__new__(cls)
        self.left_node = left_node
        self.right_node = right_node
        self.value = value
        self.version = version
        return self

    def copy(self):
       return ListNode(self.left_node,
                             self.right_node,
                             self.value,
                             self.version
                             )


class VersionNode(object):
    __slots__ = ('version', 'child', 'parent', 'front', 'back', '__weakref__', '_cached_hash')

    def __new__(cls, front, back, parent, child, version):
        self = super(VersionNode, cls).__new__(cls)
        self.back = back
        self.front = front
        self.parent = parent
        self.child = child
        self.version = version
        return self

class PListIter(object):

    def __init__(self, plist):
        self._plist = plist
        self._pos = None

    def __next__(self):
        if self._pos is None:
            if self._plist._root_version.front is None:
                raise StopIteration
            self._pos = self._plist._root_version.front.find_node(self._plist._root_version)
        elif self._pos.right_node is None:
            raise StopIteration
        else:
            self._pos = self._pos.right_node.find_node(self._plist._root_version)
        return self._pos.value

class PList(object):

    __slots__ = ('_root_version', '__weakref__', '_cached_hash')

    GLOBAL_VERSION = 0

    def __init__(self, version_node=None):

        if version_node:
            self._root_version = version_node
        else:
            PList.GLOBAL_VERSION += 1
            self._root_version = VersionNode(None, None, None, None, PList.GLOBAL_VERSION)

    def __str__(self):
        return str(self.tolist())

    def __len__(self):
        return len(self.tolist())

    def __iter__(self):
        return PListIter(self)

    def undo(self):
        if self._root_version.parent is None:
            return None
        return PList(self._root_version.parent)

    def redo(self):
        if self._root_version.child is None:
            return None
        return PList(self._root_version.child)

    def front(self):
        return self._root_version.front.value

    def back(self):
        return self._root_version.back.value

    def tolist(self):
        py_list = []
        for x in self:
            py_list.append(x)
        return py_list

    def remove(self, index):
        if not isinstance(index, int):
            raise TypeError("'%s' object cannot be interpreted as an index" % type(index).__name__)
        assert index >= 0 and index < len(self)

        if index < 0:
            index += len(self)

        if not (0 <= index < len(self)):
            raise ValueError("Bad index for list with length '%s' " % len(self))

        PList.GLOBAL_VERSION += 1

        it = self._root_version.front

        for i in range(index):
            it = it.find_node(self._root_version).right_node

        node_to_del = it.find_node(self._root_version)

        new_v = VersionNode(self._root_version.front, self._root_version.back, self._root_version, None,
                            PList.GLOBAL_VERSION)

        if node_to_del.right_node is None and node_to_del.left_node is None:
            new_v.front = None
            new_v.back = None
            return PList(new_v)

        if node_to_del.right_node is None:
            new_left_node = node_to_del.left_node.update_right(None,
                                               new_v)

            if it is self._root_version.back:
                new_v.back = new_left_node

            return PList(new_v)

        if node_to_del.left_node is None:
            new_right_node = node_to_del.right_node.update_left(None,
                                               new_v)

            if it is self._root_version.front:
                new_v.front = new_right_node

            return PList(new_v)

        if not node_to_del.right_node.is_full():
            new_left_node = node_to_del.left_node.update_right(node_to_del.right_node, new_v)

            new_right_node = node_to_del.right_node.update_left(new_left_node, new_v)
            assert new_right_node is node_to_del.right_node, "вернется та же фэтнода, так как она не была полной"

            return PList(new_v)

        fake_left_fat_node = ListFatNode()
        new_right_node = node_to_del.right_node.update_left(fake_left_fat_node, new_v)

        new_left_node = node_to_del.left_node.update_right(new_right_node, new_v)
        assert len(new_right_node.nodes) == 1, "раньше правая фэтнода была полная, значит после добавления это новая фэтнода с одной нодой"

        new_right_node.nodes[0].left_node = new_left_node

        return PList(new_v)


    def insert(self, index, value):
        if not isinstance(index, int):
            raise TypeError("'%s' object cannot be interpreted as an index" % type(index).__name__)
        assert index >= 0 and index <= len(self)
        PList.GLOBAL_VERSION += 1

        new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)
        new_f = ListFatNode()
        new_f.add(new_n)
        new_v = VersionNode(self._root_version.front, self._root_version.back, self._root_version, None,
                            PList.GLOBAL_VERSION)

        front = self._root_version.front
        if front is None:
            new_v.back = new_f
            new_v.front = new_f
            return PList(new_v)
        if index == 0:
            new_n.right_node = front.update_left(new_f, new_v)
            new_v.front = new_f
            return PList(new_v)
        left_it = front
        for i in range(index - 1):
            left_it = left_it.find_node(self._root_version).right_node


        new_n.left_node = left_it.update_right(new_f, new_v)

        right_it = left_it.find_node(self._root_version).right_node

        if right_it is None:
            new_v.back = new_f
        else:
            new_n.right_node = right_it.update_left(new_f, new_v)


        return PList(new_v)

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError("'%s' object cannot be interpreted as an index" % type(item).__name__)
        assert 0 <= item < len(self)

        PList.GLOBAL_VERSION += 1

        front = self._root_version.front

        it = front

        for i in range(item):
            it = it.find_node(self._root_version).right_node

        found_node = it.find_node(self._root_version)

        return found_node.value

    def set(self, index, value):
        if not isinstance(index, int):
            raise TypeError("'%s' object cannot be interpreted as an index" % type(index).__name__)
        assert index >= 0 and index < len(self)
        PList.GLOBAL_VERSION += 1

        front = self._root_version.front

        it = front

        for i in range(index):
            it = it.find_node(self._root_version).right_node

        found_node = it.find_node(self._root_version)
        new_n = found_node.copy()

        new_v = VersionNode(self._root_version.front, self._root_version.back, self._root_version, None, PList.GLOBAL_VERSION)
        new_n.value = value
        new_n.version = PList.GLOBAL_VERSION

        if it.is_full():
            new_f = ListFatNode()
            new_f.add(new_n)
            if new_n.left_node is not None:
                new_n.left_node = found_node.left_node.update_right(new_f, new_v)
            else:
                new_v.front = new_f
            if new_n.right_node is not None:
                new_n.right_node = found_node.right_node.update_left(new_f, new_v)
            else:
                new_v.back = new_f

            return PList(new_v)

        it.add(new_n)

        return PList(new_v)


    def append_back(self, value):

        PList.GLOBAL_VERSION += 1

        if self._root_version.back is None:
            return self._init_root(value)

        new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)
        new_f = ListFatNode()
        new_f.add(new_n)

        new_v = VersionNode(self._root_version.front, new_f, self._root_version, None, PList.GLOBAL_VERSION)
        self._root_version.child = new_v

        new_n.left_node = self._root_version.back.update_right(new_f, new_v)

        return PList(new_v)

    def append_front(self, value):

        PList.GLOBAL_VERSION += 1

        if self._root_version.front is None:
            return self._init_root(value)

        new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)
        new_f = ListFatNode()
        new_f.add(new_n)

        new_v = VersionNode(new_f, self._root_version.back, self._root_version, None, PList.GLOBAL_VERSION)
        self._root_version.child = new_v

        new_n.right_node = self._root_version.front.update_left(new_f, new_v)

        return PList(new_v)

    def _init_root(self, value):

        new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)

        new_f = ListFatNode()
        new_f.add(new_n)

        new_v = VersionNode(new_f, new_f, self._root_version, None, PList.GLOBAL_VERSION)

        return PList(new_v)


def plist():
    return PList()







