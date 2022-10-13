import unittest
from bible.reference import BibleBook, BibleVerse, BibleRange


class TestBibleReference(unittest.TestCase):
    def test_bible_books(self):
        self.assertEqual(BibleBook.from_name("Gen"), BibleBook.Gen)
        self.assertEqual(BibleBook.from_name("Mt"), BibleBook.Matt)
        self.assertEqual(BibleBook.from_name("Rev"), BibleBook.Rev)
    
    def test_bible_ranges(self):
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
         