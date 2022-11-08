import unittest
from bible.reference import BibleBook, BibleVerse, BibleRange, BibleRangeList, \
                            BibleVersePart as BVP, InvalidReferenceError


class TestBibleReference(unittest.TestCase):
    def test_bible_books(self):
        self.assertEqual(BibleBook.from_name("Gen"), BibleBook.Gen)
        self.assertEqual(BibleBook.from_name("Mt"), BibleBook.Matt)
        self.assertEqual(BibleBook.from_name("Rev"), BibleBook.Rev)
    
    def test_bible_verse_to_string(self):
        verse = BibleVerse(BibleBook.Matt, 5, 3)
        self.assertEqual(str(verse), "Matthew 5:3")
        self.assertEqual(verse.string(abbrev=True), "Matt 5:3")
        self.assertEqual(verse.string(alt_sep=True), "Matthew 5.3")
        self.assertEqual(verse.string(nospace=True), "Matthew5:3")
        self.assertEqual(verse.string(verse_parts=BVP.CHAP_VERSE), "5:3")

        verse = BibleVerse(BibleBook._3Jn, 1, 4)
        self.assertEqual(str(verse), "3 John 4")
        self.assertEqual(verse.string(abbrev=True), "3Jn 4")
        self.assertEqual(verse.string(), "3 John 4")
        self.assertEqual(verse.string(nospace=True), "3John4")
        self.assertEqual(verse.string(verse_parts=BVP.CHAP_VERSE), "4")

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
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None, None,    6), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 1, 6))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None, None,    6), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 2, 6))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None, None,    6), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 2, 6))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    5, None, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 5, 47, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None,           None,    6,    7), BibleRange(BibleBook.Matt, 1, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 1, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3,           None,    6,    7), BibleRange(BibleBook.Matt, 2, 3, BibleBook.Matt, 6, 7))
        self.assertEqual(BibleRange(BibleBook.Matt, None, None, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 8, 10, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2, None, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 1, BibleBook.John, 8, 10, allow_multibook=True))
        self.assertEqual(BibleRange(BibleBook.Matt,    2,    3, BibleBook.John,    8,   10, allow_multibook=True), BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 8, 10, allow_multibook=True))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(BibleBook.Matt, None, 3, None, None, None))
        self.assertRaises(InvalidReferenceError, lambda: BibleRange(BibleBook.Matt, None, None, BibleBook.John, None, 6))

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

    def test_bible_range_to_string(self):
        rng = BibleRange(BibleBook.Rom, 1, 1, None, 16, 27)
        self.assertEqual(str(rng), "Romans")

        rng = BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 21, 25, allow_multibook=True)
        self.assertEqual(str(rng), "Matthew-John")

        rng = BibleRange(BibleBook.Matt, 5, 6, BibleBook.John, 21, 25, allow_multibook=True)
        self.assertEqual(str(rng), "Matthew 5:6-John")

        rng = BibleRange(BibleBook.Matt, 1, 1, BibleBook.John, 10, 11, allow_multibook=True)
        self.assertEqual(str(rng), "Matthew-John 10:11")

        rng = BibleRange(BibleBook.Matt, 5, 6, BibleBook.John, 10, 11, allow_multibook=True)
        self.assertEqual(str(rng), "Matthew 5:6-John 10:11")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 7, 25)
        self.assertEqual(str(rng), "Exodus 7")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 10, 29)
        self.assertEqual(str(rng), "Exodus 7-10")

        rng = BibleRange(BibleBook.Exod, 7, 4, None, 10, 29)
        self.assertEqual(str(rng), "Exodus 7:4-10:29")

        rng = BibleRange(BibleBook.Exod, 7, 1, None, 10, 12)
        self.assertEqual(str(rng), "Exodus 7-10:12")

        rng = BibleRange(BibleBook._1Cor, 15, 1, BibleBook._2Cor, 1, 24, allow_multibook=True)
        self.assertEqual(str(rng), "1 Corinthians 15-2 Corinthians 1")

        rng = BibleRange(BibleBook.Obad, 1, 10, None, 1, 12)
        self.assertEqual(str(rng), "Obadiah 10-12")

        rng = BibleRange(BibleBook.Obad, 1, 10, BibleBook.Jonah, 1, 4, allow_multibook=True)
        self.assertEqual(str(rng), "Obadiah 10-Jonah 1:4")

        rng = BibleRange(BibleBook.Obad, 1, 10, BibleBook.Jonah, 2, 10, allow_multibook=True)
        self.assertEqual(str(rng), "Obadiah 10-Jonah 2")

        rng = BibleRange(BibleBook._1Jn, 5, 18, BibleBook._3Jn, 1, 14, allow_multibook=True)
        self.assertEqual(str(rng), "1 John 5:18-3 John")

        rng = BibleRange(BibleBook._2Jn, 1, 1, BibleBook._3Jn, 1, 14, allow_multibook=True)
        self.assertEqual(str(rng), "2 John-3 John")

        rng = BibleRange(BibleBook._2Jn, 1, 6, BibleBook._3Jn, 1, 14, allow_multibook=True)
        self.assertEqual(str(rng), "2 John 6-3 John")

        rng = BibleRange(BibleBook._2Jn, 1, 1, BibleBook._3Jn, 1, 8, allow_multibook=True)
        self.assertEqual(str(rng), "2 John-3 John 8")

    def test_bible_range_list_to_string(self):
        text_ranges = "Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3:16-18; 10-14:2; " + \
                      "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10"
        range_list = BibleRangeList.new_from_text(text_ranges)
        self.assertEqual(text_ranges, str(range_list))