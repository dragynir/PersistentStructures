from unittest import TestCase
from src.plist import plist
from enum import Enum
import random
from functools import partial


class Operations(Enum):
    REMOVE = 1
    APPEND_BACK = 2
    APPEND_FRONT = 3
    SET = 4
    INSERT = 5


class TestPList(TestCase):

    @staticmethod
    def get_operation():
        operations = [Operations.REMOVE,
                      Operations.SET,
                      Operations.APPEND_BACK,
                      Operations.APPEND_FRONT,
                      Operations.INSERT
                      ]

        op = operations[random.randint(0, len(operations) - 1)]

        return op

    def test_init(self):
        l = plist()
        self.assertEqual(len(l), 0)

    def test_append_back_to_empty(self):
        l = plist()
        l1 = l.append_back(2)
        self.assertEqual(l1[0], 2)

    def test_append_front_to_empty(self):
        l = plist()
        l1 = l.append_front(2)
        self.assertEqual(l1[0], 2)

    def test_append_back_add_node(self):
        l = plist()
        l1 = l.append_back(1)
        l2 = l1.append_back(2)
        self.assertEqual(l2.tolist(), [1, 2])

    def test_append_back_add_fat_node(self):
        l = plist()
        max_size = 4 + 1
        ref_list = [1] * max_size
        for i in range(max_size):
            l = l.append_back(1)

        self.assertEqual(l.tolist(), ref_list)

    def test_append_front_add_node(self):
        l = plist()
        l1 = l.append_front(1)
        l2 = l1.append_front(2)
        self.assertEqual(l2.tolist(), [2, 1])

    def test_append_front_add_fat_node(self):
        l = plist()
        max_size = 4 + 1
        ref_list = [1] * max_size
        for i in range(max_size):
            l = l.append_front(1)

        self.assertEqual(l.tolist(), ref_list)

    def test_insert_empty(self):
        l = plist()
        l1 = l.insert(0, 1)

        self.assertEqual(len(l1), 1)
        self.assertEqual(l1[0], 1)

    @staticmethod
    def append_plist(pl, times):
        for i in range(times):
            pl = pl.append_back(i)
        return pl

    def test_insert_front(self):
        l = plist()
        l = TestPList.append_plist(l, 3)
        ref_list = [4, 0, 1, 2]
        l1 = l.insert(0, 4)
        self.assertEqual(l1.tolist(), ref_list)

    def test_insert_back(self):
        l = plist()
        l = TestPList.append_plist(l, 3)
        ref_list = [0, 1, 2, 4]
        l1 = l.insert(3, 4)
        self.assertEqual(l1.tolist(), ref_list)

    def test_insert_center(self):
        l = plist()
        max_size = 4 * 3 + 1
        l = TestPList.append_plist(l, max_size)
        l1 = l.insert(max_size//2, 0)

        ref_list = list(range(max_size))
        ref_list.insert(max_size//2, 0)
        self.assertEqual(l1.tolist(), ref_list)

    def test_set_for_empty(self):
        l = plist()
        self.assertRaises(AssertionError, partial(l.set, index=0, value=0))

    def test_set_not_int(self):
        l = plist()
        self.assertRaises(AssertionError, partial(l.set, index=-1, value=0))

    def test_set_one_node(self):
        l = plist()
        l1 = l.append_back(1)
        l2 = l1.set(0, 4)

        self.assertEqual(len(l2), 1)
        self.assertEqual(l2[0], 4)

    def test_set_center(self):
        l = plist()
        max_size = 4 * 3 + 1
        l = TestPList.append_plist(l, max_size)

        l2 = l.set(max_size//2, 0)

        ref_list = list(range(max_size))
        ref_list[max_size // 2] = 0

        self.assertEqual(len(l2), max_size)
        self.assertEqual(l2.tolist(), ref_list)


    def test_getitem(self):
        l = plist()
        l = l.append_back_list([1, 2])
        self.assertEqual(l[1], 2)

    def test_remove_empty(self):
        l = plist()
        self.assertRaises(AssertionError, partial(l.remove, index=0))

    def test_remove_front_node(self):
        l = plist()
        l = TestPList.append_plist(l, 3)
        ref_list = [1, 2]
        l1 = l.remove(0)
        self.assertEqual(l1.tolist(), ref_list)

    def test_remove_back_node(self):
        l = plist()
        l = TestPList.append_plist(l, 3)
        ref_list = [0, 1]
        l1 = l.remove(2)
        self.assertEqual(l1.tolist(), ref_list)

    def test_remove_center(self):
        l = plist()
        max_size = 4 * 3 + 1
        l = TestPList.append_plist(l, max_size)

        l2 = l.remove(max_size // 2)

        ref_list = list(range(max_size))
        ref_list.pop(max_size // 2)

        self.assertEqual(len(l2), max_size - 1)
        self.assertEqual(l2.tolist(), ref_list)

    def test_iterator_empty(self):
        list = []
        pl = plist()
        for x in pl:
            list.append(x)
        self.assertEqual(list, pl.tolist())

    def test_iterator_one(self):
        list = []
        pl = plist()
        pl = pl.append_back(1)
        for x in pl:
            list.append(x)
        self.assertEqual(list, pl.tolist())

    def test_iterator(self):
        list = []
        pl = plist()
        pl = pl.append_back(1)
        pl = pl.append_back(2)
        pl = pl.append_back(3)
        pl = pl.append_back(4)
        for x in pl:
            list.append(x)
        self.assertEqual(list, pl.tolist())

    def undo_none_test(self):
        pl = plist()
        self.assertEqual(pl.undo(), None)

    def redo_none_test(self):
        pl = plist()
        self.assertEqual(pl.redo(), None)

    def redo_test(self):
        pl = plist()
        pl = pl.append_back(1)
        pl2 = pl.append_back(2)
        self.assertEqual(pl2.undo().redo().tolist(), pl2.tolist())

    def undo_test(self):
        pl = plist()
        pl = pl.append_back(1)
        pl2 = pl.append_back(2)
        self.assertEqual(pl2.undo().tolist(), pl.tolist())

    def test_brute_force(self):

        for i in range(200):
            pl = plist()
            l = []

            for j in range(200):

                op = TestPList.get_operation()

                pl_len = len(pl)
                ind = 0
                if pl_len != 0:
                    ind = random.randint(0, pl_len - 1)

                value = random.randint(0, 1000)

                print(i, j, op, ind, value)
                print("before: ", pl)

                if op == Operations.REMOVE:
                    if pl_len == 0:
                        continue

                    pl = pl.remove(ind)
                    del l[ind]

                elif op == Operations.APPEND_BACK:
                    pl = pl.append_back(value)
                    l.append(value)
                elif op == Operations.APPEND_FRONT:
                    pl = pl.append_front(value)
                    l.insert(0, value)
                elif op == Operations.SET:
                    if pl_len == 0:
                        continue
                    pl = pl.set(ind, value)
                    l[ind] = value

                elif op == Operations.INSERT:
                    pl = pl.insert(ind, value)
                    l.insert(ind, value)

                print("after: ", pl)
            self.assertEqual(l, pl.tolist())
