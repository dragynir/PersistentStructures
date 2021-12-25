from unittest import TestCase
from src import pvector

class TestPythonPVector(TestCase):

    # test creation
    def test_empty(self):
        v = pvector()
        self.assertEqual(len(v), 0)

    def test_from_iterable(self):
        iterable = list(range(10))
        v = pvector(iterable)
        self.assertEqual(v.tolist(), iterable)

    def test_version_instance(self):
        v1 = pvector()
        v2 = v1.append(3)
        self.assertNotEqual(id(v1), id(v2))

    # test append
    def test_multi_append_leaf(self):
        v = pvector()
        base_list = []
        for i in range(1 << 5):
            v2 = v.append(i)
            base_list.append(i)
            self.assertEqual(v2.tolist(), base_list)
            self.assertNotEqual(v.tolist(), v2.tolist())
            v = v2

    def test_multi_append_multi_leafs(self):
        v = pvector()
        base_list = []
        for i in range(2 * (1 << 5)):
            v2 = v.append(i)
            base_list.append(i)
            self.assertEqual(v2.tolist(), base_list)
            self.assertNotEqual(v.tolist(), v2.tolist())
            v = v2

    def test_two_levels(self):
        v = pvector()
        base_list = []
        for i in range(((1 << 5) << 5) + 1):
            v2 = v.append(i)
            base_list.append(i)
            self.assertEqual(v2.tolist(), base_list)
            self.assertNotEqual(v.tolist(), v2.tolist())
            v = v2

    def test_add(self):
        v = pvector()
        v2 = v + [4, 3]
        self.assertEqual(v2.tolist(), [4, 3])

    # test helpers
    def test_get_item(self):
        v = pvector()
        v = v.append(4)
        self.assertEqual(v[0], 4)

    def test_get_neg_item(self):
        v = pvector()
        v = v.append(4)
        self.assertEqual(v[-1], 4)

    def test_hash(self):
        v = pvector([4, 5, 6])
        self.assertEqual(hash(v), hash(v))

    def test_iter(self):
        count = 20
        v = pvector(range(20))

        for i, val in enumerate(v):
            self.assertEqual(v[i], val)

    # test slice
    def test_pos_slice(self):
        v = pvector([1, 2, 3, 4])
        self.assertEqual(v[:2].tolist(), [1, 2])

    def test_neg_slice(self):
        v = pvector([1, 2, 3, 4])
        self.assertEqual(v[:-2].tolist(), [1, 2])

    def test_none_slice(self):
        init_list = [1, 2, 3, 4]
        v = pvector(init_list)
        self.assertEqual(v[:].tolist(), init_list)

    def test_multi_slice(self):
        init_list = [1, 2, 3, 4]
        v = pvector(init_list)
        self.assertEqual(v[1:3].tolist(), [2, 3])

    # test set
    def test_set_one(self):
        v = pvector()
        v2 = v.set(0, 42)
        self.assertEqual(v2.tolist(), [42])

    def test_set_neg_one(self):
        v = pvector([3])
        v2 = v.set(-1, 42)
        self.assertEqual(v2.tolist(), [42])

    def test_set_tail(self):
        v = pvector()
        for i in range(1 << 5):
            v = v.append(i)

        v2 = v.set((1 << 5) - 1, 42)

        self.assertEqual(v2[-1], 42)

    def test_count(self):
        v = pvector([3] * 4)
        self.assertEqual(4, v.count(3))

    def test_delete(self):
        v = pvector([3])
        v1 = v.delete(0)
        self.assertEqual(len(v1), 0)

    def test_undo_one(self):
        v = pvector([3, 4, 5])

        self.assertEqual(len(v.undo()), 0)

    def test_redo_one(self):
        v = pvector()
        v1 = v.append(5)
        self.assertEqual(v.redo().tolist(), v1.tolist())