from collections.abc import MutableSequence
import copy
from dataclasses import dataclass
from enum import Enum
import re


allow_multibook = False     # Set to True to default to allowing a BibleRange to span multiple books.
                            # The default value can be overridden in individual methods.

allow_verse_0 = False       # Set to True to default to allowing verse 0 to be the first verse for some
                            # chapters (currently just Psalms with superscriptions).
                            # This default value can be overridden in individual methods.


class MultibookRangeNotAllowedError(Exception):
    pass


class InvalidReferenceError(Exception):
    pass


class BibleBook(Enum):
    '''An enum for specifying books in the Bible.

    Note that Python identifiers can't start with a number. So books like
    1 Samuel are written here as _1Sam.

    BibleBooks have the following extra attributes (added by the module):
      abbrev:   The abbreviated name of the book
      title:    The full title of the book.
      regex:    A regex which matches any acceptable name/abbrev for the book.
      order:    An integer indicating its ordering in the collection of books (0-based).
    '''
    # Extra private attributes:
    # _max_verses:  List of max verse number for each chapter (ascending by chapter).
    #               Len of list is number of chapters. 
    # _verse_0s:    If not None, set of chapter numbers (1-indexed) that can begin with a verse 0.
    #
    Gen = "Gen" 
    Exod = "Exod"
    Lev = "Lev"
    Num = "Num"
    Deut = "Deut"
    Josh = "Josh"
    Judg = "Judg"
    Ruth = "Ruth"
    _1Sam = "1Sam"
    _2Sam = "2Sam"
    _1Kgs = "1Kgs"
    _2Kgs = "2Kgs"
    _1Chr = "1Chr"
    _2Chr = "2Chr"
    Ezra = "Ezra"
    Neh = "Neh"
    Esth = "Esth"
    Job = "Job"
    Psa = "Psa"
    Prov = "Prov"
    Eccl = "Eccl"
    Song = "Song"
    Isa = "Isa"
    Jer = "Jer"
    Lam = "Lam"
    Ezek = "Ezek"
    Dan = "Dan"
    Hos = "Hos"
    Joel = "Joel"
    Amos = "Amos"
    Obad = "Obad"
    Jonah = "Jonah"
    Mic = "Mic"
    Nah = "Nah"
    Hab = "Hab"
    Zeph = "Zeph"
    Hag = "Hag"
    Zech = "Zech"
    Mal = "Mal"
    Matt = "Matt"
    Mark = "Mark"
    Luke = "Luke"
    John = "John"
    Acts = "Acts"
    Rom = "Rom"
    _1Cor = "1Cor"
    _2Cor = "2Cor"
    Gal = "Gal"
    Eph = "Eph"
    Phil = "Phil"
    Col = "Col"
    _1Thess = "1Thess"
    _2Thess = "2Thess"
    _1Tim = "1 Tim"
    _2Tim = "2 Tim"
    Titus = "Titus"
    Phlm = "Phlm"
    Heb = "Heb"
    James = "James"
    _1Pet = "1Pet"
    _2Pet = "2Pet"
    _1Jn = "1Jn"
    _2Jn = "2Jn"
    _3Jn = "3Jn"
    Jude = "Jude"
    Rev = "Rev"

    @classmethod
    def from_name(cls, name: str) -> 'BibleBook':
        '''Return BibleBook matching the given string name, or None if no book matches.
        '''
        name = name.strip()
        match = False
        for book in BibleBook:
            if book.regex.fullmatch(name) is not None:
                match = True
                break
        return book if match else None

    def min_chap(self) -> int:
        '''Return lowest chapter number (indexed from 1) for this BibleBook.
        '''
        return 1    # Currently always 1. Perhaps in future some books may have a chapter-0 prologue included?

    def max_chap(self) -> int:
        '''Return highest chapter number (indexed from 1) for this BibleBook.
        '''
        return len(self._max_verses)
    
    def chap_count(self):
        return (self.max_chap() - self.min_chap() + 1)

    def min_verse(self, chap: int, allow_verse_0: bool = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the specified chapter
        of this BibleBook. If allow_verse_0 is not None it overrides the module attribute
        with the same name. If True, some chapters can start with verse 0 (e.g. Psalm superscriptions).
        '''
        if allow_verse_0 is None:
            allow_verse_0 = globals()['allow_verse_0']
        if chap < self.min_chap() or chap > self.max_chap():
            raise InvalidReferenceError(f"No chapter {chap} in {self.title}")
        return 0 if (allow_verse_0 and chap in self._verse_0s) else 1

    def max_verse(self, chap: int) -> int:
        '''Return the highest verse number (usually indexed from 1) for the specified chapter
        numbr of this BibleBook.
        '''
        if chap < self.min_chap() or chap > self.max_chap():
            raise InvalidReferenceError(f"No chapter {chap} in {self.title}")
        return self._max_verses[chap-1]

    def next(self) -> 'BibleBook':
        '''Returns the next BibleBook in the book ordering, or None if this is the final book.
        '''
        if self.order == len(order)-1:
            return None
        else:
            return order[self.order+1]

    def prev(self) -> 'BibleBook':
        '''Returns the previous BibleBook in the book ordering, or None if this is the first book.
        '''
        if self.order == 0:
            return None
        else:
            return order[self.order-1]

    def __lt__(self, other):
        if not isinstance(other, BibleBook):
            return NotImplemented
        else:
            return self.order < other.order

    def __le__(self, other):
        if not isinstance(other, BibleBook):
            return NotImplemented
        else:
            return self.order <= other.order

    def __gt__(self, other):
        if not isinstance(other, BibleBook):
            return NotImplemented
        else:
            return self.order > other.order

    def __ge__(self, other):
        if not isinstance(other, BibleBook):
            return NotImplemented
        else:
            return self.order >= other.order


@dataclass(init=False, repr=False, eq=True, order=False, frozen=True)
class BibleVerse:
    '''A reference to a single Bible verse. Contains 3 attributes:
    
    book:   The BibleBook of the book of the reference.
    chap:   The chapter number (indexed from 1) of the reference.
    verse:  The verse number (usually indexed from 1) of the reference.

    BibleVerses are immutable.
    '''
    book:   BibleBook
    chap:   int
    verse:  int

    def __init__(self, book: BibleBook, chap: int, verse: int):
        '''Returns a new BibleVerse.

        If the supplied data is not valid, raises an InvalidReferenceError.
        '''
        if not isinstance(book, BibleBook):
            raise InvalidReferenceError(f"{book} is not an instance of BibleBook")
        if chap < book.min_chap() or chap > book.max_chap():
            raise InvalidReferenceError(f"No chapter {chap} in {book.title}")
        if verse < book.min_verse(chap) or verse > book.max_verse(chap):
            raise InvalidReferenceError(f"No verse {verse} in {book.title} {chap}")
        object.__setattr__(self, "book", book) # We have to use object.__setattr__ because the class is frozen
        object.__setattr__(self, "chap", chap)
        object.__setattr__(self, "verse", verse)
       
    def __repr__(self):
        return str((self.book.abbrev, self.chap, self.verse))

    def __str__(self):
        return self.string()

    def string(self, abbrev: bool = False, periods: bool = False, nospace: bool = False, nobook: bool = False):
        '''Returns a string representation of this BibleVerse.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If periods is True, chapter and verse numbers are separated by '.' instead of ':'.
        If nospace is True, no spaces are included in the string.
        If nobook is True, the book name is omitted.
        '''
        name = "" if nobook else (self.book.abbrev if abbrev else self.book.title)
        sep = "." if periods else ":"
        space = "" if nospace else " "
        return f"{name}{space}{str(self.chap)}{sep}{str(self.verse)}"

    def copy(self):
        return copy.copy(self)

    def add(self, num_verses: int, allow_multibook: bool = None, allow_verse_0: bool = None):
        ''' Returns a new BibleVerse that is the specified number of verses after this verse.
        
        If not None, allow_multibook and allow_verse_0 override the module attributes of the same names.
        If allow_multibook is True, and the result would be beyond the current book, a verse
        in a subsequent book is returned. Otherwise, if the verse does not exist, None is returned.
        '''
        if allow_multibook is None:
            allow_multibook = globals()['allow_multibook']
        if allow_verse_0 is None:
            allow_verse_0 = globals()['allow_verse_0']
        
        new_book = self.book
        new_chap = self.chap
        new_verse = self.verse + num_verses
        max_verse = new_book.max_verse(new_chap)
        while new_verse > max_verse:
            new_chap += 1
            if new_chap > new_book.max_chap():
                if not allow_multibook:
                    return None
                else:
                    new_book = new_book.next()
                    if new_book is None:
                        return None
                    new_chap = new_book.min_chap()
            
            new_verse = new_verse - max_verse - 1 + new_book.min_verse(new_chap, allow_verse_0)
            max_verse = new_book.max_verse(new_chap)

        return BibleVerse(new_book, new_chap, new_verse)

    def subtract(self, num_verses: int, allow_multibook: bool = None, allow_verse_0: bool = None):
        ''' Return a new BibleVerse that is the specified number of verses before this verse.
        
        Returns None if the result would not be a valid reference in the book.
        
        If not None, allow_multibook and allow_verse_0 override the module attributes of the same names.
        If allow_multibook is True, and the result would be before the current book, a verse
        in a previous book is returned. Otherwise, if the verse does not exist, None is returned.
        '''
        if allow_multibook is None:
            allow_multibook = globals()['allow_multibook']
        if allow_verse_0 is None:
            allow_verse_0 = globals()['allow_verse_0']
        
        new_book = self.book
        new_chap = self.chap
        new_verse = self.verse - num_verses
        min_verse = new_book.min_verse(new_chap, allow_verse_0)
        while new_verse < min_verse:
            new_chap -= 1
            if new_chap < new_book.min_chap():
                if not allow_multibook:
                    return None
                else:
                    new_book = new_book.prev()
                    if new_book is None:
                        return None
                    new_chap = new_book.max_chap()
             
            new_verse = new_verse + new_book.max_verse(new_chap)
            min_verse = new_book.min_verse(new_chap)

        return BibleVerse(new_book, new_chap, new_verse)

    def __lt__(self, other):
        if not isinstance(self, BibleVerse):
            return NotImplemented
        else:
            return (self.book < other.book) or \
                   (self.book == other.book and self.chap < other.chap) or \
                   (self.book == other.book and self.chap == other.chap and self.verse < other.verse)

    def __le__(self, other):
        if not isinstance(self, BibleVerse):
            return NotImplemented
        else:
            return (self.book < other.book) or \
                   (self.book == other.book and self.chap < other.chap) or \
                   (self.book == other.book and self.chap == other.chap and self.verse <= other.verse)

    def __gt__(self, other):
        if not isinstance(self, BibleVerse):
            return NotImplemented
        else:
            return (self.book > other.book) or \
                   (self.book == other.book and self.chap > other.chap) or \
                   (self.book == other.book and self.chap == other.chap and self.verse > other.verse)

    def __ge__(self, other):
        if not isinstance(self, BibleVerse):
            return NotImplemented
        else:
            return (self.book > other.book) or \
                   (self.book == other.book and self.chap > other.chap) or \
                   (self.book == other.book and self.chap == other.chap and self.verse >= other.verse)

    # def min_chap(self):
    #     '''Return lowest chapter number (indexed from 1) of the book of this BibleVerse.
    #     '''
    #     return self.book.min_chap()

    # def max_chap(self):
    #     '''Return highest chapter number (indexed from 1) of the book of this BibleVerse.
    #     '''
    #     return self.book.max_chap()

    def min_chap_verse(self, allow_verse_0: bool = None):
        '''Return the lowest verse number (usually indexed from 1) for the chapter of this BibleVerse.
        If allow_verse_0 is not None it overrides the module attribute of the same name. If True,
        chapters with superscriptions start with verse 0.
        '''
        return self.book.min_verse(self.chap, allow_verse_0)

    def max_chap_verse(self):
        '''Return the highest verse number (usually indexed from 1) for the chapter of this BibleVerse.
        '''
        return self.book.max_verse(self.chap)


@dataclass(init=False, repr=False, eq=True, order=False, frozen=True)
class BibleRange:
    '''A reference to a range of Bible verses. Contains 2 attributes:
    
    start:  The BibleVerse of the first verse in the range.
    end:    The BibleVerse of the last verse in the range.
    '''
    start: BibleVerse
    end: BibleVerse

    def __init__(self, start_book: BibleBook, start_chap: int = None, start_verse: int = None,
                end_book: BibleBook = None, end_chap: int = None, end_verse: int = None,
                validate: bool = True, allow_multibook: bool = None, allow_verse_0: bool = None):
        if allow_multibook is None:
            allow_multibook = globals()['allow_multibook']
        if allow_verse_0 is None:
            allow_verse_0 = globals()['allow_verse_0']

        if start_book is None or start_book not in BibleBook:
            raise InvalidReferenceError("Start book not valid")
        if start_chap is None and start_verse is not None:
            raise InvalidReferenceError("Start verse is missing a start chapter")

        no_end = (end_book is None and end_chap is None and end_verse is None)

        if start_chap is None: # Start is book only
            start_chap = start_book.min_chap()
            start_verse = start_book.min_verse(start_chap, allow_verse_0)
            if no_end:
                end_book = start_book
                end_chap = end_book.max_chap()
                end_verse = end_book.max_verse(end_chap)
        elif start_verse is None: # Start is book and chap only
            start_verse = start_book.min_verse(start_chap, allow_verse_0)
            if no_end:
                end_book = start_book
                end_chap = start_chap
                end_verse = end_book.max_verse(end_chap)
        else: # Start is book, chap and verse
            if no_end:
                end_book = start_book
                end_chap = start_chap
                end_verse = start_verse
        
        if not no_end: # We have end-point info
            if end_book is None:
                end_book = start_book
            if end_chap is None and end_verse is None: # End is book only
                end_chap = end_book.max_chap()
                end_verse = end_book.max_verse(end_chap)
            elif end_verse is None: # End is book and chap only
                end_verse = end_book.max_verse(end_chap)
            elif end_chap is None: # End is book and verse only
                if start_book != end_book:
                    raise InvalidReferenceError("End verse is missing an end chapter")
                else:
                    end_chap = start_chap

        if not allow_multibook and start_book != end_book:
            raise MultibookRangeNotAllowedError()

        object.__setattr__(self, "start", BibleVerse(start_book, start_chap, start_verse))
        object.__setattr__(self, "end", BibleVerse(end_book, end_chap, end_verse))

    def contains(self, bible_verse: BibleVerse) -> bool:
        '''Returns True if this BibleRange contains the given BibleVerse, otherwise False.
        '''
        return (bible_verse >= self.start and bible_verse <= self.end)

    def split(self, by_chap: bool = True, num_verses: bool = None, allow_verse_0: bool = None):
        '''Split this range into a list of smaller consecutive ranges.
        
        If by_chap is true, splits are made end of each chapter.
        If num_verses is specified, splits are made after no more than the specified number of verses.
        If both by_chap and num_verses are specified, splits occur both at chapter boundaries, and after
        the specified number of verses.
        '''
        if allow_verse_0 is None:
            allow_verse_0 = globals()['allow_verse_0']
        
        # Start by dividing our initial range into chapters, if requested.
        if by_chap:
            chap_split = []
            book = self.start.book
            chap = self.start.chap
            done = False
            while book <= self.end.book and chap <= self.end.chap:
                if book == self.start.book and chap == self.start.chap:
                    start_verse = self.start.verse
                else:
                    start_verse = book.min_verse(chap, allow_verse_0)
                if book == self.end.book and chap == self.end.chap:
                    end_verse = self.end.verse
                    done = True
                else:
                    end_verse = book.max_verse(chap)
                chap_split.append(BibleRange(book, chap, start_verse, book, chap, end_verse))
                
                if not done:
                    chap += 1
                    if chap > book.max_chap():
                        book = book.next()
                        chap = book.min_chap()
        else:
            chap_split = [BibleRange(self.start.book, self.start.chap, self.start.verse,
                                    self.end.book, self.end.chap, self.end.verse)]

        # Next, split our list of ranges into smaller ranges with a max numbers of verses, if requested.
        if num_verses is not None:
            verse_split = []
            for bible_range in chap_split:
                start = BibleVerse(bible_range.start.book, bible_range.start.chap, bible_range.start.verse)
                end = start.add(num_verses-1, allow_verse_0=allow_verse_0)
                while end is not None and end < bible_range.end:
                    verse_split.append(BibleRange(start.book, start.chap, start.verse, end.book, end.chap, end.verse))
                    start = end.add(1, allow_verse_0=allow_verse_0)
                    end = start.add(num_verses-1, allow_verse_0=allow_verse_0)
                verse_split.append(BibleRange(start.book, start.chap, start.verse,
                                   bible_range.end.book, bible_range.end.chap, bible_range.end.verse))
            return verse_split
        else:
            return chap_split

    def __repr__(self):
        return str((self.start.book.abbrev, self.start.chap, self.start.verse,
                    self.end.book.abbrev, self.end.chap, self.end.verse))
    
    def __str__(self):
        return self.string()

    def __iter__(self):
        verse = self.start
        while verse <= self.end:
            yield verse
            verse = verse.add(1, allow_multibook=True)

    def string(self, abbrev=False, periods=False, nospace=False, nobook=False):
        '''Returns a string representation of this BibleRange.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If periods is True, chapter and verse numbers are separated by '.' instead of ':'.
        If nospace is True, no spaces are included in the string.
        If nobook is True, the book name is omitted.
        '''
        # TODO Make this a proper implementation that doesn't double-print anything and handles multibook ranges.
        sep = "." if periods else ":"
        return self.start.string(abbrev, periods, nospace, nobook) + f"-{self.end.chap}{sep}{self.end.verse}"


class _LinkedList(MutableSequence):
    '''A linked list, with the ability to also group items.

    Groups are accessed using the groups property and created using append_group().
    '''
    # Derived from https://github.com/Superbird11/ranges/blob/master/ranges/_helper.py (MIT Licence)
    class Node:
        def __init__(self, value, prev=None, next=None, parent=None):
            self.value = value
            self.prev = prev
            self.next = next
            self.is_group_head: bool = False  # True if this node is the start of a group.
            self.prev_group = None # If this is a group head, link to next group head.
            self.next_group = None # If this is a group head, link to prev group head.
            self.parent = parent

        def __eq__(self, other):
            return self.value.__eq__(other.data)

        def __lt__(self, other):
            return self.value.__lt__(other.data)

        def __gt__(self, other):
            return self.value.__gt__(other.data)

        def __ge__(self, other):
            return self.value.__ge__(other.data)

        def __le__(self, other):
            return self.value.__le__(other.data)

        def __str__(self):
            return f"Node({str(self.value)})"

        def __repr__(self):
            return str(self)

    def __init__(self, iterable=None):
        self._first = None
        self._last = None
        self._node_count = 0
        if iterable is not None:
            for item in iterable:
                self.append(item)

    def _check_type(self, value):
        '''Subclasses can override to ensure list items are of a certain type'''
        pass

    def _check_is_child(self, node):
        if not isinstance(node, _LinkedList.Node) or node.parent is not self:
            raise ValueError(f"List is not the parent of this node: {node}")

    def _conform_index(self, index):
        ''' Check the index is within range. If negative, convert to its
        positive equivalent. Return the resulting index.
        '''
        if index < 0:
            index += self._node_count
        if index >= self._node_count:
            raise IndexError(f"List index {index} out of range")
        return index

    def _node_at(self, index):
        index = self._conform_index(index)
        if index <= self._node_count // 2:
            # Node is closer to the start, so search from there
            node = self._first
            for i in range(index):
                node = node.next
            return node
        else:
            # Node is closer to the end, so seach from there
            node = self._last
            for i in range(self._node_count - index - 1):
                node = node.prev
            return node

    def _insert_first(self, value):
        self._first = self.Node(value, parent=self)
        self._last = self._first
        self._node_count += 1

    def _insert_before(self, node, value):
        self._check_is_child(node)
        if node is self._first:
            self.prepend(value)
        else:
            new = self.Node(value, prev=node.prev, next=node, parent=self)
            node.prev.next = new
            node.prev = new
            self._node_count += 1

    def _insert_after(self, node, value):
        self._check_is_child(node)
        if node is self._last:
            self.append(value)
        else:
            new = self.Node(value, prev=node, next=node.next, parent=self)
            node.next.prev = new
            node.next = new
            self._node_count += 1

    def _pop_node(self, node):
        self._check_is_child(node)
        # pop only element
        if self._node_count == 1:
            self._first = None
            self._last = None
        # pop from start
        elif node is self._first:
            self._first = self._first.next
            self._first.prev = None
        # pop at end
        elif node is self._last:
            self._last = self._last.prev
            self._last.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        
        node.parent = None
        self._node_count -= 1
        return node.value

    def _pop_before(self, node):
        self._check_is_child(node)
        if node is self._first:
            raise IndexError("Can't pop before first node")
        return self._pop_node(node.prev)

    def _pop_after(self, node):
        self._check_is_child(node)
        if node is self._last:
            raise IndexError("Can't pop after last node")
        return self._pop_node(node.next)

    def prepend(self, value):
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            new = self.Node(value, next=self._first, parent=self)
            self._first.prev = new
            self._first = new
            self._node_count += 1

    def append(self, value):
        self._check_type(value)
        if self._node_count == 0:
            self._insert_first(value)
        else:
            new = self.Node(value, prev=self._last, parent=self)
            self._last.next = new
            self._last = new
            self._node_count += 1
    
    def insert(self, index, value):
        self._check_type(value)
        if index == 0:
            self.prepend(value)
        elif index == self._node_count:
            self.append(value)
        else:
            self._insert_before(self._node_at(index), value)

    def index(self, value, min_index=None, limit_index=None):
        if min_index is None:
            min_index = 0
        if limit_index is None:
            limit_index = self._node_count
        self._check_type(value)
        min_index = self._conform_index(min_index)
        limit_index = self._conform_index(limit_index-1) + 1
        if min_index > limit_index: # Swap
            (limit_index, min_index) = (min_index, limit_index)
        node: _LinkedList.Node = self._first
        for index in range(limit_index):
            if node.value == value and index >= min_index:
                return index
            node = node.next
        # At this point item not found
        raise ValueError(f"Item {value} not found in list")        
            
    def count(self, value):
        self._check_type(value)
        count = 0
        for node_value in self:
            if node_value == value:
                count += 1
        return count         

    def pop(self, index=None):
        if index is None:
            index = self._node_count - 1
        index = self._conform_index(index)
        return self._pop_node(self._node_at(index))

    def clear(self):
        self._first = None
        self._last = None
        self._length = 0

    def __len__(self):
        return self._node_count
    
    def __iter__(self):
        node = self._first
        while node is not None:
            yield node.value
            node = node.next

    def __contains__(self, value):
        self._check_type(value)
        for node_value in self:
            if node_value == value:
                return True
        # At this point item not found
        return False
 
    def __getitem__(self, index):
        return self._node_at(index).value

    def __setitem__(self, index, value):
        self._check_type(value)
        self._node_at(index).value = value

    def __delitem__(self, index):
        self.pop(index)

    def __reversed__(self):
        node = self._last
        while node is not None:
            yield node.value
            node = node.prev


class BibleRangeList(_LinkedList):
    def _check_type(self, value):
        if not isinstance(value, BibleRange):
            raise TypeError(f"Item is not a BibleRange: {value}")


    



name_data = {
    # Keys: Bible Book
    # Values: (Abbrev title, Full title, Min unique chars (excl. numbers), List of extra recognised abbrevs)
    #
    # The min unique chars is the minimum number of characters in the full title (after any initial "1 ",
    # "2 " or "3 " has been stripped out) needed to uniquely identify the book.
    #
    BibleBook.Gen:      ("Gen",     "Genesis",          2,   ["Gn"]),
    BibleBook.Exod:     ("Exod",    "Exodus",           2,   []),
    BibleBook.Lev:      ("Lev",     "Leviticus",        2,   ["Lv"]),
    BibleBook.Num:      ("Num",     "Numbers",          2,   ["Nm", "Nb"]),
    BibleBook.Deut:     ("Deut",    "Deuteronomy",      2,   ["Dt"]),
    BibleBook.Josh:     ("Josh",    "Joshua",           3,   ["Js", "Jsh"]),
    BibleBook.Judg:     ("Judg",    "Judges",           4,   ["Jg", "Jdg", "Jdgs"]),
    BibleBook.Ruth:     ("Ruth",    "Ruth",             2,   ["Ruth"]),
    BibleBook._1Sam:    ("1Sam",    "1 Samuel",         1,   ["1 Sm"]),
    BibleBook._2Sam:    ("2Sam",    "2 Samuel",         1,   ["2 Sm"]),
    BibleBook._1Kgs:    ("1Kgs",    "1 Kings",          1,   ["1 Kg", "1 Kgs"]),
    BibleBook._2Kgs:    ("2Kgs",    "2 Kings",          1,   ["2 Kg", "2 Kgs"]),
    BibleBook._1Chr:    ("1Chr",    "1 Chronicles",     2,   []),
    BibleBook._2Chr:    ("2Chr",    "2 Chronicles",     2,   []),
    BibleBook.Ezra:     ("Ezra",    "Ezra",             3,   []),
    BibleBook.Neh:      ("Neh",     "Nehemiah",         2,   []),
    BibleBook.Esth:     ("Esth",    "Esther",           2,   []),
    BibleBook.Job:      ("Job",     "Job",              3,   ["Jb"]),
    BibleBook.Psa:      ("Psa",     "Psalms",           2,   ["Pslm", "Psm", "Pss"]),
    BibleBook.Prov:     ("Prov",    "Proverbs",         2,   ["Prv"]),
    BibleBook.Eccl:     ("Eccl",    "Ecclesiastes",     2,   []),
    BibleBook.Song:     ("Song",    "Song of Songs",    2,   ["Song of Sol", "Song of Solo", "Song of Solomon", "SOS"]),
    BibleBook.Isa:      ("Isa",     "Isaiah",           2,   []),
    BibleBook.Jer:      ("Jer",     "Jeremiah",         2,   ["Jr"]),
    BibleBook.Lam:      ("Lam",     "Lamentations",     2,   []),
    BibleBook.Ezek:     ("Ezek",    "Ezekiel",          3,   ["Ezk"]),
    BibleBook.Dan:      ("Dan",     "Daniel",           2,   ["Dn"]),
    BibleBook.Hos:      ("Hos",     "Hosea",            2,   []),
    BibleBook.Joel:     ("Joel",    "Joel",             3,   ["Jl"]),
    BibleBook.Amos:     ("Amos",    "Amos",             2,   []),
    BibleBook.Obad:     ("Obad",    "Obadiah",          2,   ["Obd"]),
    BibleBook.Jonah:    ("Jonah",   "Jonah",            3,   ["Jnh"]),
    BibleBook.Mic:      ("Mic",     "Micah",            2,   ["Mc"]),
    BibleBook.Nah:      ("Nah",     "Nahum",            2,   []),
    BibleBook.Hab:      ("Hab",     "Habakkuk",         3,   ["Hbk"]),
    BibleBook.Zeph:     ("Zeph",    "Zephaniah",        3,   ["Zp", "Zph"]),
    BibleBook.Hag:      ("Hag",     "Haggai",           3,   ["Hg"]),
    BibleBook.Zech:     ("Zech",    "Zechariah",        3,   ["Zc"]),
    BibleBook.Mal:      ("Mal",     "Malachi",          3,   ["Ml"]),
    BibleBook.Matt:     ("Matt",    "Matthew",          3,   ["Mt"]),
    BibleBook.Mark:     ("Mark",    "Mark",             3,   ["Mk", "Mrk"]),
    BibleBook.Luke:     ("Luke",    "Luke",             2,   ["Lk"]),
    BibleBook.John:     ("John",    "John",             3,   ["Jn", "Jhn"]),
    BibleBook.Acts:     ("Acts",    "Acts",             2,   []),
    BibleBook.Rom:      ("Rom",     "Romans",           2,   ["Rm"]),
    BibleBook._1Cor:    ("1Cor",    "1 Corinthians",    2,   []),
    BibleBook._2Cor:    ("2Cor",    "2 Corinthians",    2,   []),
    BibleBook.Gal:      ("Gal",     "Galatians",        2,   []),
    BibleBook.Eph:      ("Eph",     "Ephesians",        2,   []),
    BibleBook.Phil:     ("Phil",    "Philippians",      5,   ["Pp", "Php"]),
    BibleBook.Col:      ("Col",     "Colossians",       2,   []),
    BibleBook._1Thess:  ("1Thess",  "1 Thessalonians",  2,   ["1 Ths"]),
    BibleBook._2Thess:  ("2Thess",  "2 Thessalonians",  2,   ["2 Ths"]),
    BibleBook._1Tim:    ("1Tim",    "1 Timothy",        2,   []),
    BibleBook._2Tim:    ("2Tim",    "2 Timothy",        2,   []),
    BibleBook.Titus:    ("Titus",   "Titus",            2,   []),
    BibleBook.Phlm:     ("Phlm",    "Philemon",         5,   ["Pm", "Phm"]),
    BibleBook.Heb:      ("Heb",     "Hebrews",          2,   []),
    BibleBook.James:    ("James",   "James",            2,   ["Jm", "Jas"]),
    BibleBook._1Pet:    ("1Pet",    "1 Peter",          1,   ["1 Pt"]),
    BibleBook._2Pet:    ("2Pet",    "2 Peter",          1,   ["2 Pt"]),
    BibleBook._1Jn:     ("1Jn",     "1 John",           1,   ["1 Jn", "1 Jhn"]),
    BibleBook._2Jn:     ("2Jn",     "2 John",           1,   ["2 Jn", "2 Jhn"]),
    BibleBook._3Jn:     ("3Jn",     "3 John",           1,   ["3 Jn", "3 Jhn"]),
    BibleBook.Jude:     ("Jude",    "Jude",             4,   []),
    BibleBook.Rev:      ("Rev",     "Revelation",       2,   ["The Revelation", "The Revelation to John"])
}

order = [
    BibleBook.Gen,
    BibleBook.Exod,
    BibleBook.Lev,
    BibleBook.Num,
    BibleBook.Deut,
    BibleBook.Josh,
    BibleBook.Judg,
    BibleBook.Ruth,
    BibleBook._1Sam,
    BibleBook._2Sam,
    BibleBook._1Kgs,
    BibleBook._2Kgs,
    BibleBook._1Chr,
    BibleBook._2Chr,
    BibleBook.Ezra,
    BibleBook.Neh,
    BibleBook.Esth,
    BibleBook.Job,
    BibleBook.Psa,
    BibleBook.Prov,
    BibleBook.Eccl,
    BibleBook.Song,
    BibleBook.Isa,
    BibleBook.Jer,
    BibleBook.Lam,
    BibleBook.Ezek,
    BibleBook.Dan,
    BibleBook.Hos,
    BibleBook.Joel,
    BibleBook.Amos,
    BibleBook.Obad,
    BibleBook.Jonah,
    BibleBook.Mic,
    BibleBook.Nah,
    BibleBook.Hab,
    BibleBook.Zeph,
    BibleBook.Hag,
    BibleBook.Zech,
    BibleBook.Mal,
    BibleBook.Matt,
    BibleBook.Mark,
    BibleBook.Luke,
    BibleBook.John,
    BibleBook.Acts,
    BibleBook.Rom,
    BibleBook._1Cor,
    BibleBook._2Cor,
    BibleBook.Gal,
    BibleBook.Eph,
    BibleBook.Phil,
    BibleBook.Col,
    BibleBook._1Thess,
    BibleBook._2Thess,
    BibleBook._1Tim,
    BibleBook._2Tim,
    BibleBook.Titus,
    BibleBook.Phlm,
    BibleBook.Heb,
    BibleBook.James,
    BibleBook._1Pet,
    BibleBook._2Pet,
    BibleBook._1Jn,
    BibleBook._2Jn,
    BibleBook._3Jn,
    BibleBook.Jude,
    BibleBook.Rev
]

max_verses = {
    # Keys: Bible books
    # Values: List of max verse number for each chapter (ascending by chapter). Len of list is number of chapters.
    BibleBook.Gen:      [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26],
    BibleBook.Exod:     [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38],
    BibleBook.Lev:      [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34],
    BibleBook.Num:      [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13],
    BibleBook.Deut:     [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12],
    BibleBook.Josh:     [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33],
    BibleBook.Judg:     [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25],
    BibleBook.Ruth:     [22, 23, 18, 22],
    BibleBook._1Sam:    [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13],
    BibleBook._2Sam:    [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25],
    BibleBook._1Kgs:    [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53],
    BibleBook._2Kgs:    [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30],
    BibleBook._1Chr:    [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30],
    BibleBook._2Chr:    [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23],
    BibleBook.Ezra:     [11, 70, 13, 24, 17, 22, 28, 36, 15, 44],
    BibleBook.Neh:      [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31],
    BibleBook.Esth:     [22, 23, 15, 17, 14, 14, 10, 17, 32, 3],
    BibleBook.Job:      [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17],
    BibleBook.Psa:      [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6],
    BibleBook.Prov:     [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31],
    BibleBook.Eccl:     [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14],
    BibleBook.Song:     [17, 17, 11, 16, 16, 13, 13, 14],
    BibleBook.Isa:      [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24],
    BibleBook.Jer:      [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34],
    BibleBook.Lam:      [22, 22, 66, 22, 22],
    BibleBook.Ezek:     [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35],
    BibleBook.Dan:      [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13],
    BibleBook.Hos:      [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9],
    BibleBook.Joel:     [20, 32, 21],
    BibleBook.Amos:     [15, 16, 15, 13, 27, 14, 17, 14, 15],
    BibleBook.Obad:     [21],
    BibleBook.Jonah:    [17, 10, 10, 11],
    BibleBook.Mic:      [16, 13, 12, 13, 15, 16, 20],
    BibleBook.Nah:      [15, 13, 19],
    BibleBook.Hab:      [17, 20, 19],
    BibleBook.Zeph:     [18, 15, 20],
    BibleBook.Hag:      [15, 23],
    BibleBook.Zech:     [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21],
    BibleBook.Mal:      [14, 17, 18, 6],
    BibleBook.Matt:     [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20],
    BibleBook.Mark:     [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20],
    BibleBook.Luke:     [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53],
    BibleBook.John:     [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25],
    BibleBook.Acts:     [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31],
    BibleBook.Rom:      [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27],
    BibleBook._1Cor:    [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24],
    BibleBook._2Cor:    [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14],
    BibleBook.Gal:      [24, 21, 29, 31, 26, 18],
    BibleBook.Eph:      [23, 22, 21, 32, 33, 24],
    BibleBook.Phil:     [30, 30, 21, 23],
    BibleBook.Col:      [29, 23, 25, 18],
    BibleBook._1Thess:  [10, 20, 13, 18, 28],
    BibleBook._2Thess:  [12, 17, 18],
    BibleBook._1Tim:    [20, 15, 16, 16, 25, 21],
    BibleBook._2Tim:    [18, 26, 17, 22],
    BibleBook.Titus:    [16, 15, 15],
    BibleBook.Phlm:     [25],
    BibleBook.Heb:      [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25],
    BibleBook.James:    [27, 26, 18, 17, 20],
    BibleBook._1Pet:    [25, 25, 22, 19, 14],
    BibleBook._2Pet:    [21, 22, 18],
    BibleBook._1Jn:     [10, 29, 24, 21, 21],
    BibleBook._2Jn:     [13],
    BibleBook._3Jn:     [14],
    BibleBook.Jude:     [25],
    BibleBook.Rev:      [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
}

verse_0s = {
    # Keys: Bible books
    # Values: Set of chapter numbers (1-indexed) that can begin with a verse 0.
     BibleBook.Psa:     set([3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                        28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                        54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 78,
                        79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 98, 100, 101, 102, 103, 108, 109, 110, 120,
                        121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 138, 139, 140, 141, 142,
                        143, 144, 145])
}


def _add_abbrevs_and_titles():
    for book, data in name_data.items():
        book.abbrev = data[0]
        book.title = data[1]

def _add_regexes():
    '''Add a 'regex' attribute to each BibleBook for a regex matching acceptable names.

    For each book, several regex patterns are joined together.
    The main pattern is derived from the book's full title, and requires the min number of unique characters.
    Any characters beyond the minimum are optional, but must be correct.
    Extra patterns are derived from the list of any extra recognised abbreviations.
    '''
    for book, data in name_data.items():
        # For clarity, the comments show what happens for the example of "1 John"
        full_title = data[1]    # e.g. "1 John"
        min_chars = data[2]     # e.g. 1
        extra_abbrevs = data[3] #
        full_title_pattern = ""

        # Peel off any numeric prefix, and match variations on the prefix.
        # e.g. full_title_pattern = r"(1|I)\s*"
        #      full_title = "John"
        if full_title[0:2] == "1 " or full_title[0:2] == "2 " or full_title[0:2] == "3 ":
            full_title_pattern = full_title[0:2]
            full_title_pattern = full_title_pattern.replace("1 ", r"(1|I)\s*") 
            full_title_pattern = full_title_pattern.replace("2 ", r"(2|II)\s*")
            full_title_pattern = full_title_pattern.replace("3 ", r"(3|III)\s*")
            full_title = full_title[2:]
        
        # Add the minimum number of unique characters
        # e.g. full_title_pattern = r"(1|I)\s*J"
        full_title_pattern += full_title[0:min_chars]

        # Add the rest of full title characters as optional matches.
        # e.g. full_title_pattern = r"(1|I)\s*J(o(h(n)?)?)?"
        for char in full_title[min_chars:]:
            full_title_pattern += "(" + char
        full_title_pattern += ")?" * (len(full_title)-min_chars)

        # Allow for extra whitespace.
        full_title_pattern = full_title_pattern.replace(" ",r"\s+")

        # Collate the extra acceptable abbreviations, and combine everything into a final,
        # single regex for the book
        total_pattern = full_title_pattern
        for abbrev in extra_abbrevs:
            abbrev = abbrev.replace(" ",r"\s+") # Allow for extra whitespace
            total_pattern += "|" + abbrev
        book.regex = re.compile(total_pattern, re.IGNORECASE)

def _add_order():
    for i in range(len(order)):
        order[i].order = i

def _add_max_verses():
    for book, max_verse_list in max_verses.items():
        book._max_verses = max_verse_list

def _add_verse_0s():
    for book in BibleBook:
        if book in verse_0s:
            book._verse_0s = verse_0s[book]
        else:
            book._verse_0s = None


_add_abbrevs_and_titles()
_add_regexes()
_add_order()
_add_max_verses()
_add_verse_0s()
