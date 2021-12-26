from numbers import Integral
import operator

def _bitcount(val):
    return bin(val).count("1")

# bit partitioning
BRANCH_FACTOR = 32 #
BIT_MASK = BRANCH_FACTOR - 1
SHIFT = _bitcount(BIT_MASK)


def compare_pvector(v, other, operator):
    return operator(v.tolist(), other.tolist() if isinstance(other, PythonPVector) else other)


def _index_or_slice(index, stop):
    if stop is None:
        return index
    return slice(index, stop)


class PythonPVector(object):

    __slots__ = ('_count', '_shift', '_root', '_tail', '_tail_offset', '_versions', '__weakref__')

    def __new__(cls, count, shift, root, tail, versions):
        self = super(PythonPVector, cls).__new__(cls)
        self._count = count
        self._shift = shift # 5 for empty
        self._root = root
        self._tail = tail
        self._versions = versions + [self]

        # кол-во элементов в вереве (не учитываем элементы в хвосте)
        self._tail_offset = self._count - len(self._tail)
        return self

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.start is None and index.stop is None and index.step is None:
                return self

            new_v = PythonPVector(0, SHIFT, [], [], self._versions)
            self._save_version(new_v)

            return new_v.extend(self.tolist()[index])

        if index < 0:
            index += self._count

        return PythonPVector._node_for(self, index)[index & BIT_MASK]

    def __add__(self, other):
        return self.extend(other)

    def __iter__(self):
        return iter(self.tolist())

    def _save_version(self, new):
        self._versions.append(new)
        return new

    def _fill_list(self, node, shift, the_list):
        """ Рекурсивно наполняем лист """

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

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return str(self.tolist())

    def __hash__(self):
        return hash(self._totuple())

    def undo(self):
        """ Возвращает предыдущую версию вектора """
        curr_index = self._versions.index(self)
        curr_index = max(0, curr_index - 1)
        return self._versions[curr_index]

    def redo(self):
        """ Возвращает следующую версию вектора """

        curr_index = self._versions.index(self)
        curr_index = min(len(self._versions) - 1, curr_index + 1)
        return self._versions[curr_index]

    def set(self, i, val):
        """ Обновление значения по индексу """

        if not isinstance(i, Integral):
            raise TypeError("Not index")

        # для отрицательных индексов
        if i < 0:
            i += self._count

        # если индекс существует в векторе
        if 0 <= i < self._count:
            if i >= self._tail_offset:
                # если элемент для обновления в хвосте
                new_tail = list(self._tail)
                # обновляем tail
                new_tail[i & BIT_MASK] = val
                # создаем новый вектор
                return self._save_version(PythonPVector(self._count,
                                                        self._shift,
                                                        self._root,
                                                        new_tail,
                                                        self._versions))
            # обновление элемента в дереве
            return self._save_version(PythonPVector(self._count,
                                                    self._shift,
                                                    self._do_set(self._shift, self._root, i, val),
                                                    self._tail,
                                                    self._versions))

        # добавление в конец
        if i == self._count:
            return self.append(val)

        raise IndexError("Index out of range: %s" % (i,))

    def _do_set(self, level, node, i, val):
        """
            Обновление элемента в дереве
        """

        # копируем ноду
        ret = list(node)
        if level == 0:
            ret[i & BIT_MASK] = val
        else:
            # переход на следующий уровень и обновляем ссылку на новую ноду
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
        """ Создание нового root """

        new_shift = self._shift

        # root overflow, надо создать новый уровень дерева
        # count > (2 ^ _shift)
        # example: 1056 >> 5 == 33 > 32 --> Root overflow
        # 32 ноды в root, по 32 элемента в каждой ноде + 32 в tail
        if (self._count >> SHIFT) > (1 << self._shift):
            # создаем новый root и подвещиваем старый root первым потомком, копируем путь
            new_root = [self._root, self._new_path(self._shift, self._tail)]
            new_shift += SHIFT
        else:
            # 1) в tail закончилось место, кладем элементы из tail в root, новый элемент будет в tail
            new_root = self._push_tail(self._shift, self._root, self._tail)

        return new_root, new_shift

    def append(self, val):
        """ Добавление элемента в конец """

        # есть место в tail?
        if len(self._tail) < BRANCH_FACTOR:
            # ускорение за счет отказа от копирования пути при добавлении нового элемента
            # добавляем новый элемент в tail
            new_tail = list(self._tail)
            new_tail.append(val)
            return self._save_version(PythonPVector(self._count + 1,
                                                    self._shift,
                                                    self._root,
                                                    new_tail,
                                                    self._versions))

        # в tail нет места - добавляем элементы в root или создаем новый уровень дерева
        # новый элемент кладем в tail
        new_root, new_shift = self._create_new_root()
        return self._save_version(PythonPVector(self._count + 1,
                                                new_shift,
                                                new_root,
                                                [val],
                                                self._versions
                                                ))

    def _new_path(self, level, node):
        # 1) _shift, _tail
        if level == 0:
            return node

        return [self._new_path(level - SHIFT, node)]

    def _mutating_insert_tail(self):
        """ Создаем рут или новый уровень при переполнении tail"""

        self._root, self._shift = self._create_new_root()
        self._tail = []

    def _mutating_fill_tail(self, offset, sequence):
        """ Заполняем tail не создавая новую версию """

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
        """ Добавление нескольких элементов в вектор """

        l = obj.tolist() if isinstance(obj, PythonPVector) else list(obj)
        if l:
            # создаем новый вектор с одним элементом (новая версия)
            # добавляем остальные элементы из obj без изменения версии
            new_vector = self.append(l[0])
            new_vector._mutating_extend(l[1:])
            return new_vector

        return self

    def _push_tail(self, level, parent, tail_node):
        # 1: _shift, _root, _tail

        # копируем ноду
        ret = list(parent)

        # первый уровень
        if level == SHIFT:
            # добавляем ноду с tail в root
            ret.append(tail_node)
            return ret

        # получаем индекс для перехода на следующий уровень дерева
        sub_index = ((self._count - 1) >> level) & BIT_MASK  # >>>

        # если можем совершить переход дальше (индекс принадлежит этому уровню)
        if len(parent) > sub_index:
            # делаем переход
            ret[sub_index] = self._push_tail(level - SHIFT, parent[sub_index], tail_node)
            return ret

        # копируем путь
        ret.append(self._new_path(level - SHIFT, tail_node))
        return ret

    def index(self, value, *args, **kwargs):
        """ Индекс элемента в векторе """

        return self.tolist().index(value, *args, **kwargs)

    def count(self, value):
        """ Количество элементов в веторе равных value """

        return self.tolist().count(value)

    def remove(self, value):
        """ Удаление элемента """

        l = self.tolist()
        l.remove(value)
        new_v = PythonPVector(0, SHIFT, [], [], self._versions)
        self._save_version(new_v)
        return new_v.extend(l)


def pvector(iterable=()):
    return PythonPVector(0, SHIFT, [], [], []).extend(iterable)


def v(*elements):
    return pvector(elements)