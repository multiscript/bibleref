import copy
from dataclasses import dataclass
from enum import Enum, Flag, auto
import re

from . import parser
from . import util


allow_multibook = False     # Set to True to default to allowing a BibleRange to span multiple books.
                            # The default value can be overridden in individual methods.

allow_verse_0 = False       # Set to True to default to allowing verse 0 to be the first verse for some
                            # chapters (currently just Psalms with superscriptions).
                            # This default value can be overridden in individual methods.


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

    def first_verse(self, chap: int = None, allow_verse_0: bool = None) -> 'BibleVerse':
        '''Returns a BibleVerse for the first verse of the specified chapter of the BibleBook.
        If chap is None, it uses the first chapter of the book.
        '''
        if chap is None:
            chap = self.min_chap()
        return BibleVerse(self, chap, self.min_verse(chap, allow_verse_0))        

    def last_verse(self, chap: int = None) -> 'BibleVerse':
        '''Returns a BibleVerse for the last verse of the specified chapter of the BibleBook.
        If chap is None, it uses the last chapter of the book.
        '''
        if chap is None:
            chap = self.max_chap()
        return BibleVerse(self, chap, self.max_verse(chap))        

    def next(self) -> 'BibleBook':
        '''Returns the next BibleBook in the book ordering, or None if this is the final book.
        '''
        if self.order == len(data.order)-1:
            return None
        else:
            return data.order[self.order+1]

    def prev(self) -> 'BibleBook':
        '''Returns the previous BibleBook in the book ordering, or None if this is the first book.
        '''
        if self.order == 0:
            return None
        else:
            return data.order[self.order-1]

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


# We delay the import of data until this point so that BibleBook and its related classes
# are already defined and can be used by the data submodule
from . import data


class BibleVersePart(Flag):
    NONE    = 0
    BOOK    = auto()
    CHAP    = auto()
    VERSE   = auto()
    FULL_REF    = BOOK | CHAP | VERSE
    BOOK_CHAP   = BOOK | CHAP
    BOOK_VERSE  = BOOK | VERSE
    CHAP_VERSE  = CHAP | VERSE


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

    def string(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
               verse_parts: BibleVersePart = BibleVersePart.FULL_REF):
        '''Returns a string representation of this BibleVerse.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If alt_sep is True, chapter and verse numbers are separated by the alternate
          separator (defaults to '.') instead of the standard separator (defaults to ':').
        If nospace is True, no spaces are included in the string.
        verse_parts is a combination of BibleVersePart flags, controlling what combination of book,
          chap & verse are displayed.
        '''
        if self.book.chap_count() == 1:
            verse_parts &= ~BibleVersePart.CHAP # Don't display chap
        
        if BibleVersePart.BOOK in verse_parts:
            book_name = self.book.abbrev if abbrev else self.book.title
        else:
            book_name = ""
        
        chap_str = str(self.chap) if BibleVersePart.CHAP in verse_parts else ""
        verse_str = str(self.verse) if BibleVersePart.VERSE in verse_parts else ""
        
        if BibleVersePart.CHAP_VERSE in verse_parts:
            verse_sep = data.VERSE_SEP_ALT if alt_sep else data.VERSE_SEP_STANDARD
        else:
            verse_sep = ""

        result = f"{book_name} {chap_str}{verse_sep}{verse_str}"

        if nospace:
            return result.replace(" ", "")
        else:
            return result.strip()

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

    def min_chap_verse(self, allow_verse_0: bool = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the chapter of this BibleVerse.
        If allow_verse_0 is not None it overrides the module attribute of the same name. If True,
        chapters with superscriptions start with verse 0.
        '''
        return self.book.min_verse(self.chap, allow_verse_0)

    def max_chap_verse(self) -> int:
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
                allow_multibook: bool = None, allow_verse_0: bool = None):
        if allow_multibook is None:
            allow_multibook = globals()['allow_multibook']
 
        if start_book is None or start_book not in BibleBook:
            raise InvalidReferenceError("Start book not valid")
        if start_chap is None and start_verse is not None:
            raise InvalidReferenceError("Start verse is missing a start chapter")

        no_end = (end_book is None and end_chap is None and end_verse is None)

        if start_chap is None: # Start is book only
            start = start_book.first_verse(None, allow_verse_0)
            if no_end:
                end = start_book.last_verse()
        elif start_verse is None: # Start is book and chap only
            start = start_book.first_verse(start_chap, allow_verse_0)
            if no_end:
                end = start_book.last_verse(start_chap)
        else: # Start is book, chap and verse
            start = BibleVerse(start_book, start_chap, start_verse)
            if no_end: # Single verse reference, so end is same as start
                end = BibleVerse(start_book, start_chap, start_verse)
        
        if not no_end: # We have end-point info
            if end_book is None:
                end_book = start_book
            if end_chap is None and end_verse is None: # End is book only
                end = end_book.last_verse()
            elif end_verse is None: # End is book and chap only
                end = end_book.last_verse(end_chap)
            elif end_chap is None: # End is book and verse only
                if start_book != end_book:
                    raise InvalidReferenceError("End verse is missing an end chapter")
                else:
                    end = BibleVerse(end_book, start.chap, end_verse)
            else:
                end = BibleVerse(end_book, end_chap, end_verse)

        if not allow_multibook and start.book != end.book:
            raise MultibookRangeNotAllowedError()

        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

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

    def is_whole_book(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange exactly spans a whole book, else False.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(None, allow_verse_0)) and \
                (self.end == self.end.book.last_verse())

    def spans_start_book(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange spans the whole start book.'''
        return  (self.start == self.start.book.first_verse(None, allow_verse_0)) and \
                (self.end >= self.start.book.last_verse())

    def spans_end_book(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange spans the whole start book.'''
        return  (self.end == self.end.book.last_verse()) and \
                (self.start <= self.end.book.first_verse())

    def is_whole_chap(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange exactly spans a whole chapter, else False.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(self.start.chap, allow_verse_0)) and \
                (self.end == self.end.book.last_verse(self.start.chap))

    def spans_start_chap(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange spans the whole start chap.'''
        return  (self.start == self.start.book.first_verse(self.start.chap, allow_verse_0)) and \
                (self.end >= self.start.book.last_verse(self.start.chap))

    def spans_end_chap(self, allow_verse_0: bool = None):
        '''Returns True if the BibleRange spans the whole end chap.'''
        return  (self.end == self.end.book.last_verse(self.end.chap)) and \
                (self.start <= self.end.book.first_verse(self.end.chap, allow_verse_0))

    def is_single_verse(self):
        '''Returns True if the BibleRange represents a single verse, else False.'''
        return  (self.start == self.end)

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

    def string(self, abbrev=False, alt_sep=False, nospace=False):
        '''Returns a string representation of this BibleRange.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If alt_sep is True, chapter and verse numbers are separated by the alternate
          separator (defaults to '.') instead of the standard separator (defaults to ':').
        If nospace is True, no spaces are included in the string.
        '''
        if self.spans_start_book():
            start_parts = BibleVersePart.BOOK
            at_verse_level = False
        elif self.spans_start_chap():
            start_parts = BibleVersePart.BOOK_CHAP
            at_verse_level = False
        else:
            start_parts = BibleVersePart.FULL_REF
            at_verse_level = True
        start_str = self.start.string(abbrev, alt_sep, nospace, start_parts) 
        
        if self.is_whole_book() or self.is_whole_chap() or self.is_single_verse(): # Single reference
            end_str = ""
            range_sep = ""
        else: 
            range_sep = data.RANGE_SEP
            if self.end.book != self.start.book:
                at_verse_level = False
            
            if self.spans_end_book():
                end_parts = BibleVersePart.BOOK
            elif not at_verse_level and self.spans_end_chap():
                end_parts = BibleVersePart.BOOK_CHAP
            else:
                end_parts = BibleVersePart.FULL_REF
            if self.start.book == self.end.book:
                end_parts &= ~BibleVersePart.BOOK # Omit book
            end_str = self.end.string(abbrev, alt_sep, nospace, end_parts) 
        
        result = f"{start_str}{range_sep}{end_str}"
        if nospace:
            return result.replace(" ", "")
        else:
            return result.strip()


class BibleRangeList(util.LinkedList):
    @classmethod
    def new_from_text(cls, text):
        return parser._parse(text)

    def _check_type(self, value):
        if not isinstance(value, BibleRange):
            raise TypeError(f"Item is not a BibleRange: {value}")

    def __str__(self):
        return self.string()

    def string(self, abbrev=False, alt_sep=False, nospace=False, preserve_groups=True):
        '''Returns a string representation of this BibleRangeList.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If alt_sep is True, chapter and verse numbers are separated by the alternate
          separator (defaults to '.') instead of the standard separator (defaults to ':').
        If nospace is True, no spaces are included in the string.
         If preserve_groups is True, the major group separator is only used between groups, and
           not within groups. Parsing the resulting string should yield an equivalent BibleRangeList.
        '''
        cur_book = None
        cur_chap = None
        at_verse_level = False
        first_range = True
        list_sep = ""
        result_str = ""
        force_dual_ref = False # True if we require a single reference to display as a dual_reference_range

        for group in self.groups:
            for br in group:
                bible_range: BibleRange = br # Typecast                
                if bible_range.spans_start_book(): # Range start includes an entire book
                    # Even if already in same book, whole book references repeat the whole book name.
                    start_parts = BibleVersePart.BOOK
                    cur_chap = None
                    at_verse_level = False
                elif bible_range.spans_start_chap(): # Range start includes an entire chap
                    if cur_book == bible_range.start.book: # Continuing same book
                        if at_verse_level: # We're in a list of verses
                            if not preserve_groups: # Use major list sep to return to chapters
                                list_sep = data.MAJOR_LIST_SEP
                                start_parts = BibleVersePart.CHAP
                                at_verse_level = False
                            else: # Preserving groups
                                if list_sep == data.MAJOR_LIST_SEP:
                                    # We're straight after a major list ref, so must return to chaps
                                    start_parts = BibleVersePart.CHAP
                                    at_verse_level = False
                                else: # We're after a minor list ref, so we can't return to chaps,
                                      # so we force display the whole range
                                    start_parts = BibleVersePart.CHAP_VERSE
                                    at_verse_level = True
                                    force_dual_ref = True
                        else: # We're in a list of chapters
                            if not preserve_groups: # Use major list sep between chapters
                                list_sep = data.MAJOR_LIST_SEP
                            start_parts = BibleVersePart.CHAP
                            at_verse_level = False
                    else: # Start of a different book
                        if not preserve_groups: # Use major list sep between books
                            list_sep = data.MAJOR_LIST_SEP
                        start_parts = BibleVersePart.BOOK_CHAP
                        at_verse_level = False
                    cur_chap = bible_range.start.chap
                else: # Range start is just a particular verse
                    if cur_book == bible_range.start.book: # Continuing same book
                        if at_verse_level and cur_chap == bible_range.start.chap: # Continuing same chap
                            start_parts = BibleVersePart.VERSE
                        else: # At chap level or verse level in a different chap
                            if not preserve_groups: # Use major list sep between chapters
                                list_sep = data.MAJOR_LIST_SEP
                            start_parts = BibleVersePart.CHAP_VERSE
                    else: # Different book
                        if not preserve_groups: # Use major list sep between books
                            list_sep = data.MAJOR_LIST_SEP
                        start_parts = BibleVersePart.FULL_REF
                    cur_chap = bible_range.start.chap
                    at_verse_level = True # All single verses move us to verse level
                cur_book = bible_range.start.book
                start_str = bible_range.start.string(abbrev, alt_sep, nospace, start_parts) 

                if not force_dual_ref and (bible_range.is_whole_book() or bible_range.is_whole_chap() or \
                                           bible_range.is_single_verse()):
                    # Single reference
                    end_str = ""
                    range_sep = ""
                else:
                    range_sep = data.RANGE_SEP
                    if bible_range.end.book != bible_range.start.book:
                        at_verse_level = False

                    if bible_range.spans_end_book(): # Range end includes an entire book
                        end_parts = BibleVersePart.BOOK
                        cur_chap = None
                        at_verse_level = False
                    elif not at_verse_level and bible_range.spans_end_chap(): # Range end includes an entire chap
                        if cur_book == bible_range.end.book: # Continuing same book
                            end_parts = BibleVersePart.CHAP
                        else: # Different book
                            end_parts = BibleVersePart.BOOK_CHAP
                        cur_chap = bible_range.end.chap
                        at_verse_level = False
                    else: # Range end is a whole chap after a particular verse, or a particular verse
                        if cur_book == bible_range.end.book: # Continuing same book
                            if cur_chap == bible_range.end.chap: # Continuing same chap
                                end_parts = BibleVersePart.VERSE
                            else: # Different chap
                                end_parts = BibleVersePart.CHAP_VERSE
                        else: # Different book
                            end_parts = BibleVersePart.FULL_REF
                        cur_chap = bible_range.end.chap
                        at_verse_level = True
                    cur_book = bible_range.end.book
                    end_str = bible_range.end.string(abbrev, alt_sep, nospace, end_parts) 
                
                if first_range:
                    list_sep = ""
                    first_range = False
                range_str = f"{list_sep} {start_str}{range_sep}{end_str}"

                if nospace:
                    result_str += range_str.replace(" ", "")
                else:
                    result_str += range_str.strip()

                list_sep = data.MINOR_LIST_SEP # Minor list separator between groups
            list_sep = data.MAJOR_LIST_SEP # Major list separator between groups
        return result_str

class MultibookRangeNotAllowedError(Exception):
    pass


class InvalidReferenceError(Exception):
    pass


def _add_abbrevs_and_titles():
    for book, name_data in data.name_data.items():
        book.abbrev = name_data[0]
        book.title = name_data[1]

def _add_regexes():
    '''Add a 'regex' attribute to each BibleBook for a regex matching acceptable names.

    For each book, several regex patterns are joined together.
    The main pattern is derived from the book's full title, and requires the min number of unique characters.
    Any characters beyond the minimum are optional, but must be correct.
    Extra patterns are derived from the list of any extra recognised abbreviations.
    '''
    for book, name_data in data.name_data.items():
        # For clarity, the comments show what happens for the example of "1 John"
        full_title = name_data[1]    # e.g. "1 John"
        min_chars = name_data[2]     # e.g. 1
        extra_abbrevs = name_data[3] #
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
    for i in range(len(data.order)):
        data.order[i].order = i

def _add_max_verses():
    for book, max_verse_list in data.max_verses.items():
        book._max_verses = max_verse_list

def _add_verse_0s():
    for book in BibleBook:
        if book in data.verse_0s:
            book._verse_0s = data.verse_0s[book]
        else:
            book._verse_0s = None


_add_abbrevs_and_titles()
_add_regexes()
_add_order()
_add_max_verses()
_add_verse_0s()
