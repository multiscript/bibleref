'''Submodule for parsing strings into Bible references. The contents of this submodule should be considered an
implementation detail and not relied upon.
'''
from lark import Lark, UnexpectedInput
from lark import Transformer, v_args
from lark.visitors import VisitError

import bibleref
from bibleref import ref, bible_data


MAJOR_LIST_SEP_SENTINEL = object()
MINOR_LIST_SEP_SENTINEL = object()


_parser_obj = None

def _parser():
    '''Return a Lark parser singleton.'''
    global _parser_obj
    if _parser_obj is None:
        # from pathlib import Path
        # GRAMMAR_FILE_NAME = "bible-reference.lark"
        # grammar_path = Path(__file__, "..", GRAMMAR_FILE_NAME).resolve()
        # with open(grammar_path) as file:
        #     grammar_text = file.read()
        _recreate_parser()
    return _parser_obj


_transformer_obj = None

def _transformer():
    '''Return a Lark Transformer singleton.'''
    global _transformer_obj

    if _transformer_obj is None:
        _transformer_obj = _BibleRefTransformer()
    return _transformer_obj


def _parse(string, flags: ref.BibleFlag = None):
    '''Parse `string` as a `bibleref.ref.BibleRefList` using `BibleRefTransformer`.'''
    try:
        tree = _parser().parse(string)
    except UnexpectedInput as orig:
        start_pos=orig.pos_in_stream
        end_pos=orig.pos_in_stream + 1
        new_error = ref.BibleRefParsingError(f"Unexpected text: {string[start_pos:end_pos]}",
                                         start_pos, end_pos)
        new_error.orig = orig
        raise new_error
    
    try:
        flags = flags or bibleref.flags or ref.BibleFlag.NONE
        _transformer().flags = flags
        range_groups_list = _transformer().transform(tree)
    except VisitError as e:
        raise e.orig_exc
    return range_groups_list

def _meta_info_to_pos(meta_info):
    return (meta_info.start_pos, meta_info.end_pos)

@v_args(meta=True)
class _BibleRefTransformer(Transformer):
    '''Lark Transformer for parsing strings into Bible references.'''
    def __init__(self, *args, flags: ref.BibleFlag = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_book = None            # Tracks implied current book
        self.cur_chap_num = None        # Tracks implied current chapter
        self.at_verse_level = False     # If try, bare numbers represent verses, otherwise chapters.
        self.flags = flags

    def ref_list(self, meta, children):
        '''Returns a list of group lists.'''
        parent_list = []
        group_list = []
        for child in children:
            if child is MAJOR_LIST_SEP_SENTINEL:
                if len(group_list) > 0:
                    parent_list.append(group_list)
                    group_list = []
            elif child is MINOR_LIST_SEP_SENTINEL:
                pass
            else: # It's a BibleRange
                group_list.append(child)
        if len(group_list) > 0:
            parent_list.append(group_list)
            group_list = []
        return parent_list

    def dual_ref(self, meta, children): # Children: single_ref RANGE_SEP single_ref
        first: ref.BibleRange = children[0]
        second: ref.BibleRange = children[2]
        # We don't need to update self.cur_book or self.cur_chap_num as they will
        # have already been updated by the parsing of the second BibleRange child.
        try:
            bible_range = ref.BibleRange(first.start.book, first.start.chap_num, first.start.verse_num,
                                               second.end.book, second.end.chap_num, second.end.verse_num,
                                               flags=self.flags)
        except Exception as e:
            raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range

    def book_only_ref(self, meta, children): # Children: BOOK_NAME
        book: ref.BibleBook = children[0]
        self.cur_book = book
        self.at_verse_level = False
        try:
            bible_range = ref.BibleRange(book, flags=self.flags)
        except Exception as e:
            raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range
        
    def book_num_ref(self, meta, children): # Children: BOOK_NAME NUM
        book: ref.BibleBook = children[0]
        num: int = children[1]
        self.cur_book = book
        # For single-chapter books, bare numbers represent verses instead of chapters
        is_single_chap = (book.chap_count() == 1)
        self.at_verse_level = is_single_chap
        try:
            if is_single_chap:
                self.cur_chap_num = book.min_chap_num()
                bible_range = ref.BibleRange(book, self.cur_chap_num, num,
                                                   flags=self.flags)
            else:
                self.cur_chap_num = num
                bible_range = ref.BibleRange(book, num, flags=self.flags)
        except Exception as e:
            raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range

    def book_chap_verse_ref(self, meta, children): # Children: BOOK_NAME NUM VERSE_SEP NUM
        book: ref.BibleBook = children[0]
        chap_num: int = children[1]
        verse_num: int = children [3]
        self.cur_book = book
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        try:
            bible_range = ref.BibleRange(book, chap_num, verse_num, flags=self.flags)
        except Exception as e:
            raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range

    def chap_verse_ref(self, meta, children): # Children: NUM VERSE_SEP NUM
        if self.cur_book is None:
            raise ref.BibleRefParsingError("No book specified", *_meta_info_to_pos(meta))
        book: ref.BibleBook = self.cur_book
        chap_num: int = children[0]
        verse_num: int = children [2]
        self.cur_chap_num = chap_num
        self.at_verse_level = True
        try:
            bible_range = ref.BibleRange(book, chap_num, verse_num, flags=self.flags)
        except Exception as e:
            raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range

    def num_only_ref(self, meta, children): # Children: NUM
        if self.cur_book is None:
            raise ref.BibleRefParsingError("No book specified", *_meta_info_to_pos(meta))
        book: ref.BibleBook = self.cur_book
        num: int = children[0]
        is_single_chap = (book.chap_count() == 1)
        try:
            if self.at_verse_level or is_single_chap: # Book, chapter, verse ref
                if is_single_chap:
                    self.cur_chap_num = book.min_chap_num()
                elif self.cur_chap_num is None:
                    raise ref.BibleRefParsingError("No chapter specified", *_meta_info_to_pos(meta))
                bible_range = ref.BibleRange(book, self.cur_chap_num, num, flags=self.flags)
            else: # Book, chapter ref
                bible_range = ref.BibleRange(book, num, flags=self.flags)
        except Exception as e:
            if isinstance(e, ref.BibleRefParsingError):
                raise e
            else:
                raise ref.BibleRefParsingError(str(e), *_meta_info_to_pos(meta))
        return bible_range

    def MAJOR_LIST_SEP(self, token):
        # Major list separator means subsequent bare numbers are chapter numbers
        self.at_verse_level = False
        return MAJOR_LIST_SEP_SENTINEL

    def MINOR_LIST_SEP(self, token):
        return MINOR_LIST_SEP_SENTINEL

    def BOOK_NAME(self, token):
        book = ref.BibleBook.from_str(str(token))
        if book is None:
            raise ref.BibleRefParsingError(f"{str(token)} is not a valid book name",
                                       token.start_pos, token.end_pos)
        return book

    def NUM(self, token):
        return int(token)

def _recreate_parser():
    global _parser_obj
    range_sep = bible_data().range_sep
    major_list_sep = bible_data().major_list_sep
    minor_list_sep = bible_data().minor_list_sep
    verse_sep_std = bible_data().verse_sep_std
    verse_sep_alt = bible_data().verse_sep_alt
    grammar = rf'''
        ?start: ref_list

        ref_list: bible_ref (list_sep bible_ref)* list_sep?

        ?bible_ref: (single_ref | dual_ref)

        dual_ref: single_ref RANGE_SEP single_ref

        ?single_ref: book_only_ref
                | book_num_ref
                | book_chap_verse_ref
                | chap_verse_ref
                | num_only_ref

        book_only_ref: BOOK_NAME
        book_num_ref: BOOK_NAME NUM
        book_chap_verse_ref: BOOK_NAME NUM VERSE_SEP NUM
        chap_verse_ref: NUM VERSE_SEP NUM
        num_only_ref: NUM

        NUM: INT

        RANGE_SEP: "{range_sep}"
        ?list_sep: MAJOR_LIST_SEP | MINOR_LIST_SEP
        MAJOR_LIST_SEP: "{major_list_sep}"
        MINOR_LIST_SEP: "{minor_list_sep}"
        VERSE_SEP: "{verse_sep_std}" | "{verse_sep_alt}"

        BOOK_NAME: /\w(\w|\s)*[^0-9\s\{verse_sep_std}\{verse_sep_alt}\{major_list_sep}\{minor_list_sep}\{range_sep}]/  
            // Books match as follows:
            // Can start with any 'word' (\w) character (incl. numbers)
            // Can include any amount of word characters or whitespace
            // Cannot end with a digit, or any of these symbols -> : . ; , -

        %import common.WS
        %import common.INT
        %ignore WS
    '''
    _parser_obj = Lark(grammar, propagate_positions=True)
