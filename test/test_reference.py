import unittest
from bible.reference import BibleBook, BibleVerse, BibleRange, _LinkedList


class TestBibleReference(unittest.TestCase):
    def test_bible_books(self):
        self.assertEqual(BibleBook.from_name("Gen"), BibleBook.Gen)
        self.assertEqual(BibleBook.from_name("Mt"), BibleBook.Matt)
        self.assertEqual(BibleBook.from_name("Rev"), BibleBook.Rev)
    
    def test_bible_ranges(self):
        # TODO Add test when the end verse is just a verse
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None, None, None), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 28, 20))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None, None, None), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 2, 23))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None, None, None), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 2, 3))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John, None, None, allow_multibook=True), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 21, 25, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John, None, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 21, 25, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John, None, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 21, 25, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None,    4, None), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None,    4, None), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None,    4, None), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None,    6,    7), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 8, 10, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 8, 10, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 8, 10, allow_multibook=True))

    def test_range_iteration(self):
        bible_range = BibleRange(BibleBook.Matt, 28, 18, BibleBook.Mark, 1, 3, allow_multibook=True)
        expected_list = [
            BibleVerse(BibleBook.Matt, 28, 18),
            BibleVerse(BibleBook.Matt, 28, 19),
            BibleVerse(BibleBook.Matt, 28, 20),
            BibleVerse(BibleBook.Mark, 1, 1),
            BibleVerse(BibleBook.Mark, 1, 2),
            BibleVerse(BibleBook.Mark, 1, 3),                         
        ]
        self.assertEqual(list(bible_range), expected_list)       


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
