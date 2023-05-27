import unittest

import bibleref
from bibleref.ref import BibleBook, BibleVerse, BibleRange, BibleRangeList, \
                            BibleFlag, BibleVersePart as BVP, InvalidReferenceError, \
                            MultibookRangeNotAllowedError


class TestBibleReference(unittest.TestCase):
    def test_bible_books(self):
        self.assertEqual(BibleBook.from_str("Gen"), BibleBook.Gen)
        self.assertEqual(BibleBook.from_str("Mt"), BibleBook.Matt)
        self.assertEqual(BibleBook.from_str("Rev"), BibleBook.Rev)

    def test_bible_book_ranges(self):
        self.assertEqual(BibleBook.Matt.range(), BibleRange("Matt 1:1-28:20"))
        self.assertEqual(BibleBook.Matt.chap_range(2), BibleRange("Matt 2:1-23"))

    def test_bible_book_counts(self):
        self.assertEqual(BibleBook.Phil.verse_count(), 104) # Check one book manually
        for book in BibleBook:
            self.assertEqual(book.verse_count(), BibleRange(book.title).verse_count())
            self.assertEqual(book.chap_count(), BibleRange(book.title).chap_count())

    def test_bible_book_chap_ranges(self):
        self.assertEqual(BibleBook.Mark.chap_ranges(),
            BibleRangeList("Mark 1; 2; 3; 4; 5; 6; 7; 8; 9; 10; 11; 12; 13; 14; 15; 16"))

        self.assertEqual(BibleBook.Mark.chap_ranges(regroup=False),
            BibleRangeList("Mark 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16"))

    def test_bible_verses(self):
        self.assertRaises(ValueError, lambda: BibleVerse(BibleBook.Matt, 2, 3, 4))
        self.assertRaises(ValueError, lambda: BibleVerse(BibleBook.Matt, 2))
        self.assertRaises(ValueError, lambda: BibleVerse(True))
        self.assertRaises(InvalidReferenceError, lambda: BibleVerse("Not real book", 2, 3))
        self.assertRaises(ValueError, lambda: BibleVerse(BibleBook.Matt, [], []))
        self.assertRaises(InvalidReferenceError, lambda: BibleVerse(BibleBook.Matt, 50, 3))
        self.assertRaises(InvalidReferenceError, lambda: BibleVerse(BibleBook.Matt, 2, 100))
        self.assertRaises(InvalidReferenceError, lambda: BibleVerse("Matthew 2:3; 4:5"))
        self.assertRaises(InvalidReferenceError, lambda: BibleVerse("Matthew 2:3-4"))
        self.assertEqual(BibleVerse("Matthew", 2, 3), BibleVerse(BibleBook.Matt, 2, 3))
        self.assertEqual(BibleVerse("Matthew 2:3"), BibleVerse(BibleBook.Matt, 2, 3))

        self.assertEqual(BibleVerse("Ps 3:0", flags=BibleFlag.VERSE_0),
                         BibleVerse(BibleBook.Psa, 3, 0, flags=BibleFlag.VERSE_0))
        self.assertRaises(InvalidReferenceError,
                          lambda: BibleVerse(BibleBook.Psa, 3, 0, flags=BibleFlag.NONE))

        bible_verse = BibleVerse(BibleBook.Mark, 2, 3)
        self.assertEquals(bible_verse, BibleVerse(bible_verse))

    def test_bible_verse_comparison(self):
        self.assertTrue(BibleVerse("Matt 2:3") < BibleVerse("Matt 2:4"))
        self.assertTrue(BibleVerse("Matt 2:3") <= BibleVerse("Matt 2:4"))
        self.assertFalse(BibleVerse("Matt 2:3") == BibleVerse("Matt 2:4"))
        self.assertFalse(BibleVerse("Matt 2:3") >= BibleVerse("Matt 2:4"))
        self.assertFalse(BibleVerse("Matt 2:3") > BibleVerse("Matt 2:4"))

        self.assertTrue(BibleVerse("Matt 2:3") < BibleVerse("Matt 3:1"))
        self.assertTrue(BibleVerse("Matt 2:3") <= BibleVerse("Matt 3:1"))
        self.assertFalse(BibleVerse("Matt 2:3") == BibleVerse("Matt 3:1"))
        self.assertFalse(BibleVerse("Matt 2:3") >= BibleVerse("Matt 3:1"))
        self.assertFalse(BibleVerse("Matt 2:3") > BibleVerse("Matt 3:1"))

        self.assertTrue(BibleVerse("Matt 2:3") < BibleVerse("Mark 1:2"))
        self.assertTrue(BibleVerse("Matt 2:3") <= BibleVerse("Mark 1:2"))
        self.assertFalse(BibleVerse("Matt 2:3") == BibleVerse("Mark 1:2"))
        self.assertFalse(BibleVerse("Matt 2:3") >= BibleVerse("Mark 1:2"))
        self.assertFalse(BibleVerse("Matt 2:3") > BibleVerse("Mark 1:2"))

        self.assertFalse(BibleVerse("Matt 2:3") < BibleVerse("Matt 2:3"))
        self.assertTrue(BibleVerse("Matt 2:3") <= BibleVerse("Matt 2:3"))
        self.assertTrue(BibleVerse("Matt 2:3") == BibleVerse("Matt 2:3"))
        self.assertTrue(BibleVerse("Matt 2:3") >= BibleVerse("Matt 2:3"))
        self.assertFalse(BibleVerse("Matt 2:3") > BibleVerse("Matt 2:3"))

    def test_bible_verse_0(self):
        verse_with_0 = BibleVerse(BibleBook.Psa, 3, 0, flags=BibleFlag.VERSE_0)
        verse_with_1 = BibleVerse(BibleBook.Psa, 3, 1)
        no_verse_0 = BibleVerse(BibleBook.Matt, 2, 3)
        self.assertEqual(verse_with_0.verse_0_to_1(), verse_with_1)
        self.assertEqual(verse_with_1.verse_1_to_0(), verse_with_0)
        self.assertEqual(no_verse_0.verse_0_to_1(), no_verse_0)
        self.assertEqual(no_verse_0.verse_1_to_0(), no_verse_0)

    def test_bible_verse_bool_tests(self):
        self.assertTrue(BibleVerse(BibleBook.Matt, 2, 1).is_first_in_chap())
        self.assertFalse(BibleVerse(BibleBook.Matt, 2, 2).is_first_in_chap())
        self.assertTrue(BibleVerse(BibleBook.Matt, 2, 23).is_last_in_chap())
        self.assertFalse(BibleVerse(BibleBook.Matt, 2, 22).is_last_in_chap())

        self.assertTrue(BibleVerse(BibleBook.Matt, 1, 1).is_first_in_book())
        self.assertFalse(BibleVerse(BibleBook.Matt, 1, 2).is_first_in_book())
        self.assertTrue(BibleVerse(BibleBook.Matt, 28, 20).is_last_in_book())
        self.assertFalse(BibleVerse(BibleBook.Matt, 28, 19).is_last_in_book())

    def test_verse_ranges(self):
        bible_verse = BibleVerse("Matt 3:8")
        self.assertEqual(bible_verse.chap_range(), BibleRange("Matt 3"))
        self.assertEqual(bible_verse.book_range(), BibleRange("Matt"))

    def test_verse_arithmetic(self):
        self.assertEqual(BibleVerse("Ps 3:8") + 1, BibleVerse("Ps 4:1"))
        self.assertEqual(BibleVerse("Ps 4:1") - 1, BibleVerse("Ps 3:8"))
        self.assertEqual(BibleVerse("Ps 3:8") - BibleVerse("Ps 4:1"), -1)
        self.assertEqual(BibleVerse("Ps 4:1") - BibleVerse("Ps 3:8"), 1)

        self.assertEqual(BibleVerse("Ps 3:8").add(1, flags=BibleFlag.VERSE_0),
                        BibleVerse("Ps 4:0", flags=BibleFlag.VERSE_0))
        self.assertEqual(BibleVerse("Ps 4:0", flags=BibleFlag.VERSE_0) - 1, BibleVerse("Ps 3:8"))
        self.assertEqual(BibleVerse("Ps 3:8").subtract(BibleVerse("Ps 4:0", flags=BibleFlag.VERSE_0),
                         flags=BibleFlag.VERSE_0), -1)
        self.assertEqual(BibleVerse("Ps 4:0", flags=BibleFlag.VERSE_0).subtract(BibleVerse("Ps 3:8"),
                         flags=BibleFlag.VERSE_0), 1)
        
        self.assertEqual(BibleVerse("John 1:50") + 11, BibleVerse("John 2:10"))
        self.assertEqual(BibleVerse("John 1:50") - BibleVerse("John 2:10"), -11)
        self.assertEqual(BibleVerse("John 2:10") - BibleVerse("John 1:50"), 11)

        self.assertEqual(BibleVerse("John 2:10") - 12, BibleVerse("John 1:49"))
        self.assertEqual(BibleVerse("John 2:10") - BibleVerse("John 1:49"), 12)
        self.assertEqual(BibleVerse("John 1:49") - BibleVerse("John 2:10"), -12)

    def test_bible_verse_to_string(self):
        verse = BibleVerse(BibleBook.Matt, 5, 3)
        self.assertEqual(str(verse), "Matthew 5:3")
        self.assertEqual(verse.str(abbrev=True), "Matt 5:3")
        self.assertEqual(verse.str(alt_sep=True), "Matthew 5.3")
        self.assertEqual(verse.str(nospace=True), "Matthew5:3")
        self.assertEqual(verse.str(verse_parts=BVP.CHAP_VERSE), "5:3")

        verse = BibleVerse(BibleBook.IIIJn, 1, 4)
        self.assertEqual(str(verse), "3 John 4")
        self.assertEqual(verse.str(abbrev=True), "3Jn 4")
        self.assertEqual(verse.str(), "3 John 4")
        self.assertEqual(verse.str(nospace=True), "3John4")
        self.assertEqual(verse.str(verse_parts=BVP.CHAP_VERSE), "4")

    def test_bible_ranges(self):
        # Test each combination of args
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None, None, None), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 28, 20))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None, None, None), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 2, 23))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None, None, None), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 2, 3))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John, None, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 21, 25, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John, None, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 21, 25, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John, None, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 21, 25, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None,    4, None), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None,    4, None), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None,    4, None), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 4, 25))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None, None,    6), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 1, 6))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None, None,    6), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 2, 6))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None, None,    6), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 2, 6))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    5, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 5, 47, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    5, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 5, 47, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    5, None, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 5, 47, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None,    6,    7), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    8,   10, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 8, 10, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    8,   10, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 8, 10, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    8,   10, flags=BibleFlag.MULTIBOOK), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 8, 10, flags=BibleFlag.MULTIBOOK))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(BibleBook.Matt, None, 3, None, None, None))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(BibleBook.Matt, None, None, BibleBook.John, None, 6))

        # Test constructing a copy of a BibleRange
        bible_range = BibleRange("Matt 2:3-4:5")
        self.assertEqual(bible_range, BibleRange(bible_range))

        # Test start and end keyword args
        self.assertEqual(BibleRange("Matt 2:3-4:5"), BibleRange(start=BibleVerse("Matt 2:3"),
                         end=BibleVerse("Matt 4:5")))

        # Test string arg
        self.assertEqual(BibleRange("Matt", 2, 3, "Mark", 4, 5, flags=BibleFlag.MULTIBOOK),
                         BibleRange(BibleBook.Matt, 2, 3, BibleBook.Mark, 4, 5, flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange("Matthew 2:3-Mark 4:5", flags=BibleFlag.MULTIBOOK),
                         BibleRange(BibleBook.Matt, 2, 3, BibleBook.Mark, 4, 5, flags=BibleFlag.MULTIBOOK))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange("Matthew 2:3-4:5; Mark 5:6"))

        # Test multibook flag effect
        self.assertEqual(BibleRange("Matt-Mark", flags=BibleFlag.MULTIBOOK),
                         BibleRange(BibleBook.Matt, None, None, BibleBook.Mark, flags=BibleFlag.MULTIBOOK))
        self.assertRaises(MultibookRangeNotAllowedError,
                          lambda: BibleRange(BibleBook.Matt, None, None, BibleBook.Mark, flags=BibleFlag.NONE))

        # Test allow verse 0 flag effect
        self.assertEqual(BibleRange("Psa 3:0-3", flags=BibleFlag.VERSE_0),
                         BibleRange(BibleBook.Psa, 3, 0, None, None, 3, flags=BibleFlag.VERSE_0))
        self.assertRaises(InvalidReferenceError,
                          lambda: BibleRange(BibleBook.Psa, 3, 0, None, None, 3, flags=BibleFlag.NONE))

        # Test start and end reversal
        self.assertEqual(BibleRange("Matt 2:3-4:5"), BibleRange(end=BibleVerse("Matt 2:3"),
                         start=BibleVerse("Matt 4:5")))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(None, None, None, BibleBook.Matt, None, None))
        self.assertEqual(BibleRange(BibleBook.John, None, None, BibleBook.Matt, None, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt-John", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John, None, None, BibleBook.Matt,    2, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2-John", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John, None, None, BibleBook.Matt,    2,    3, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2:3-John", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    4, None,           None,    2, None), BibleRange("Matt 2-4"))
        self.assertEqual(BibleRange(BibleBook.Matt,    4, None,           None,    2,    3), BibleRange("Matt 2:3-Matt 4"))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(BibleBook.Matt, None, 6, None, None, None))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    6,           None, None,    3), BibleRange("Matt 2:3-6"))
        self.assertEqual(BibleRange(BibleBook.John,    5, None, BibleBook.Matt, None, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt-John 5", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John,    5, None, BibleBook.Matt,    2, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2-John 5", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John,    5, None, BibleBook.Matt,    2,    3, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2:3-John 5", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.Matt,    6,    7,           None,    2, None), BibleRange("Matt 2-6:7"))
        self.assertEqual(BibleRange(BibleBook.Matt,    6,    7,           None,    2,    3), BibleRange("Matt 2:3-6:7"))
        self.assertEqual(BibleRange(BibleBook.John,    8,   10, BibleBook.Matt, None, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt-John 8:10", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John,    8,   10, BibleBook.Matt,    2, None, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2-John 8:10", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(BibleRange(BibleBook.John,    8,   10, BibleBook.Matt,    2,    3, flags=BibleFlag.MULTIBOOK), BibleRange("Matt 2:3-John 8:10", flags=BibleFlag.MULTIBOOK))

    def test_bibleref_flags(self):
        orig_flags = bibleref.flags
        bibleref.flags = BibleFlag.NONE
        self.assertRaises(bibleref.ref.MultibookRangeNotAllowedError, lambda: BibleRange(BibleBook.Matt, None, None, BibleBook.John))
        self.assertRaises(bibleref.ref.InvalidReferenceError, lambda: BibleVerse(BibleBook.Psa, 3, 0))
        
        bibleref.flags = BibleFlag.ALL
        bible_range = BibleRange(BibleBook.Matt, None, None, BibleBook.John)
        bible_verse = BibleVerse(BibleBook.Psa, 3, 0)
        
        bibleref.flags = orig_flags

    def test_whole_bible(self):
        self.assertEqual(BibleRange.whole_bible(), BibleRange("Gen-Rev", flags=BibleFlag.MULTIBOOK))

    def test_bible_range_comparison(self):
        self.assertTrue(BibleRange("Matt 2:3-4:5") < BibleRange("Matt 2:3-4:6"))
        self.assertTrue(BibleRange("Matt 2:3-4:5") <= BibleRange("Matt 2:3-4:6"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") == BibleRange("Matt 2:3-4:6"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") >= BibleRange("Matt 2:3-4:6"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") > BibleRange("Matt 2:3-4:6"))

        self.assertTrue(BibleRange("Matt 2:3-4:5") < BibleRange("Matt 2:3-5:1"))
        self.assertTrue(BibleRange("Matt 2:3-4:5") <= BibleRange("Matt 2:3-5:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") == BibleRange("Matt 2:3-5:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") >= BibleRange("Matt 2:3-5:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") > BibleRange("Matt 2:3-5:1"))

        self.assertTrue(BibleRange("Matt 2:3-4:5") < BibleRange("Matt 2:4-3:1"))
        self.assertTrue(BibleRange("Matt 2:3-4:5") <= BibleRange("Matt 2:4-3:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") == BibleRange("Matt 2:4-3:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") >= BibleRange("Matt 2:4-3:1"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") > BibleRange("Matt 2:4-3:1"))

        self.assertTrue(BibleRange("Matt 2:3-4:5") < BibleRange("Matt 3:1-3:2"))
        self.assertTrue(BibleRange("Matt 2:3-4:5") <= BibleRange("Matt 3:1-3:2"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") == BibleRange("Matt 3:1-3:3"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") >= BibleRange("Matt 3:1-3:3"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") > BibleRange("Matt 3:1-3:3"))

        self.assertTrue(BibleRange("Matt 2:3-4:5") < BibleRange("Mark 1:2-3:4"))
        self.assertTrue(BibleRange("Matt 2:3-4:5") <= BibleRange("Mark 1:2-3:4"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") == BibleRange("Mark 1:2-3:4"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") >= BibleRange("Mark 1:2-3:4"))
        self.assertFalse(BibleRange("Matt 2:3-4:5") > BibleRange("Mark 1:2-3:4"))

    def test_bible_range_verse_0(self):
        range_with_0 = BibleRange("Ps 3:0-4:0", flags=BibleFlag.VERSE_0)
        range_with_1 = BibleRange("Ps 3:1-4:1", flags=BibleFlag.VERSE_0)
        no_verse_0 = BibleRange("Matt 2:3-4:5")
        self.assertEqual(range_with_0.verse_0_to_1(), range_with_1)
        self.assertEqual(range_with_1.verse_1_to_0(), range_with_0)
        self.assertEqual(no_verse_0.verse_0_to_1(), no_verse_0)
        self.assertEqual(no_verse_0.verse_1_to_0(), no_verse_0)

    def test_range_iteration(self):
        bible_range = BibleRange(BibleBook.Matt, 28, 18, BibleBook.Mark, 1, 3, flags=BibleFlag.MULTIBOOK)
        expected_list = [
            BibleVerse(BibleBook.Matt, 28, 18),
            BibleVerse(BibleBook.Matt, 28, 19),
            BibleVerse(BibleBook.Matt, 28, 20),
            BibleVerse(BibleBook.Mark, 1, 1),
            BibleVerse(BibleBook.Mark, 1, 2),
            BibleVerse(BibleBook.Mark, 1, 3),                         
        ]
        self.assertEqual(list(bible_range), expected_list)       

    def test_range_ranges(self):
        bible_range = BibleRange("Matt 3:8-John 4:9", flags=BibleFlag.MULTIBOOK)
        self.assertEqual(bible_range.chap_range(), BibleRange("Matt 3-John 4", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(bible_range.book_range(), BibleRange("Matt-John", flags=BibleFlag.MULTIBOOK))

    def test_range_counts(self):
        # Multi-book range
        bible_range = BibleRange("1 John 1:5-3 John 8", flags=BibleFlag.MULTIBOOK)
        self.assertEqual(bible_range.verse_count(), 122)
        self.assertEqual(bible_range.chap_count(), 7)
        self.assertEqual(bible_range.chap_count(whole=True), 5)
        self.assertEqual(bible_range.book_count(), 3)
        self.assertEqual(bible_range.book_count(whole=True), 1)

        # Range across 3 chapters
        bible_range = BibleRange("1 John 1:5-3:10", flags=BibleFlag.MULTIBOOK)
        self.assertEqual(bible_range.verse_count(), 45)
        self.assertEqual(bible_range.chap_count(), 3)
        self.assertEqual(bible_range.chap_count(whole=True), 1)
        self.assertEqual(bible_range.book_count(), 1)
        self.assertEqual(bible_range.book_count(whole=True), 0)

        # Range across 2 chapters
        bible_range = BibleRange("1 John 1:5-2:11", flags=BibleFlag.MULTIBOOK)
        self.assertEqual(bible_range.verse_count(), 17)
        self.assertEqual(bible_range.chap_count(), 2)
        self.assertEqual(bible_range.chap_count(whole=True), 0)
        self.assertEqual(bible_range.book_count(), 1)
        self.assertEqual(bible_range.book_count(whole=True), 0)

        # Range across 1 chapter
        bible_range = BibleRange("3 John 5-10")
        self.assertEqual(bible_range.verse_count(), 6)
        self.assertEqual(bible_range.chap_count(), 1)
        self.assertEqual(bible_range.chap_count(whole=True), 0)
        self.assertEqual(bible_range.book_count(), 1)
        self.assertEqual(bible_range.book_count(whole=True), 0)

    def test_range_split(self):
        ref = BibleRange("Matt 1:5-John 10:11", flags=BibleFlag.MULTIBOOK)
        split = ref.split()
        self.assertEqual(split, BibleRangeList("Matt 1:5-John 10:11", flags=BibleFlag.MULTIBOOK))

        ref = BibleRange("Matt 1:5-John 10:11", flags=BibleFlag.MULTIBOOK)
        split = ref.split(by_book=True)
        self.assertEqual(split, BibleRangeList("Matt 1:5-28:20; Mark; Luke; John 1-10:11"))

        ref = BibleRange("John 1:11-10:5")
        split = ref.split(by_chap=True)
        self.assertEqual(split, BibleRangeList("John 1:11-51; 2; 3; 4; 5; 6; 7; 8; 9; 10:1-5"))

        ref = BibleRange("John 1:1-11")
        split = ref.split(by_chap=False, num_verses=10)
        self.assertEqual(split, BibleRangeList("John 1:1-10, 11"))

        ref = BibleRange("John 1:11-10:5")
        split = ref.split(by_chap=False, num_verses=100)
        self.assertEqual(split, BibleRangeList("John 1:11-3:34; 3:35-5:44; 5:45-7:26; 7:27-9:14; 9:15-10:5"))

    def test_range_is_disjoint(self):
        test_range = BibleRange("Matt 1:10-15")
        
        self.assertTrue(test_range.is_disjoint(BibleVerse("Matt 1:9")))
        self.assertFalse(test_range.is_disjoint(BibleVerse("Matt 1:10")))        
        
        self.assertTrue(test_range.is_disjoint(BibleRange("Matt 1:5-9")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:5-10")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:5-11")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:10-12")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:11-14")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:13-15")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:10-15")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:14-20")))
        self.assertFalse(test_range.is_disjoint(BibleRange("Matt 1:15-20")))
        self.assertTrue(test_range.is_disjoint(BibleRange("Matt 1:16-20")))

        self.assertTrue(test_range.is_disjoint(BibleRangeList("Matt 1:16-20; Mark 9-11; Luke 13-15; John 17-19")))
        self.assertFalse(test_range.is_disjoint(BibleRangeList("Matt 1:15-20; Mark 9-11; Luke 12-15; John 17-19")))

    def test_range_is_adjacent(self):
        test_range = BibleRange("Matt 1:10-15")
        
        self.assertFalse(test_range.is_adjacent(BibleVerse("Matt 1:8")))
        self.assertTrue(test_range.is_adjacent(BibleVerse("Matt 1:9")))

        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:5-8")))
        self.assertTrue(test_range.is_adjacent(BibleRange("Matt 1:5-9")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:5-10")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:5-11")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:10-12")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:11-14")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:13-15")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:10-15")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:14-20")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:15-20")))
        self.assertTrue(test_range.is_adjacent(BibleRange("Matt 1:16-20")))
        self.assertFalse(test_range.is_adjacent(BibleRange("Matt 1:17-20")))

        self.assertTrue(test_range.is_adjacent(BibleRangeList("Matt 1:16-20; Mark 2-4; Luke 6-8")))
        self.assertTrue(test_range.is_adjacent(BibleRangeList("Matt 1:16-20; Mark 2-4; Matt 1:5-9")))
        self.assertFalse(test_range.is_adjacent(BibleRangeList("Matt 1:16-20; Mark 2-4; Matt 1:5-10")))

    def test_range_contains(self):
        test_range = BibleRange("Matt 2:20-3:7")
        self.assertFalse(BibleVerse("Matt 2:19") in test_range)
        self.assertTrue(BibleVerse("Matt 2:20") in test_range)
        self.assertTrue(BibleVerse("Matt 3:1") in test_range)
        self.assertTrue(BibleVerse("Matt 3:7") in test_range)
        self.assertFalse(BibleVerse("Matt 3:8") in test_range)

        test_range = BibleRange("Matt 1:10-15")
        self.assertFalse(BibleRange("Matt 1:5-8") in test_range)
        self.assertFalse(BibleRange("Matt 1:5-9") in test_range)
        self.assertFalse(BibleRange("Matt 1:5-10") in test_range)
        self.assertFalse(BibleRange("Matt 1:5-11") in test_range)
        self.assertTrue(BibleRange("Matt 1:10-12") in test_range)
        self.assertTrue(BibleRange("Matt 1:11-14") in test_range)
        self.assertTrue(BibleRange("Matt 1:13-15") in test_range)
        self.assertTrue(BibleRange("Matt 1:10-15") in test_range)
        self.assertFalse(BibleRange("Matt 1:14-20") in test_range)
        self.assertFalse(BibleRange("Matt 1:15-20") in test_range)
        self.assertFalse(BibleRange("Matt 1:16-20") in test_range)
        self.assertFalse(BibleRange("Matt 1:17-20") in test_range)

        test_range = BibleRange("Matt 4-8")
        self.assertTrue(BibleRangeList("Matt 4:1-5; 6:4-6; 8:10-12") in test_range)
        self.assertFalse(BibleRangeList("Matt 3:1-4:5; 6:4-6; 8:10-12") in test_range)
        self.assertFalse(BibleRangeList("Matt 4:1-5; 6:4-9:1; 8:10-12") in test_range)
        self.assertFalse(BibleRangeList("Matt 4:1-5; 6:4-6; 8-9:1") in test_range)

    def test_range_surrounds(self):
        test_range = BibleRange("Matt 1:10-15")
        self.assertFalse(test_range.surrounds(BibleVerse("Matt 1:9")))
        self.assertFalse(test_range.surrounds(BibleVerse("Matt 1:10")))
        self.assertTrue(test_range.surrounds(BibleVerse("Matt 1:11")))
        self.assertTrue(test_range.surrounds(BibleVerse("Matt 1:14")))
        self.assertFalse(test_range.surrounds(BibleVerse("Matt 1:15")))
        self.assertFalse(test_range.surrounds(BibleVerse("Matt 1:16")))

        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:5-8")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:5-9")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:5-10")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:5-11")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:10-12")))
        self.assertTrue(test_range.surrounds(BibleRange("Matt 1:11-14")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:13-15")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:10-15")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:14-20")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:15-20")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:16-20")))
        self.assertFalse(test_range.surrounds(BibleRange("Matt 1:17-20")))

        test_range = BibleRange("Matt 4-8")
        self.assertTrue(test_range.surrounds(BibleRangeList("Matt 4:2-5; 6:4-6; 8:10-33")))
        self.assertFalse(test_range.surrounds(BibleRangeList("Matt 4:1-5; 6:4-6; 8:10-33")))
        self.assertFalse(test_range.surrounds(BibleRangeList("Matt 4:2-5; 6:4-6; 8:10-34")))
        self.assertFalse(test_range.surrounds(BibleRangeList("Matt 4:2-5; 6:4-6; 8:10-33; 9:1")))
        self.assertFalse(test_range.surrounds(BibleRangeList("Matt 3:17; 4:2-5; 6:4-6; 8:10-33")))
        self.assertFalse(test_range.surrounds(BibleRangeList("Matt 4:2-5; 6:4-9:1; 8:10-33")))

    def test_range_union(self):
        test_range = BibleRange("Matt 1:10-15")

        self.assertEqual(test_range | BibleVerse("Matt 1:8"), BibleRangeList("Matt 1:8, 10-15"))
        self.assertEqual(test_range | BibleVerse("Matt 1:9"), BibleRangeList("Matt 1:9-15"))
        self.assertEqual(test_range | BibleVerse("Matt 1:10"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range | BibleVerse("Matt 1:11"), BibleRangeList("Matt 1:10-15"))

        self.assertEqual(test_range | BibleRange("Matt 1:5-8"), BibleRangeList("Matt 1:5-8, 10-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:5-9"), BibleRangeList("Matt 1:5-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:5-10"), BibleRangeList("Matt 1:5-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:5-11"), BibleRangeList("Matt 1:5-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:10-12"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:11-14"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:13-15"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:10-15"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range | BibleRange("Matt 1:14-20"), BibleRangeList("Matt 1:10-20"))
        self.assertEqual(test_range | BibleRange("Matt 1:15-20"), BibleRangeList("Matt 1:10-20"))
        self.assertEqual(test_range | BibleRange("Matt 1:16-20"), BibleRangeList("Matt 1:10-20"))
        self.assertEqual(test_range | BibleRange("Matt 1:17-20"), BibleRangeList("Matt 1:10-15, 17-20"))

        self.assertEqual(test_range | BibleRangeList("Matt 1:5-8; Mark 1-3"),
                         BibleRangeList("Matt 1:5-8, 10-15; Mark 1-3"))
        self.assertEqual(test_range | BibleRangeList("Matt 1:5-9; Mark 1-3"),
                         BibleRangeList("Matt 1:5-15; Mark 1-3"))
        self.assertEqual(test_range | BibleRangeList("Matt 1:5-10; Mark 1-3"),
                         BibleRangeList("Matt 1:5-15; Mark 1-3"))
        self.assertEqual(test_range | BibleRangeList("Mark 4-6; Matt 1:5-9, 16-20"),
                         BibleRangeList("Matt 1:5-20; Mark 4-6"))

    def test_range_intersection(self):
        test_range = BibleRange("Matt 1:10-15")

        self.assertEqual(test_range & BibleVerse("Matt 1:8"), BibleRangeList())
        self.assertEqual(test_range & BibleVerse("Matt 1:9"), BibleRangeList())
        self.assertEqual(test_range & BibleVerse("Matt 1:10"), BibleRangeList("Matt 1:10"))
        self.assertEqual(test_range & BibleVerse("Matt 1:11"), BibleRangeList("Matt 1:11"))

        self.assertEqual(test_range & BibleRange("Matt 1:5-8"), BibleRangeList())
        self.assertEqual(test_range & BibleRange("Matt 1:5-9"), BibleRangeList())
        self.assertEqual(test_range & BibleRange("Matt 1:5-10"), BibleRangeList("Matt 1:10"))
        self.assertEqual(test_range & BibleRange("Matt 1:5-11"), BibleRangeList("Matt 1:10-11"))
        self.assertEqual(test_range & BibleRange("Matt 1:10-12"), BibleRangeList("Matt 1:10-12"))
        self.assertEqual(test_range & BibleRange("Matt 1:11-14"), BibleRangeList("Matt 1:11-14"))
        self.assertEqual(test_range & BibleRange("Matt 1:13-15"), BibleRangeList("Matt 1:13-15"))
        self.assertEqual(test_range & BibleRange("Matt 1:10-15"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range & BibleRange("Matt 1:14-20"), BibleRangeList("Matt 1:14-15"))
        self.assertEqual(test_range & BibleRange("Matt 1:15-20"), BibleRangeList("Matt 1:15"))
        self.assertEqual(test_range & BibleRange("Matt 1:16-20"), BibleRangeList())
        self.assertEqual(test_range & BibleRange("Matt 1:17-20"), BibleRangeList())

        self.assertEqual(test_range & BibleRangeList("Matt 1:5-8; Mark 1-3"), BibleRangeList())
        self.assertEqual(test_range & BibleRangeList("Matt 1:5-9; Mark 1-3"), BibleRangeList())
        self.assertEqual(test_range & BibleRangeList("Matt 1:5-10; Mark 1-3; Matt 1:14-20"), BibleRangeList("Matt 1:10, 14-15"))
        self.assertEqual(test_range & BibleRangeList("Mark 4-6; Matt 1:5-11, 16-20"), BibleRangeList("Matt 1:10-11"))

    def test_range_difference(self):
        test_range = BibleRange("Matt 1:10-15")
        self.assertEqual(test_range - BibleRange("Matt 1:5-8"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:5-9"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:5-10"), BibleRangeList("Matt 1:11-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:5-11"), BibleRangeList("Matt 1:12-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:10-12"), BibleRangeList("Matt 1:13-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:10-14"), BibleRangeList("Matt 1:15"))
        self.assertEqual(test_range - BibleRange("Matt 1:11-14"), BibleRangeList("Matt 1:10, 15"))
        self.assertEqual(test_range - BibleRange("Matt 1:12-13"), BibleRangeList("Matt 1:10-11, 14-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:11-15"), BibleRangeList("Matt 1:10"))
        self.assertEqual(test_range - BibleRange("Matt 1:13-15"), BibleRangeList("Matt 1:10-12"))
        self.assertEqual(test_range - BibleRange("Matt 1:10-15"), BibleRangeList())
        self.assertEqual(test_range - BibleRange("Matt 1:9-16"), BibleRangeList())
        self.assertEqual(test_range - BibleRange("Matt 1:14-20"), BibleRangeList("Matt 1:10-13"))
        self.assertEqual(test_range - BibleRange("Matt 1:15-20"), BibleRangeList("Matt 1:10-14"))
        self.assertEqual(test_range - BibleRange("Matt 1:16-20"), BibleRangeList("Matt 1:10-15"))
        self.assertEqual(test_range - BibleRange("Matt 1:17-20"), BibleRangeList("Matt 1:10-15"))

    def test_range_sym_difference(self):
        test_range = BibleRange("Matt 1:10-15")
        self.assertEqual(test_range ^ BibleRange("Matt 1:5-8"), BibleRangeList("Matt 1:5-8, 10-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:5-9"), BibleRangeList("Matt 1:5-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:5-10"), BibleRangeList("Matt 1:5-9, 11-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:5-11"), BibleRangeList("Matt 1:5-9, 12-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:10-12"), BibleRangeList("Matt 1:13-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:10-14"), BibleRangeList("Matt 1:15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:11-14"), BibleRangeList("Matt 1:10, 15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:12-13"), BibleRangeList("Matt 1:10-11, 14-15"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:11-15"), BibleRangeList("Matt 1:10"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:13-15"), BibleRangeList("Matt 1:10-12"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:10-15"), BibleRangeList())
        self.assertEqual(test_range ^ BibleRange("Matt 1:9-16"), BibleRangeList("Matt 1:9, 16"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:14-20"), BibleRangeList("Matt 1:10-13, 16-20"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:15-20"), BibleRangeList("Matt 1:10-14, 16-20"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:16-20"), BibleRangeList("Matt 1:10-20"))
        self.assertEqual(test_range ^ BibleRange("Matt 1:17-20"), BibleRangeList("Matt 1:10-15, 17-20"))

    def test_bible_range_to_string(self):
        rng = BibleRange(BibleBook.Rom, 1, 1, None, 16, 27)
        self.assertEqual(str(rng), "Romans")

        rng = BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 21, 25, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Matthew-John")

        rng = BibleRange(BibleBook.Matt, 5, 6, BibleBook.John, 21, 25, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Matthew 5:6-John")

        rng = BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 10, 11, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Matthew-John 10:11")

        rng = BibleRange(BibleBook.Matt, 5, 6, BibleBook.John, 10, 11, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Matthew 5:6-John 10:11")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 7, 25)
        self.assertEqual(str(rng), "Exodus 7")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 10, 29)
        self.assertEqual(str(rng), "Exodus 7-10")

        rng = BibleRange(BibleBook.Exod, 7, 4, None, 10, 29)
        self.assertEqual(str(rng), "Exodus 7:4-10:29")

        rng = BibleRange(BibleBook.Exod, 7, 4, None, None, 8)
        self.assertEqual(str(rng), "Exodus 7:4-8")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 10, 12)
        self.assertEqual(rng.str(force_start_verses=False), "Exodus 7-10:12")
        self.assertEqual(rng.str(force_start_verses=True), "Exodus 7:1-10:12")

        rng = BibleRange(BibleBook.ICor, 15, 1, BibleBook.IICor, 1, 24, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "1 Corinthians 15-2 Corinthians 1")

        rng = BibleRange(BibleBook.Obad, 1, 10, None, 1, 12)
        self.assertEqual(str(rng), "Obadiah 10-12")

        rng = BibleRange(BibleBook.Obad, 1, 10, BibleBook.Jonah, 1, 4, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Obadiah 10-Jonah 1:4")

        rng = BibleRange(BibleBook.Obad, 1, 10, BibleBook.Jonah, 2, 10, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "Obadiah 10-Jonah 2")

        rng = BibleRange(BibleBook.IJn, 5, 18, BibleBook.IIIJn, 1, 14, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "1 John 5:18-3 John")

        rng = BibleRange(BibleBook.IIJn, 1, 1, BibleBook.IIIJn, 1, 14, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "2 John-3 John")

        rng = BibleRange(BibleBook.IIJn, 1, 6, BibleBook.IIIJn, 1, 14, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "2 John 6-3 John")

        rng = BibleRange(BibleBook.IIJn, 1, 1, BibleBook.IIIJn, 1, 8, flags=BibleFlag.MULTIBOOK)
        self.assertEqual(str(rng), "2 John-3 John 8")

    def test_bible_range_string_roundtrip(self):
        # For each Bible book, test that we can convert a range to a string and back again
        for book in BibleBook:
            if book.abbrev is None or book.title is None or book.regex is None:
                print(f"{book} lacks complete name data.")
                continue

            orig_range = BibleRange(book, 1, 1, None, 1, 2)

            # Test abbreviated strings
            string = orig_range.str(abbrev=True)
            final_range = BibleRange(string)
            self.assertEqual(orig_range, final_range)

            # Test full strings
            string = orig_range.str(abbrev=False)
            final_range = BibleRange(string)
            self.assertEqual(orig_range, final_range)

    def test_bible_range_list(self):
        range_list = BibleRangeList("Mark 3:1-4:2; Mark 5:6-8; Mark 5:10; Matt 4")
        expected_range_str = "Mark 3-4:2; 5:6-8, 10; Matt 4"
        self.assertEqual(range_list.str(abbrev=True, preserve_groups=False,
                                        force_start_verses=False), expected_range_str)

        range_list = BibleRangeList([BibleRange("Mark 3:1-4:2"), BibleRange("Mark 5:6-8"),
                                     BibleRange("Mark 5:10"), BibleRange("Matt 4")])
        self.assertEqual(range_list.str(abbrev=True, preserve_groups=False,
                                        force_start_verses=False), expected_range_str)

        range_list = BibleRangeList("Mark 3:1-4:2; Mark 5:6-8; Mark 5:10; Matt 4")
        self.assertEqual(range_list, BibleRangeList(range_list))

    def test_bible_range_list_verse_0(self):
        list_with_0 = BibleRangeList("Ps 3:0-4:0; Matt 2:3-4:5", flags=BibleFlag.VERSE_0)
        list_with_1 = BibleRangeList("Ps 3:1-4:1; Matt 2:3-4:5", flags=BibleFlag.VERSE_0)
        no_verse_0 = BibleRangeList("Matt 2:3-4:5; Mark 6:7-8:9")
        list_with_0.verse_0_to_1()
        self.assertEqual(list_with_0, list_with_1)
        list_with_0 = BibleRangeList("Ps 3:0-4:0; Matt 2:3-4:5", flags=BibleFlag.VERSE_0)
        list_with_1.verse_1_to_0()
        self.assertEqual(list_with_0, list_with_1)
        no_verse_0.verse_0_to_1()
        self.assertEqual(no_verse_0, BibleRangeList("Matt 2:3-4:5; Mark 6:7-8:9"))
        no_verse_0.verse_1_to_0()
        self.assertEqual(no_verse_0, BibleRangeList("Matt 2:3-4:5; Mark 6:7-8:9"))

    def test_range_list_ranges(self):
        range_list = BibleRangeList("John 4:9; Luke 1:12; Mark 7:3; Matt 3:8")
        self.assertEqual(range_list.range(), BibleRange("Matt 3:8-John 4:9", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(range_list.chap_range(), BibleRange("Matt 3-John 4", flags=BibleFlag.MULTIBOOK))
        self.assertEqual(range_list.book_range(), BibleRange("Matt-John", flags=BibleFlag.MULTIBOOK))

    def test_range_list_counts(self):
        range_list = BibleRangeList("1 John 1:5-3 John 8; 1 John 1:5-3:10; 1 John 1:5-2:11; 3 John 5-10",
                                    flags=BibleFlag.MULTIBOOK)
        self.assertEqual(range_list.verse_count(), 190)
        self.assertEqual(range_list.chap_count(), 13)
        self.assertEqual(range_list.chap_count(whole=True), 6)
        self.assertEqual(range_list.book_count(), 6)
        self.assertEqual(range_list.book_count(whole=True), 1)

    def test_regroup(self):
        range_list = BibleRangeList("Matt 1:4-7, 9-15, 17-20, Luke, John")
        range_list.regroup()
        self.assertEqual(range_list, BibleRangeList("Matt 1:4-7, 9-15, 17-20; Luke; John"))

        range_list = BibleRangeList("Matt 1:4-7, 9-15, 17-20, John 2, 3, Luke 2:1-5, 6-10, 11-15")
        range_list.regroup()
        self.assertEqual(range_list, BibleRangeList("Matt 1:4-7, 9-15, 17-20; John 2; 3; Luke 2:1-5, 6-10, 11-15"))

    def test_bible_range_list_merge(self):
        range_list = BibleRangeList("John; Luke; Matt 1:17-20, 12-15, 9-11, 5-7, 4-6", flags=BibleFlag.MULTIBOOK)
        range_list.sort()
        range_list.merge(flags=BibleFlag.NONE)
        self.assertEqual(range_list, BibleRangeList("Matt 1:4-7, 9-15, 17-20; Luke; John"))
        range_list.merge(flags=BibleFlag.MULTIBOOK)
        self.assertEqual(range_list, BibleRangeList("Matt 1:4-7, 9-15, 17-20; Luke-John", flags=BibleFlag.MULTIBOOK))

        # Test groups
        range_list = BibleRangeList([[BibleRange("Mark 3:1-4:2"), BibleRange("Mark 5:6-8")],
                                      [BibleRange("Mark 5:10"), BibleRange("Matt 4")]])
        self.assertEqual(len(range_list.groups), 2)
        self.assertEqual(range_list.groups[0][0], BibleRange("Mark 3:1-4:2"))
        self.assertEqual(range_list.groups[0][1], BibleRange("Mark 5:6-8"))
        self.assertEqual(range_list.groups[1][0], BibleRange("Mark 5:10"))
        self.assertEqual(range_list.groups[1][1], BibleRange("Matt 4"))

    def test_bible_range_list_is_disjoint(self):
        test_list = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")

        self.assertTrue(test_list.is_disjoint(BibleRangeList("Matt 5-7; Mark 9-11; Luke 13-15; John 17-19")))
        self.assertFalse(test_list.is_disjoint(BibleRangeList("Matt 5-7; Mark 9-11; Luke 12-15; John 17-19")))
        self.assertFalse(test_list.is_disjoint(BibleRangeList("Matt 5-7; Mark 8:38-Mark 11; Luke 13-15; John 17-19")))

    def test_bible_range_list_contains(self):
        test_list = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")

        self.assertTrue(test_list in BibleRangeList("Matt 2-3, 4-5; Mark 5-9; Luke 9-11, 12-13; John"))
        self.assertFalse(test_list in BibleRangeList("Matt 2-3, 5-7; Mark 5-9; Luke 9-11, 12-13; John"))
        self.assertFalse(test_list in BibleRangeList("Matt 2-3, 4-5; Mark 7-9; Luke 9-11, 12-13; John"))
        self.assertFalse(test_list in BibleRangeList("Matt 2-3, 4-5; Mark 6-9; Luke 10:2-Luke 12; John"))
        self.assertFalse(test_list in BibleRangeList("Matt 2-3, 4-5; Mark 6-9; Luke 10:2-Luke 12; John 14:2-John 16"))

    def test_bible_range_list_union(self):
        list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
        
        list_2 = BibleRangeList("John 1-3; Luke 9; Matt 3-5; Mark 12")
        self.assertEqual(list_1 | list_2, BibleRangeList("Matt 2-5; Mark 6-8; 12; Luke 9-12; John 1-3; 14-16"))

        list_2 = BibleRangeList("John 12-13; Luke 13-15; Mark 1-3; Matt 15-16")
        self.assertEqual(list_1 | list_2, BibleRangeList("Matt 2-4; 15-16; Mark 1-3; 6-8; Luke 10-15; John 12-16"))

    def test_bible_range_list_intersection(self):
        list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
        
        list_2 = BibleRangeList("John 1-3; Luke 9-10; Matt 3-5; Mark 12")
        self.assertEqual(list_1 & list_2, BibleRangeList("Matt 3-4; Luke 10"))

        list_2 = BibleRangeList("John 12-15; Luke 12-15; Mark 1-3; Matt 15-16")
        self.assertEqual(list_1 & list_2, BibleRangeList("Luke 12; John 14-15"))

    def test_bible_range_list_difference(self):
        list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-18")
        
        list_2 = BibleRangeList("John 1-3; Luke 9-10; Matt 3-5; Mark 12")
        self.assertEqual(list_1 - list_2, BibleRangeList("Matt 2; Mark 6-8; Luke 11-12; John 14-18"))

        list_2 = BibleRangeList("John 16; Luke 11; Mark 1-3; Matt 15-16")
        self.assertEqual(list_1 - list_2, BibleRangeList("Matt 2-4; Mark 6-8; Luke 10; 12; John 14-15; 17-18"))

    def test_bible_range_list_sym_difference(self):
        list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-18")
        
        list_2 = BibleRangeList("John 1-3; Luke 9-10; Matt 3-5; Mark 12")
        self.assertEqual(list_1 ^ list_2, BibleRangeList("Matt 2; 5; Mark 6-8; 12; Luke 9; 11-12; John 1-3; 14-18"))

        list_2 = BibleRangeList("John 16; Luke 11; Mark 1-3; Matt 15-16")
        self.assertEqual(list_1 ^ list_2,
                         BibleRangeList("Matt 2-4; 15-16; Mark 1-3; 6-8; Luke 10; 12; John 14-15; 17-18"))

    def test_bible_range_list_to_string(self):
        # Start range spans a book, after a ref from same book
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew-Mark", flags=BibleFlag.MULTIBOOK).str(),  # Start range spans book
            "Matthew 2:3-4:5; Matthew-Mark")

        # Start range spans a chapter from same book, when at verse level
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Don't force start verse to display
            "Matthew 2:3, Matthew 3-4:5").str(preserve_groups=False, force_start_verses=False),
            "Matthew 2:3; 3-4:5")
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Force start verse to display
            "Matthew 2:3, Matthew 3-4:5").str(preserve_groups=False, force_start_verses=True),
            "Matthew 2:3; 3:1-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after major sep.
            "Matthew 2:3; Matthew 3-4:5").str(force_start_verses=False),
            "Matthew 2:3; 3-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after major sep.
            "Matthew 2:3; Matthew 3-4:5").str(force_start_verses=True),
            "Matthew 2:3; 3:1-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after minor sep
            "Matthew 2:3, Matthew 3-4").str(),
            "Matthew 2:3, 3:1-4:25")
        # Start range spans a chapter from same book, when at chap level
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Don't force start verse to display
            "Matthew 2, Matthew 3-4:5").str(preserve_groups=False, force_start_verses=False),
            "Matthew 2; 3-4:5")
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Force start verse to display
            "Matthew 2, Matthew 3-4:5").str(preserve_groups=False, force_start_verses=True),
            "Matthew 2; 3:1-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after major sep
            "Matthew 2; Matthew 3-4:5").str(preserve_groups=False, force_start_verses=False),
            "Matthew 2; 3-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after major sep
            "Matthew 2; Matthew 3-4:5").str(preserve_groups=False, force_start_verses=True),
            "Matthew 2; 3:1-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups, after minor sep, spanning whole chaps
            "Matthew 2, Matthew 3:1-4:25").str(force_start_verses=False),
            "Matthew 2, 3-4")
        self.assertEqual(BibleRangeList(  # Preserve groups, after minor sep, spanning whole chaps
            "Matthew 2, Matthew 3:1-4:25").str(force_start_verses=True),
            "Matthew 2, 3-4")
        self.assertEqual(BibleRangeList(  # Preserve groups, after minor sep, spanning partial chaps
            "Matthew 2, Matthew 3:1-4:5").str(),
            "Matthew 2, 3:1-4:5")
        # Start range spans a chapter from different book
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Don't force start verse display
            "Matthew 2:3, Mark 3-4:5").str(preserve_groups=False, force_start_verses=False),
            "Matthew 2:3; Mark 3-4:5")
        self.assertEqual(BibleRangeList(  # Don't preserve groups. Force start verse display
            "Matthew 2:3, Mark 3-4:5").str(preserve_groups=False, force_start_verses=True),
            "Matthew 2:3; Mark 3:1-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups
            "Matthew 2:3, Mark 3-4:5").str(force_start_verses=False),
            "Matthew 2:3, Mark 3-4:5")
        self.assertEqual(BibleRangeList(  # Preserve groups
            "Matthew 2:3, Mark 3-4:5").str(force_start_verses=True),
            "Matthew 2:3, Mark 3:1-4:5")
  
        # Start range is just a verse from same book
        self.assertEqual(BibleRangeList(  # Same chap at verse level. End verse within same chap
            "Matthew 2:3, Matthew 2:6-10").str(),
            "Matthew 2:3, 6-10")
        self.assertEqual(BibleRangeList(  # Same chap at verse level. End verse in a different chap
            "Matthew 2:3, Matthew 2:6-5:7").str(),
            "Matthew 2:3, 2:6-5:7")
        self.assertEqual(BibleRangeList(  # Same chap at verse level. End verse in diff chap. Don't preserve groups.
            "Matthew 2:3, Matthew 2:6-5:7").str(preserve_groups=False),
            "Matthew 2:3; 2:6-5:7")
        self.assertEqual(BibleRangeList(  # Same chap at verse level. End verse in a different book
            "Matthew 2:3, Matthew 2:6-John 5:7", flags=BibleFlag.MULTIBOOK).str(),
            "Matthew 2:3, 2:6-John 5:7")
        self.assertEqual(BibleRangeList(  # Same chap at chap level, don't preserve groups
            "Matthew 2, Matthew 2:6-5:7").str(preserve_groups=False),
            "Matthew 2; 2:6-5:7")
        self.assertEqual(BibleRangeList(  # Same chap at chap level, preserve groups
            "Matthew 2, Matthew 2:6-5:7").str(),
            "Matthew 2, 2:6-5:7")
        self.assertEqual(BibleRangeList(  # Different chap, don't preserve groups
            "Matthew 2:3, Matthew 3:6-5:7").str(preserve_groups=False),
            "Matthew 2:3; 3:6-5:7")
        self.assertEqual(BibleRangeList(  # Different chap, preserve groups
            "Matthew 2:3, Matthew 3:6-5:7").str(),
            "Matthew 2:3, 3:6-5:7")
        # Start range is just a verse from a different book
        self.assertEqual(BibleRangeList(  # Don't preserve groups
            "Matthew 2:3, Mark 2:6-5:7").str(preserve_groups=False),
            "Matthew 2:3; Mark 2:6-5:7")
        self.assertEqual(BibleRangeList(  # Preserve groups
            "Matthew 2:3, Mark 2:6-5:7").str(),
            "Matthew 2:3, Mark 2:6-5:7")

        # Start range is a whole book, after same book
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew").str(),
            "Matthew 2:3-4:5; Matthew")
        # Start range is a whole chapter, after same book
        self.assertEqual(BibleRangeList( # After major group separator
            "Matthew 2:3-4:5; Matthew 7").str(), 
            "Matthew 2:3-4:5; 7")
        self.assertEqual(BibleRangeList( # After minor group separator, don't preserve groups
            "Matthew 2:3-4:5, Matthew 7").str(preserve_groups=False),
            "Matthew 2:3-4:5; 7")
        self.assertEqual(BibleRangeList( # After minor group separator, preserve groups
            "Matthew 2:3-4:5, Matthew 7").str(),
            "Matthew 2:3-4:5, 7:1-29")
        # Start range is a single verse, after same book
        self.assertEqual(BibleRangeList( # After major group separator
            "Matthew 2:3-4:5; Matthew 10:3").str(),
            "Matthew 2:3-4:5; 10:3")
        self.assertEqual(BibleRangeList( # After minor group separator, don't preserve groups
            "Matthew 2:3-4:5, Matthew 10:3").str(preserve_groups=False),
            "Matthew 2:3-4:5; 10:3")
        self.assertEqual(BibleRangeList( # After minor group separator, preserve groups
            "Matthew 2:3-4:5, Matthew 10:3").str(),
            "Matthew 2:3-4:5, 10:3")

        # End range spans a book
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; 6:7-Mark", flags=BibleFlag.MULTIBOOK).str(),  # Start range spans book
            "Matthew 2:3-4:5; 6:7-Mark")
        # End range spans a chapter while at chapter level
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6-9").str(),  # From same book
            "Matthew 2:3-4:5; 6-9")
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6-Mark 3", flags=BibleFlag.MULTIBOOK).str(),  # From different book
            "Matthew 2:3-4:5; 6-Mark 3")
        # End range spans a chapter while at verse level
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6:2-9:38").str(),  # From same book
            "Matthew 2:3-4:5; 6:2-9:38")
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6:4-Mark 3", flags=BibleFlag.MULTIBOOK).str(),  # From different book
            "Matthew 2:3-4:5; 6:4-Mark 3")
        # End range is a particular verse
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6:2-9:5").str(),  # From same book
            "Matthew 2:3-4:5; 6:2-9:5")
        self.assertEqual(BibleRangeList(
            "Matthew 2:3-4:5; Matthew 6:4-Mark 3:8", flags=BibleFlag.MULTIBOOK).str(),  # From different book
            "Matthew 2:3-4:5; 6:4-Mark 3:8")

        # Major group separator returns us to chap level
        self.assertEqual(BibleRangeList( # After minor group separator, preserve groups
            "Matthew 2:3-4:5, 7, 9; 11-12").str(),
            "Matthew 2:3-4:5, 7, 9; 11-12")

        # Test preserving/not-preserving groups
        self.assertEqual(BibleRangeList( # 
            "Matthew 2:3-4:5, 7; Matthew 4:9, Matthew 11-12").str(), # Preserve groups by default
            "Matthew 2:3-4:5, 7; 4:9, 11:1-12:50")
        self.assertEqual(BibleRangeList( # 
            "Matthew 2:3-4:5, 7; Matthew 4:9, Matthew 11-12").str(preserve_groups=False),
            "Matthew 2:3-4:5, 7, 9; 11-12")


        # Test a variety of types
        self.assertEqual(BibleRangeList(
            "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " + 
            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10").str(force_start_verses=False),
            "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " +
            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
        # Test a variety of types, with abbreviations
        self.assertEqual(BibleRangeList(
            "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " + 
            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10").str(abbrev=True, force_start_verses=False),
            "Matt; Mark 2; Jude 5; 8; Obad 2-3; John 3:16-18; 10-14:2; " +
            "Rom 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
        # Test a variety of types, with abbreviations, with alt verse separator
        self.assertEqual(BibleRangeList(
            "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " + 
            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10").str(abbrev=True, alt_sep=True, force_start_verses=False),
            "Matt; Mark 2; Jude 5; 8; Obad 2-3; John 3.16-18; 10-14.2; " +
            "Rom 1.10-22; 2; 3.20-22, 24, 4.2-5.2, 10")
        # Test a variety of types, with abbreviations, with alt verse separator, with no space
        self.assertEqual(BibleRangeList(
            "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " + 
            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10").str(abbrev=True, alt_sep=True, nospace=True,
                                                               force_start_verses=False),
            "Matt;Mark2;Jude5;8;Obad2-3;John3.16-18;10-14.2;" +
            "Rom1.10-22;2;3.20-22,24,4.2-5.2,10")

    def test_bible_range_list_sort(self):
        range_list_str = "Matt 2:3-4:5; Mark 3:4-5:6; Mark 3:4-5:5; Gen 1:2-3:4; " + \
                         "Matt 2:3-4:4; 1 Sam 2:2-3:3; Matt 1:2-11:1"
        range_list = BibleRangeList(range_list_str)
        range_list.sort()
        sorted_list_str = range_list.str(abbrev=True, preserve_groups=False)
        expected_list_str = "Gen 1:2-3:4; 1Sam 2:2-3:3; Matt 1:2-11:1; 2:3-4:4; " + \
                            "2:3-4:5; Mark 3:4-5:5; 3:4-5:6"
        self.assertEqual(sorted_list_str, expected_list_str)
        self.assertEqual(range_list._first.value, BibleRange("Gen 1:2-3:4"))
        self.assertEqual(range_list._last.value, BibleRange("Mark 3:4-5:6"))