from pprint import pprint
import unittest

from bible.reference import BibleBook, BibleRange
from bible.parser import BibleRefParsingError, _parse as parse

class TestBibleParser(unittest.TestCase):
    def test_parse(self):
        try:
            range_list = parse("Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3.16-18; " + 
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
            [BibleRange(BibleBook.Rom, 1, 10, None, None, 22)],                      
            [BibleRange(BibleBook.Rom, 2)],
            [
                BibleRange(BibleBook.Rom, 3, 20, None, None, 22),                      
                BibleRange(BibleBook.Rom, 3, 24),
                BibleRange(BibleBook.Rom, 4, 2, None, 5, 2),
                BibleRange(BibleBook.Rom, 5, 10),
            ]
        ]
        # pprint(range_list.to_nested_lists())
        # pprint(expected_list)
        self.assertEqual(range_list.to_nested_lists(), expected_list)
