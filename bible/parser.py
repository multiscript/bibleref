from pathlib import Path
from pprint import pprint

from lark import Lark, Transformer
from lark.visitors import VisitError

from .reference import BibleBook, BibleVerse, BibleRange


GRAMMAR_FILE_NAME = "bible-reference.lark"

MAJOR_LIST_SEP_SENTINEL = object()
MINOR_LIST_SEP_SENTINEL = object()

class BibleRefTransformer(Transformer):
    def __init__(self, allow_multibook: bool = None, allow_verse_0: bool = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_book = None            # Tracks implied current book
        self.cur_chap_num = None        # Tracks implied current chapter
        self.at_verse_level = False     # If try, bare numbers represent verses, otherwise chapters.
        self.allow_multibook = allow_multibook
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

    def dual_ref(self, children): # Children: single_ref RANGE_SEP single_ref
        first: BibleRange = children[0]
        second: BibleRange = children[2]
        # We don't need to update self.cur_book or self.cur_chap_num as they will
        # have already been updated by the parsing of the second BibleRange child.
        return BibleRange(first.start.book, first.start.chap, first.start.verse,
                          second.end.book, second.end.chap, second.end.verse,
                          allow_multibook_ranges=self.allow_multibook)

    def book_only_ref(self, children): # Children: BOOK_NAME
        book: BibleBook = children[0]
        self.cur_book = book
        self.at_verse_level = False
        return BibleRange(book)

    def book_num_ref(self, children): # Children: BOOK_NAME NUM
        book: BibleBook = children[0]
        num: int = children[1]
        self.cur_book = book
        # For single-chapter books, bare numbers represent verses instead of chapters
        is_single_chap = (book.chap_count() == 1)
        self.at_verse_level = is_single_chap
        if is_single_chap:
            self.cur_chap_num = book.min_chap()
            result = BibleRange(book, self.cur_chap_num, num)
        else:
            self.cur_chap_num = num
            result = BibleRange(book, num)
        return result

    def book_chap_verse_ref(self, children): # Children: BOOK_NAME NUM VERSE_SEP NUM
        book: BibleBook = children[0]
        chap_num: int = children[1]
        verse_num: int = children [3]
        self.cur_book = book
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return BibleRange(book, chap_num, verse_num)

    def chap_verse_ref(self, children): # Children: NUM VERSE_SEP NUM
        if self.cur_book is None:
            raise Exception("No book specified.")
        book: BibleBook = self.cur_book
        chap_num: int = children[0]
        verse_num: int = children [2]
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return BibleRange(book, chap_num, verse_num)

    def num_only_ref(self, children): # Children: NUM
        if self.cur_book is None:
            raise Exception("No book specified.")
        book: BibleBook = self.cur_book
        num: int = children[0]
        is_single_chap = (book.chap_count() == 1)
        if self.at_verse_level or is_single_chap: # Book, chapter, verse ref
            if is_single_chap:
                self.cur_chap_num = book.min_chap()
            elif self.cur_chap_num is None:
                raise Exception("No chapter specified") # Is it even possible to arrive here?
            result = BibleRange(book, self.cur_chap_num, num)
        else: # Book, chapter ref
            result = BibleRange(book, num)
        return result

    def MAJOR_LIST_SEP(self, token):
        # Majore list separator means subsequent bare numbers are chapter numbers
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
    tree = parser.parse("Matthew; Mark 2; Jude 5; 8; Obadiah 2-3; John 3.16-18; " + 
                        "Romans 1:10-22; 2; 3:20-22, 24, 4:2-5:2, 10")
    try:
        tree = BibleRefTransformer().transform(tree)
    except VisitError as e:
        raise e.orig_exc
    # print(tree.pretty())
    pprint(tree)


if __name__ == '__main__':
    parse()