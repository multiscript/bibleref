from pathlib import Path

from lark import Lark, Transformer


GRAMMAR_FILE_NAME = "bible-reference.lark"


class BibleRefTransformer(Transformer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_book_name = None
        self.cur_chap_num = 0
    
    def book_only_ref(self, children):
        book = children[0]
        start_chap = 1
        start_verse = 1
        end_chap = 9999
        end_verse = 9999
        self.cur_book_name = book
        self.cur_chap_num = end_chap
        return (book, start_chap, start_verse, end_chap, end_verse)

    def book_num_ref(self, children):
        book = children[0]
        start_chap = children[1]
        start_verse = 1
        end_chap = start_chap
        end_verse = 9999
        self.cur_book_name = book
        self.cur_chap_num = end_chap
        return (book, start_chap, start_verse, end_chap, end_verse)

    def BOOK_NAME(self, token):
        return str(token)

    def CHAP_NUM(self, token):
        return int(token)

    def VERSE_NUM(self, token):
        return int(token)

    def NUM(self, token):
        return int(token)

def parse():
    grammar_path = Path(__file__, "..", GRAMMAR_FILE_NAME).resolve()
    with open(grammar_path) as file:
                grammar_text = file.read()
    parser = Lark(grammar_text)
    tree = parser.parse("Matthew; Mark 2; John 3:16-18; Romans 1:10-22; 3:20-22, 24")
    tree = BibleRefTransformer().transform(tree)
    print(tree)
    print(tree.pretty())


if __name__ == '__main__':
    parse()