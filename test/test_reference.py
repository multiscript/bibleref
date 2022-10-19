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
        list_A = _LinkedList([5,8,2,7,3,10])
        self.assertListEqual(list(list_A), [5,8,2,7,3,10])
    
    def test_conform_index(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        self.assertEqual(list_A._conform_index(-2), -2 + len(list_A))
        self.assertRaises(IndexError, lambda: list_A._conform_index(len(list_A)))
    
    def test_node_at(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        self.assertIs(list_A._node_at(0), list_A._first)
        self.assertIs(list_A._node_at(-1), list_A._last)
        self.assertIs(list_A._node_at(2), list_A._first.next.next)
    
    def test_insert_first(self):
        list_A = _LinkedList()
        list_A._insert_first(6)
        self.assertIs(list_A._first, list_A._last)
        self.assertEqual(list_A._first.value, 6)
        self.assertEqual(len(list_A), 1)
    
    def test_insert_before(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        list_A._insert_before(list_A._node_at(3), 12)
        self.assertListEqual(list(list_A), [5,8,2,12,7,3,10])
        list_A._insert_before(list_A._node_at(0), 14)
        self.assertListEqual(list(list_A), [14, 5,8,2,12,7,3,10])  

    def test_insert_after(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        list_A._insert_after(list_A._node_at(3), 12)
        self.assertListEqual(list(list_A), [5,8,2,7,12,3,10])
        list_A._insert_after(list_A._node_at(-1), 14)
        self.assertListEqual(list(list_A), [5,8,2,7,12,3,10,14])

    def test_pop_node(self):
        list_A = _LinkedList([1])
        value = list_A._pop_node(list_A._node_at(0))
        self.assertEqual(value, 1)
        self.assertListEqual(list(list_A), [])
        self.assertEqual(len(list_A), 0)

        list_A = _LinkedList([5,8,2,7,3,10])
        value = list_A._pop_node(list_A._node_at(0))
        self.assertEqual(value, 5)
        self.assertListEqual(list(list_A), [8,2,7,3,10])
        self.assertEqual(len(list_A), 5)
        value = list_A._pop_node(list_A._node_at(-1))
        self.assertEqual(value, 10)
        self.assertListEqual(list(list_A), [8,2,7,3])
        self.assertEqual(len(list_A), 4)

    def test_pop_before(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        self.assertRaises(IndexError, lambda: list_A._pop_before(list_A._node_at(0)))
        value = list_A._pop_before(list_A._node_at(3))
        self.assertEqual(value, 2)
        self.assertListEqual(list(list_A), [5,8,7,3,10])

    def test_pop_after(self):
        list_A = _LinkedList([5,8,2,7,3,10])
        self.assertRaises(IndexError, lambda: list_A._pop_after(list_A._node_at(-1)))
        value = list_A._pop_after(list_A._node_at(2))
        self.assertEqual(value, 7)
        self.assertListEqual(list(list_A), [5,8,2,3,10])
