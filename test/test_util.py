import unittest

from bible.util import _LinkedList


class TestLinkedList(unittest.TestCase):    
    def test_construction(self):
        self.assertListEqual(list(_LinkedList()), [])
        self.assertListEqual(list(_LinkedList([1])), [1])
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10])
    
    def test_conform_index(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(test_list._conform_index(-2), -2 + len(test_list))
        self.assertRaises(IndexError, lambda: test_list._conform_index(len(test_list)))
    
    def test_node_at(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertIs(test_list._node_at(0), test_list._first)
        self.assertIs(test_list._node_at(-1), test_list._last)
        self.assertIs(test_list._node_at(2), test_list._first.next.next)
    
    def test_insert_first(self):
        test_list = _LinkedList()
        test_list._insert_first(6)
        self.assertIs(test_list._first, test_list._last)
        self.assertEqual(test_list._first.value, 6)
        self.assertEqual(len(test_list), 1)
    
    def test_insert_before(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        test_list._insert_before(test_list._node_at(3), 12)
        self.assertListEqual(list(test_list), [5, 8, 2, 12, 7, 3, 10])
        test_list._insert_before(test_list._node_at(0), 14)
        self.assertListEqual(list(test_list), [14, 5, 8, 2, 12, 7, 3, 10])  

    def test_insert_after(self):
        test_list = _LinkedList([5,8,2,7,3,10])
        test_list._insert_after(test_list._node_at(3), 12)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 12, 3, 10])
        test_list._insert_after(test_list._node_at(-1), 14)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 12, 3, 10, 14])

    def test_pop_node(self):
        test_list = _LinkedList([1])
        value = test_list._pop_node(test_list._node_at(0))
        self.assertEqual(value, 1)
        self.assertListEqual(list(test_list), [])
        self.assertEqual(len(test_list), 0)

        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        value = test_list._pop_node(test_list._node_at(0))
        self.assertEqual(value, 5)
        self.assertListEqual(list(test_list), [8, 2, 7, 3, 10])
        self.assertEqual(len(test_list), 5)
        value = test_list._pop_node(test_list._node_at(-1))
        self.assertEqual(value, 10)
        self.assertListEqual(list(test_list), [8,2,7,3])
        self.assertEqual(len(test_list), 4)

    def test_pop_before(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertRaises(IndexError, lambda: test_list._pop_before(test_list._node_at(0)))
        value = test_list._pop_before(test_list._node_at(3))
        self.assertEqual(value, 2)
        self.assertListEqual(list(test_list), [5, 8, 7, 3, 10])

    def test_pop_after(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertRaises(IndexError, lambda: test_list._pop_after(test_list._node_at(-1)))
        value = test_list._pop_after(test_list._node_at(2))
        self.assertEqual(value, 7)
        self.assertListEqual(list(test_list), [5,8,2,3,10])

    def test_prepend(self):
        test_list = _LinkedList()
        test_list.prepend(1)
        self.assertListEqual(list(test_list), [1])
        test_list.prepend(2)
        self.assertListEqual(list(test_list), [2, 1])

    def test_append(self):
        test_list = _LinkedList()
        test_list.append(1)
        self.assertListEqual(list(test_list), [1])
        test_list.append(2)
        self.assertListEqual(list(test_list), [1, 2])

    def test_insert(self):
        test_list = _LinkedList()
        test_list.insert(0, 1)
        self.assertListEqual(list(test_list), [1])
        test_list.insert(0, 2)
        test_list.insert(1, 3)
        self.assertListEqual(list(test_list), [2, 3, 1])
        test_list.insert(3, 4)
        self.assertListEqual(list(test_list), [2, 3, 1, 4])

    def test_index(self):
        test_list = _LinkedList([5, 3, 6, 3, 1, 7, 1, 6, 9, 3])
        self.assertEqual(test_list.index(3), 1)
        self.assertEqual(test_list.index(3, 2), 3)
        self.assertEqual(test_list.index(3, 4, len(test_list)), 9)
        self.assertRaises(ValueError, lambda: test_list.index(3, 4, -1))

    def test_count(self):
        test_list = _LinkedList([5, 3, 6, 3, 1, 7, 1, 6, 9, 3])
        self.assertEqual(test_list.count(5), 1)
        self.assertEqual(test_list.count(3), 3)
        self.assertEqual(test_list.count(6), 2)
        self.assertEqual(test_list.count(1), 2)
        self.assertEqual(test_list.count(10), 0)
    
    def test_pop(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        value = test_list.pop()
        self.assertEqual(value, 10)
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3])
        value = test_list.pop(0)
        self.assertEqual(value, 5)
        self.assertListEqual(list(test_list), [8, 2, 7, 3])
        value = test_list.pop(2)
        self.assertEqual(value, 7)
        self.assertListEqual(list(test_list), [8, 2, 3])

    def test_clear(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        test_list.clear()
        self.assertListEqual(list(test_list), [])
    
    def test_len(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(len(test_list), 6)

    def test_len(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertTrue(2 in test_list)
        self.assertFalse(9 in test_list)
        
    def test_get_set(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertEqual(test_list[0], 5)
        self.assertEqual(test_list[5], 10)
        self.assertEqual(test_list[3], 7)
        test_list[0] = 20
        test_list[5] = 30
        test_list[3] = 40
        self.assertEqual(test_list[0], 20)
        self.assertEqual(test_list[5], 30)
        self.assertEqual(test_list[3], 40)

    def test_del(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        del test_list[0]
        self.assertListEqual(list(test_list), [8, 2, 7, 3, 10])
        del test_list[4]
        self.assertListEqual(list(test_list), [8, 2, 7, 3])
        del test_list[2]
        self.assertListEqual(list(test_list), [8, 2, 3])

    def test_reversed(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        self.assertListEqual(list(reversed(test_list)), [10, 3, 7, 2, 8, 5])

    def test_extend(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        test_list.extend([12, 9, 20])
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10, 12, 9, 20])
    
    def test_remove(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10, 2])
        test_list.remove(2)
        self.assertListEqual(list(test_list), [5, 8, 7, 3, 10, 2])

    def test_reverse(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        test_list.reverse()
        self.assertListEqual(list(test_list), [10, 3, 7, 2, 8, 5])

    def test_iadd(self):
        test_list = _LinkedList([5, 8, 2, 7, 3, 10])
        test_list += [12, 9, 20]
        self.assertListEqual(list(test_list), [5, 8, 2, 7, 3, 10, 12, 9, 20])
        
