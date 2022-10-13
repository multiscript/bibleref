from pathlib import Path
from pprint import pprint
import unittest

from lark import Lark
from lark.visitors import VisitError

from bible.reference import BibleBook, BibleRange
from bible.parser import GRAMMAR_FILE_NAME, BibleRefTransformer


class TestBibleParser(unittest.TestCase):
    def test_parse(self):
        grammar_path = Path(__file__, "../../bible", GRAMMAR_FILE_NAME).resolve()
        with open(grammar_path) as file:
                    grammar_text = file.read()
        print("Creating parser...")
        parser = Lark(grammar_text, propagate_positions=True)
        print("Parsing...")
        tree = parser.parse("Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3.16-18; " + 
                            "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
        try:
            top_list = BibleRefTransformer().transform(tree)
        except VisitError as e:
            raise e.orig_exc
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
