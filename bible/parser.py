from pathlib import Path
from pprint import pprint

from lark import Lark, Transformer
from lark.visitors import VisitError

from .reference import BibleBook, BibleVerse, BibleRange


GRAMMAR_FILE_NAME = "bible-reference.lark"

MAJOR_LIST_SEP_SENTINEL = object()
MINOR_LIST_SEP_SENTINEL = object()

class BibleRefTransformer(Transformer):
    # TODO: Make better use of optional args to BibleRange
    def __init__(self, allow_multibook_ranges: bool = None, allow_verse_0: bool = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_book = None
        self.cur_chap_num = None
        self.at_verse_level = False
        self.allow_multibook_ranges = allow_multibook_ranges
        self.allow_verse_0 = allow_verse_0

    def ref_list(self, children):
        top_list = []
        group = []
        for child in children:
            if child is MAJOR_LIST_SEP_SENTINEL:
                if len(group) > 0:
                    top_list.append(group)
                    group = []
            elif child is MINOR_LIST_SEP_SENTINEL:
                pass
            else: # It's a BibleRange
                group.append(str(child))
        if len(group) > 0:
            top_list.append(group)
            group = []
        return top_list

    def dual_ref(self, children):
        first: BibleRange = children[0]
        second: BibleRange = children[2]
        return BibleRange(first.start.book, first.start.chap, first.start.verse,
                          second.end.book, second.end.chap, second.end.verse,
                          allow_multibook_ranges=self.allow_multibook_ranges)

    def book_only_ref(self, children):
        book: BibleBook = children[0]
        self.cur_book = book
        self.at_verse_level = False

        start_chap = book.min_chap()
        start_verse = book.min_verse(start_chap, self.allow_verse_0)
        end_chap = book.max_chap()
        end_verse = book.max_verse(end_chap)
        return BibleRange(book, start_chap, start_verse, book, end_chap, end_verse)

    def book_num_ref(self, children):
        book: BibleBook = children[0]
        num: int = children[1]
        self.cur_book = book

        single_chap = (book.chap_count() == 1)
        if single_chap:
            start_chap = end_chap = book.min_chap()
            start_verse = end_verse = num
            self.cur_chap_num = end_chap
            self.at_verse_level = True
        else:
            start_chap = end_chap = num
            start_verse = book.min_verse(start_chap, self.allow_verse_0)
            end_verse = book.max_verse(end_chap)
            self.cur_chap_num = end_chap            
            self.at_verse_level = False
        return BibleRange(book, start_chap, start_verse, book, end_chap, end_verse)

    def book_chap_verse_ref(self, children):
        book: BibleBook = children[0]
        chap_num: int = children[1]
        verse_num: int = children [3]
        self.cur_book = book
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return BibleRange(book, chap_num, verse_num, book, chap_num, verse_num)

    def chap_verse_ref(self, children):
        if self.cur_book is None:
            raise Exception("No book specified.")
        book: BibleBook = self.cur_book
        chap_num: int = children[0]
        verse_num: int = children [2]
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return BibleRange(book, chap_num, verse_num, book, chap_num, verse_num)

    def num_only_ref(self, children):
        if self.cur_book is None:
            raise Exception("No book specified.")
        book: BibleBook = self.cur_book
        num: int = children[0]
        single_chap = (book.chap_count() == 1)

        if self.at_verse_level or single_chap:
            if single_chap:
                self.cur_chap_num = book.min_chap()
            elif self.cur_chap_num is None:
                raise Exception("No chapter specified") # Is it even possible to get here?

            start_chap = end_chap = self.cur_chap_num
            start_verse = end_verse = num
        else: # We're at the chapter level
            start_chap = end_chap = num
            start_verse = book.min_verse(start_chap, self.allow_verse_0)
            end_verse = book.max_verse(end_chap)
        return BibleRange(book, start_chap, start_verse, book, end_chap, end_verse)

    def MAJOR_LIST_SEP(self, token):
        self.at_verse_level = False
        return MAJOR_LIST_SEP_SENTINEL

    def MINOR_LIST_SEP(self, token):
        return MINOR_LIST_SEP_SENTINEL

    def BOOK_NAME(self, token):
        book = BibleBook.from_name(str(token))
        if book is None:
            raise Exception(f"{str(token)} is not a valid book name.")
        return book

    def NUM(self, token):
        return int(token)


def parse():
    grammar_path = Path(__file__, "..", GRAMMAR_FILE_NAME).resolve()
    with open(grammar_path) as file:
                grammar_text = file.read()
    print("Creating parser...")
    parser = Lark(grammar_text)
    print("Parsing...")
    tree = parser.parse("Matthew; Mark 2; Jude 5; 8; John 3.16-18; Romans 1:10-22; 2; 3:20-22, 24, 26")
    try:
        tree = BibleRefTransformer().transform(tree)
    except VisitError as e:
        raise e.orig_exc
    # print(tree.pretty())
    pprint(tree)


if __name__ == '__main__':
    parse()