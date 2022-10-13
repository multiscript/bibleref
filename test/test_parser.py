from pprint import pprint
import unittest


from bible.reference import BibleBook, BibleRange
from bible.parser import BibleRefParsingError, _parse as parse

class TestBibleParser(unittest.TestCase):
    def test_parse(self):
        try:
            top_list = parse("Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3.16-18; " + 
                            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
        except BibleRefParsingError as e:
            self.fail(str([str(e), e.start_pos, e.end_pos]))

        # print(tree.pretty())
        # pprint(top_list)
        expected_top_list = [
            [str(BibleRange(BibleBook.Matt))],
            [str(BibleRange(BibleBook.Mark, 2))],
            [str(BibleRange(BibleBook.Jude, 1, 5))],
            [str(BibleRange(BibleBook.Jude, 1, 8))],
            [str(BibleRange(BibleBook.Obad, 1, 2, None, None, 3))],
            [str(BibleRange(BibleBook.John, 3, 16, None, None, 18))],
            [str(BibleRange(BibleBook.Rom, 1, 10, None, None, 22))],                      
            [str(BibleRange(BibleBook.Rom, 2))],
            [
                str(BibleRange(BibleBook.Rom, 3, 20, None, None, 22)),                      
                str(BibleRange(BibleBook.Rom, 3, 24)),
                str(BibleRange(BibleBook.Rom, 4, 2, None, 5, 2)),
                str(BibleRange(BibleBook.Rom, 5, 10)),
            ]
        ]
        # pprint(expected_top_list)
        self.assertEqual(top_list, expected_top_list)
