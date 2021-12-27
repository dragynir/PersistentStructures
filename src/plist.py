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
            # if version_node.back is self:
            #     version_node.back = new_f

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
            # if version_node.front is self:
            #     print("AAAAAAAAAAAA")
            #     version_node.front = new_f

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


class PList(object):

    __slots__ = ('_root_version', '__weakref__', '_cached_hash')

    GLOBAL_VERSION = 0

    def __init__(self, version_node=None):

        if version_node:
            self._root_version = version_node
        else:
            PList.GLOBAL_VERSION += 1
            self._root_version = VersionNode(None, None, None, None, PList.GLOBAL_VERSION)

    def set(self, index, value):
        if not isinstance(index, int):
            raise TypeError("'%s' object cannot be interpreted as an index" % type(index).__name__)

        PList.GLOBAL_VERSION += 1

        front = self._root_version.front

        it = front

        for i in range(index):
            it = it.find_node(self._root_version).right_node

        new_n = it.find_node(self._root_version).copy()

        new_v = VersionNode(self._root_version.front, self._root_version.back, self._root_version, None, PList.GLOBAL_VERSION)
        new_n.value = value
        new_n.version = PList.GLOBAL_VERSION

        if it.is_full():
            new_f = ListFatNode()
            new_f.add(new_n)

            new_n.left_node = it.update_right(new_f, new_v)
            new_n.right_node = it.update_left(new_f, new_v)

            if it.right_node is None:
                new_v.back = new_f

            if it.left_node is None:
                new_v.front = new_f

            return PList(new_v)

        it.add(new_n)

        return PList(new_v)

    def append_back(self, value):

        PList.GLOBAL_VERSION += 1

        if self._root_version.back is None:

            new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)

            new_f = ListFatNode()
            new_f.add(new_n)

            new_v = VersionNode(new_f, new_f, self._root_version, None, PList.GLOBAL_VERSION)

            return PList(new_v)

        new_n = ListNode(None, None, value, PList.GLOBAL_VERSION)
        new_f = ListFatNode()
        new_f.add(new_n)

        new_v = VersionNode(self._root_version.front, new_f, self._root_version, None, PList.GLOBAL_VERSION)
        self._root_version.child = new_v

        new_n.left_node = self._root_version.back.update_right(new_f, new_v)

        return PList(new_v)


def plist():
    return PList()































        # if self._root_version.back.is_full():
        #
        #     nearest_node = self._root_version.back.find_node(self._root_version, self._root_version.version)
        #
        #     new_n = ListNode(None, None, PList.GLOBAL_VERSION, value)
        #     new_f = ListFatNode()
        #     new_f.add(new_n)
        #
        #     node_copy = ListNode(nearest_node.left_node,
        #                          new_f,
        #                          nearest_node.value,
        #                          PList.GLOBAL_VERSION
        #              )
        #
        #     new_level_f = ListFatNode()
        #     new_level_f.add(node_copy)
        #
        #     node_copy.right_node = new_f
        #     new_n.left_node = new_level_f
        #
        #     # recursion
        #
        #
        #     pass
        #
        #
        #
        # new_n = ListNode(None, None, PList.GLOBAL_VERSION, value)
        # new_f = ListFatNode()
        # new_f.add(new_n)
        #
        # nearest_node = self._root_version.back.find_node(self._root_version, self._root_version.version)
        # node_copy = ListNode(nearest_node.left_node,
        #                      new_f,
        #                      nearest_node.value,
        #                      PList.GLOBAL_VERSION
        #                      )
        #
        # node_copy.right_node = new_f
        # new_n.left_node = self._root_version.back
        #
        # new_v = VersionNode(self._root_version.front, new_f, self._root_version, None, PList.GLOBAL_VERSION)
        #
        # return PList(new_v)










