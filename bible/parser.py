from pathlib import Path

from lark import Lark, Transformer


GRAMMAR_FILE_NAME = "bible-reference.lark"


class BibleRefTransformer(Transformer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_book = None
        self.cur_chap_num = None
        self.at_verse_level = False

    def book_only_ref(self, children):
        book = children[0]
        self.cur_book = book
        self.at_verse_level = False
        return (book, None, None)

    def book_num_ref(self, children):
        book = children[0]
        chap_num = children[1] # Unless it's a single chapter book.
        self.cur_book = book
        self.cur_chap_num = chap_num # Unless it's a single chapter book.
        self.at_verse_level = False # Unless it's a single chapter book.
        return (book, chap_num, None)

    def book_chap_verse_ref(self, children):
        book = children[0]
        chap_num = children[1]
        verse_num = children [3]
        self.cur_book = book
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return (book, chap_num, verse_num)

    def chap_verse_ref(self, children):
        if self.cur_book is None:
            raise Exception("No book specified.")
        chap_num = children[0]
        verse_num = children [2]
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        return (self.cur_book, chap_num, verse_num)

    def num_only_ref(self, children):
        if self.cur_book is None:
            raise Exception("No book specified.")
        book = self.cur_book
        if not self.at_verse_level:
            chap_num = children[0] # Unless it's a single chapter book.
            verse_num = None
            self.cur_book = book
            self.cur_chap_num = chap_num # Unless it's a single chapter book.
            self.at_verse_level = False # Unless it's a single chapter book.
        else:
            if self.cur_chap_num is None:
                raise Exception("No chapter specified") # Is it even possible to get here?
            chap_num = self.cur_chap_num
            verse_num = children[0]
        return (book, chap_num, verse_num)

    def MAJOR_LIST_SEP(self, token):
        self.at_verse_level = False
        return token

    def BOOK_NAME(self, token):
        return str(token)

    def NUM(self, token):
        return int(token)

def parse():
    grammar_path = Path(__file__, "..", GRAMMAR_FILE_NAME).resolve()
    with open(grammar_path) as file:
                grammar_text = file.read()
    parser = Lark(grammar_text)
    tree = parser.parse("Matthew; Mark 2; John 3:16-18; Romans 1:10-22; 2; 3:20-22, 24, 26")
    tree = BibleRefTransformer().transform(tree)
    print(tree)
    print(tree.pretty())


if __name__ == '__main__':
    parse()