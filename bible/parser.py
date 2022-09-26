from pathlib import Path

from lark import Lark

GRAMMAR_FILE_NAME = "bible-reference.lark"

def parse():
    grammar_path = Path(__file__, "..", GRAMMAR_FILE_NAME).resolve()
    with open(grammar_path) as file:
                grammar_text = file.read()
    parser = Lark(grammar_text)
    tree = parser.parse("John 3:16-18; Romans 1:10-22; 3:20-22, 24")
    print(tree.pretty())


if __name__ == '__main__':
    parse()