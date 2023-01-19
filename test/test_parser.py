from pprint import pprint
import unittest

from bibleref.ref import BibleBook, BibleRange, BibleRefParsingError
from bibleref.parser import _parse

class TestBibleParser(unittest.TestCase):
    def test_parse(self):
        try:
            range_groups_list = _parse("Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3.16-18; 10-14:2;" + 
                                      "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
        except BibleRefParsingError as e:
            self.fail(str([str(e), e.start_pos, e.end_pos]))

        # print(tree.pretty())
        # pprint(top_list)
        expected_list = [
            [BibleRange(BibleBook.Matt)],
            [BibleRange(BibleBook.Mark, 2)],
            [BibleRange(BibleBook.Jude, 1, 5)],
            [BibleRange(BibleBook.Jude, 1, 8)],
            [BibleRange(BibleBook.Obad, 1, 2, None, None, 3)],
            [BibleRange(BibleBook.John, 3, 16, None, None, 18)],
            [BibleRange(BibleBook.John, 10, 1, None, 14, 2)],
            [BibleRange(BibleBook.Rom, 1, 10, None, None, 22)],                      
            [BibleRange(BibleBook.Rom, 2)],
            [
                BibleRange(BibleBook.Rom, 3, 20, None, None, 22),                      
                BibleRange(BibleBook.Rom, 3, 24),
                BibleRange(BibleBook.Rom, 4, 2, None, 5, 2),
                BibleRange(BibleBook.Rom, 5, 10),
            ]
        ]
        pprint(range_groups_list)
        # pprint(expected_list)
        self.assertEqual(range_groups_list, expected_list)
