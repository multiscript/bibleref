'''A module for storing and manipulating references to Bible books, verses and ranges.

This module defines the following primary classes:
    BibleBook:      An Enum of books in the Bible, with extra methods.
    BibleVerse:     A reference to a single Bible verse (e.g. Matt 2:3)
    BibleRange:     A reference to a continuous range of Bible verses (e.g. Matt 2:3-4:5)
    BibleRangeList: A list of BibleRanges, allowing for grouping and set-style operations.

    (There is no BibleChapter class, as chapters are usually best handled as a BibleRange.)

The module attribute 'flags' is a BibleFlag enum whose elements control the following
module behaviours:
    ALLOW_MULTIBOOK: Defaults to unset. When set, BibleRanges can be constructed that span
                        multiple books. Existing multibook ranges behave correctly even when
                        ALLOW_MULTIBOOK is unset. 
    ALLOW_VERSE_0:   Defaults to unset. When set, the first verse number of some chapters
                        is 0, not 1. (This is currently just the Psalms that have
                        superscriptions.) When you need to mix references that do or don't
                        allow for verse 0, it may be easier to choose one value for all
                        your code, and then use the verse_0_to_1() and verse_1_to_0()
                        methods on BibleVerses, BibleRanges and BibleRangeLists as
                        necessary.

Many methods take a 'flags' argument that takes overrides the module-level attribute during
the execution of that method.

The Bible book, chapter and verse data is specified in the sibling 'data' module.
'''
# TODO Rename chap to chap_num and verse to verse_num
import copy
from dataclasses import dataclass
from enum import Enum, Flag, auto
import re


class BibleFlag(Flag):
    '''A Flag used for controlling various behaviours throughout the module.'''
    NONE = 0
    ALLOW_MULTIBOOK = auto()
    ALLOW_VERSE_0 = auto()
    ALL = ALLOW_MULTIBOOK | ALLOW_VERSE_0

flags = BibleFlag.NONE


class BibleBook(Enum):
    '''An enum of books in the Bible.

    Note that Python identifiers can't start with a number, so books like
    1 Samuel are specified here as _1Sam.

    BibleBooks have the following extra attributes (added during module import):
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
    def from_str(cls, string: str, raise_error: bool = False) -> 'BibleBook':
        '''Return the BibleBook matching the given string name.
        
        If no book matches and raise_error is False (the default), None is returned.
        If no book matches and raise_error is True, an InvalidReferenceError is raised.
        '''
        string = string.strip()
        match = False
        for book in BibleBook:
            if book.regex.fullmatch(string) is not None:
                match = True
                break
        if match:
            return book
        else:
            if raise_error:
                raise InvalidReferenceError(f"No book found for string '{string}'")
            else:
                return None

    def min_chap(self) -> int:
        '''Return lowest chapter number (indexed from 1) for this BibleBook.
        '''
        return 1    # Currently always 1. Perhaps in future some books may have a chapter-0 prologue included?

    def max_chap(self) -> int:
        '''Return highest chapter number (indexed from 1) for this BibleBook.
        '''
        return len(self._max_verses)
    
    def chap_count(self):
        '''Returns the number of chapters in this BibleBook.
        '''
        return (self.max_chap() - self.min_chap() + 1)

    def min_verse(self, chap: int, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the specified chapter
        of this BibleBook.
        '''
        flags = flags or globals()['flags']
        if chap < self.min_chap() or chap > self.max_chap():
            raise InvalidReferenceError(f"No chapter {chap} in {self.title}")
        return 0 if (BibleFlag.ALLOW_VERSE_0 in flags and chap in self._verse_0s) else 1

    def max_verse(self, chap: int) -> int:
        '''Return the highest verse number (usually indexed from 1) for the specified chapter
        number of this BibleBook.
        '''
        if chap < self.min_chap() or chap > self.max_chap():
            raise InvalidReferenceError(f"No chapter {chap} in {self.title}")
        return self._max_verses[chap-1]

    def first_verse(self, chap: int = None, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a BibleVerse for the first verse of the specified chapter of the BibleBook.
        If chap is None, it uses the first chapter of the book.
        '''
        if chap is None:
            chap = self.min_chap()
        return BibleVerse(self, chap, self.min_verse(chap, flags))        

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


# We delay these imports until this point so that BibleBook and its related classes
# are already defined and can be used by other sibling modules
from . import parser
from . import util
from . import data


class BibleVersePart(Flag):
    '''Flag for referring to the 3 primary attributes of a BibleVerse.
    
    Mainly used for converting BibleVerses, BibleRanges and BibleRangeLists to strings.
    '''
    NONE    = 0
    BOOK    = auto()
    CHAP    = auto()
    VERSE   = auto()
    FULL_REF    = BOOK | CHAP | VERSE
    BOOK_CHAP   = BOOK | CHAP
    BOOK_VERSE  = BOOK | VERSE
    CHAP_VERSE  = CHAP | VERSE


@dataclass(init=False, repr=False, eq=True, order=True, frozen=True)
class BibleVerse:
    '''A reference to a single Bible verse (e.g. Matt 2:3).

    Contains 3 primary attributes:
        book:   The BibleBook of the book of the reference.
        chap:   The chapter number (indexed from 1) of the reference.
        verse:  The verse number (usually indexed from 1) of the reference.

    BibleVerses are immutable.
    '''
    book:   BibleBook
    chap:   int
    verse:  int

    def __init__(self, *args, flags: BibleFlag = None):
        '''BibleVerses can be constructed in the following ways:

            1. From a single string: BibleVerse("Mark 2:3")
            2. From a string book name, chapter and verse numbers: BibleVerse("Mark", 2, 3)
            3. From a BibleBook, chapter and verse numbers: BibleVerse(BibleBook.Mark, 2, 3)
            4. As a copy of another BibleVerse: BibleVerse(existing_bible_verse)

        If the supplied arguments are not a valid verse, raises an InvalidReferenceError.
        '''
        if len(args) == 1:
            if isinstance(args[0], str):
                range_list = BibleRangeList(args[0], flags=flags)
                if len(range_list) != 1 or not range_list[0].is_single_verse():
                    raise InvalidReferenceError(f"String is not a single verse: {args[0]}")
                object.__setattr__(self, "book", range_list[0].start.book)
                object.__setattr__(self, "chap", range_list[0].start.chap)
                object.__setattr__(self, "verse", range_list[0].start.verse)
            elif isinstance(args[0], BibleVerse):
                # We have to use object.__setattr__ because the class is frozen
                object.__setattr__(self, "book", args[0].book)
                object.__setattr__(self, "chap", args[0].chap)
                object.__setattr__(self, "verse", args[0].verse)
            else:
                raise ValueError("Single argument to BibleVerse can only be a string or another BibleVerse")
        elif len(args) > 3:
            raise ValueError("Too many arguments supplied to BibleVerse")
        elif len(args) < 3:
            raise ValueError("Too few arguments supplied to BibleVerse")
        else:
            book = args[0]
            chap: int = args[1]
            verse: int = args[2]
            if isinstance(book, str):
                book = BibleBook.from_str(book, raise_error=True)
            elif not isinstance(book, BibleBook):
                raise ValueError(f"{book} must be a string or an instance of BibleBook")
            if not isinstance(chap, int):
                raise ValueError(f"{chap} is not an integer chapter number")
            if not isinstance(verse, int):
                raise ValueError(f"{chap} is not an integer verse number")
            if chap < book.min_chap() or chap > book.max_chap():
                raise InvalidReferenceError(f"No chapter {chap} in {book.title}")
            if verse < book.min_verse(chap, flags) or verse > book.max_verse(chap):
                raise InvalidReferenceError(f"No verse {verse} in {book.title} {chap}")
            object.__setattr__(self, "book", book) # We have to use object.__setattr__ because the class is frozen
            object.__setattr__(self, "chap", chap)
            object.__setattr__(self, "verse", verse)

    def min_chap_verse(self, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the chapter of this BibleVerse.
        '''
        return self.book.min_verse(self.chap, flags)

    def max_chap_verse(self) -> int:
        '''Return the highest verse number (usually indexed from 1) for the chapter of this BibleVerse.
        '''
        return self.book.max_verse(self.chap)

    def verse_0_to_1(self) -> 'BibleVerse':
        '''If this BibleVerse refers to a verse number 0, returns an identical BibleVerse
        except with a verse number of 1. Otherwise, returns the original BibleVerse.'''
        if self.verse == 0:
            return BibleVerse(self.book, self.chap, 1)
        else:
            return self
    
    def verse_1_to_0(self) -> 'BibleVerse':
        '''If this BibleVerse refers to a verse number 1, and a verse 0 is possible for the
        same chapter, returns an identical BibleVerse except with a verse number of 0.
        Otherwise, returns the original BibleVerse. The value of the module 'flags'
        attribute is ignored.'''
        if self.verse == 1 and self.min_chap_verse(flags=BibleFlag.ALLOW_VERSE_0) == 0:
            return BibleVerse(self.book, self.chap, 0, flags=BibleFlag.ALLOW_VERSE_0)
        else:
            return self

    def copy(self) -> 'BibleVerse':
        '''Returns a copy of this BibleVerse.
        '''
        return copy.copy(self)

    def add(self, num_verses: int, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a new BibleVerse that is num_verses after this BibleVerse.
        
        If BibleFlag.ALLOW_MULTIBOOK is set (either set by the 'flags' argument or,
        if None, by the module attribute), and the result would be beyond the current
        book, a verse in the subsequent book is returned. Otherwise, if the verse
        does not exist, None is returned.
        '''
        flags = flags or globals()['flags']
        new_book = self.book
        new_chap = self.chap
        new_verse = self.verse + num_verses
        max_verse = new_book.max_verse(new_chap)
        while new_verse > max_verse:
            new_chap += 1
            if new_chap > new_book.max_chap():
                if BibleFlag.ALLOW_MULTIBOOK not in flags:
                    return None
                else:
                    new_book = new_book.next()
                    if new_book is None:
                        return None
                    new_chap = new_book.min_chap()
            
            new_verse = new_verse - max_verse - 1 + new_book.min_verse(new_chap, flags)
            max_verse = new_book.max_verse(new_chap)

        return BibleVerse(new_book, new_chap, new_verse, flags=flags)

    def subtract(self, num_verses: int, flags: BibleFlag = None) -> 'BibleVerse':
        '''Return a new BibleVerse that is num_verses before this BibleVerse.
        
        If BibleFlag.ALLOW_MULTIBOOK is set (either set by the 'flags' argument or,
        if None, the module attribute), and the result would be before the current
        book, a verse in the prior book is returned. Otherwise, if the verse does
        not exist, None is returned.
        '''
        flags = flags or globals()['flags']        
        new_book = self.book
        new_chap = self.chap
        new_verse = self.verse - num_verses
        min_verse = new_book.min_verse(new_chap, flags)
        while new_verse < min_verse:
            new_chap -= 1
            if new_chap < new_book.min_chap():
                if BibleFlag.ALLOW_MULTIBOOK not in flags:
                    return None
                else:
                    new_book = new_book.prev()
                    if new_book is None:
                        return None
                    new_chap = new_book.max_chap()
             
            new_verse = new_verse + new_book.max_verse(new_chap)
            min_verse = new_book.min_verse(new_chap)

        return BibleVerse(new_book, new_chap, new_verse, flags=flags)

    def __repr__(self):
        return f"BibleVerse({self.string(abbrev=True)})"

    def __str__(self):
        return self.string()

    def string(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
               verse_parts: BibleVersePart = BibleVersePart.FULL_REF) -> str:
        '''Returns a configurable string representation of this BibleVerse.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If alt_sep is True, chapter and verse numbers are separated by the alternate
          separator ('.' by default) instead of the standard separator (':' by default).
        If nospace is True, no spaces are included in the string.
        verse_parts is a combination of BibleVersePart flags, controlling what combination of book,
          chapter & verse are displayed.
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


@dataclass(init=False, repr=False, eq=True, order=True, frozen=True)
class BibleRange:
    '''A reference to a continuous range of Bible verses (e.g. Matt 2:3-4:5).

    Contains 2 primary attributes:
        start:  The first BibleVerse in the range (inclusive).
        end:    The last BibleVerse in the range (inclusive).
    
    A BibleRange is immutable.
    '''
    start: BibleVerse
    end: BibleVerse

    def __init__(self, *args, start: BibleVerse = None, end: BibleVerse = None,
                 flags: BibleFlag = None):
        '''A BibleRange can be constructed in the following ways:

            1. From a single string: e.g. BibleRange("Mark 3:1-4:2")

            2. From positional arguments in the following order:
               Start book, start chap num, start verse num, end book, end chap num, end verse num
               Later arguments can be omitted or set to None, as in these examples:

                BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 4, 6, allow_multibook=True) # Matt 2:3-John 4:6
                BibleRange(BibleBook.Matt) # Entire book: Matt 1:1-28:20
                BibleRange(BibleBook.Matt, 2) # Entire chapter: Matt 2:1-23
                BibleRange(BibleBook.Matt, 2, 3) # Single verse: Matt 2:3
                BibleRange(BibleBook.Matt, None, None, BibleBook.John, allow_multibook=True) # Matt 1:1-John 21:25
                BibleRange(BibleBook.Matt, None, None, None, 4) # Matt 1:1-4:25
                BibleRange(BibleBook.Matt, None, None, None, None, 6) # Matt 1:1-1:6
                BibleRange(BibleBook.Matt, 2, 3, None, 4, 6) # Matt 2:3-4:6

            3. From a start and end BibleVerse, which must be specified using the keywords
               start and end.
               e.g. BibleRange(start=BibleVerse("Mark 3:1"), end=BibleVerse("Mark 4:2"))            
        '''
        flags = flags or globals()['flags']
        if len(args) == 0:
            if BibleFlag.ALLOW_MULTIBOOK not in flags and start.book != end.book:
                raise MultibookRangeNotAllowedError(f"Multi-book ranges not allowed " + 
                                                    f"({start.book.abbrev} and {end.book.abbrev} are different)")
            object.__setattr__(self, "start", start)
            object.__setattr__(self, "end", end)
            return
        elif len(args) > 6:
            raise ValueError("Too many arguments supplied to BibleRange")
        if len(args) == 1:
            if isinstance(args[0], str):
                range_list = BibleRangeList(args[0], flags=flags)
                if len(range_list) != 1:
                    raise InvalidReferenceError(f"String is not a single verse range: {args[0]}")
                object.__setattr__(self, "start", range_list[0].start)
                object.__setattr__(self, "end", range_list[0].end)
                return                
            elif isinstance(args[0], BibleRange):
                object.__setattr__(self, "start", args[0].start)
                object.__setattr__(self, "end", args[0].end)
                return
            elif not isinstance(args[0], BibleBook):
                raise ValueError("Single argument to BibleRange can only be a string, BibleBook or another BibleRange")

        start_book = args[0]
        start_chap = args[1] if len(args) > 1 else None
        start_verse = args[2] if len(args) > 2 else None
        end_book = args[3] if len(args) > 3 else None
        end_chap = args[4] if len(args) > 4 else None
        end_verse = args[5] if len(args) > 5 else None

        if start_book is None or not isinstance(start_book, BibleBook):
            raise InvalidReferenceError(f"{start_book} is not a valid BibleBook")
        if start_chap is None and start_verse is not None:
            raise InvalidReferenceError("Start verse is missing a start chapter")

        no_end = (end_book is None and end_chap is None and end_verse is None)

        if start_chap is None: # Start is book only
            start = start_book.first_verse(None, flags)
            if no_end:
                end = start_book.last_verse()
        elif start_verse is None: # Start is book and chap only
            start = start_book.first_verse(int(start_chap), flags)
            if no_end:
                end = start_book.last_verse(start_chap)
        else: # Start is book, chap and verse
            start = BibleVerse(start_book, int(start_chap), int(start_verse), flags=flags)
            if no_end: # Single verse reference, so end is same as start
                end = BibleVerse(start_book, int(start_chap), int(start_verse), flags=flags)
        
        if not no_end: # We have end-point info
            if end_book is None:
                end_book = start_book
            elif not isinstance(end_book, BibleBook):
                raise InvalidReferenceError(f"{end_book} is not a valid BibleBook")
            if end_chap is None and end_verse is None: # End is book only
                end = end_book.last_verse()
            elif end_verse is None: # End is book and chap only
                end = end_book.last_verse(int(end_chap))
            elif end_chap is None: # End is book and verse only
                if start_book != end_book:
                    raise InvalidReferenceError("End verse is missing an end chapter")
                else:
                    end = BibleVerse(end_book, int(start.chap), int(end_verse), flags=flags)
            else:
                end = BibleVerse(end_book, int(end_chap), int(end_verse), flags=flags)

        if BibleFlag.ALLOW_MULTIBOOK not in flags and start.book != end.book:
            raise MultibookRangeNotAllowedError(f"Multi-book ranges not allowed " + 
                                                f"({start.book.abbrev} and {end.book.abbrev} are different)")

        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    def verse_0_to_1(self) -> 'BibleRange':
        '''Returns a new BibleRange created by calling verse_0_to_1() on both its start and end
        BibleVerses. The value of the module 'flags' attribute is ignored.'''
        return BibleRange(start=self.start.verse_0_to_1(), end=self.end.verse_0_to_1(),
                          flags=BibleFlag.ALL)

    def verse_1_to_0(self) -> 'BibleRange':
        '''Returns a new BibleRange created by calling verse_1_to_0() on both its start and end
        BibleVerses. The value of the module 'flags' attribute is ignored.'''
        return BibleRange(start=self.start.verse_1_to_0(), end=self.end.verse_1_to_0(),
                          flags=BibleFlag.ALL)

    def is_whole_book(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans a whole book, else False.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(None, flags)) and \
                (self.end == self.end.book.last_verse())

    def spans_start_book(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange includes the whole book containing the
        starting verse, else False.'''
        return  (self.start == self.start.book.first_verse(None, flags)) and \
                (self.end >= self.start.book.last_verse())

    def spans_end_book(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange includes the whole book containing the
        ending verse, else False.'''
        return  (self.end == self.end.book.last_verse()) and \
                (self.start <= self.end.book.first_verse(None, flags))

    def is_whole_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans one whole chapter, else False.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(self.start.chap, flags)) and \
                (self.end == self.end.book.last_verse(self.start.chap))

    def spans_start_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans the whole chapter containing the
        starting verse, else False.'''
        return  (self.start == self.start.book.first_verse(self.start.chap, flags)) and \
                (self.end >= self.start.book.last_verse(self.start.chap))

    def spans_end_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans the whole chapter containing the
        ending verse, else False.'''
        return  (self.end == self.end.book.last_verse(self.end.chap)) and \
                (self.start <= self.end.book.first_verse(self.end.chap, flags))

    def is_single_verse(self) -> bool:
        '''Returns True if the BibleRange exactly spans a single verse, else False.'''
        return  (self.start == self.end)

    def contains(self, bible_verse: BibleVerse) -> bool:
        '''Returns True if this BibleRange contains bible_verse, otherwise False.
        '''
        return (bible_verse >= self.start and bible_verse <= self.end)

    # TODO: Check this is correct. Allow splitting by book as well. Add unit tests.
    def split(self, by_chap: bool = True, num_verses: bool = None, flags: BibleFlag = None):
        '''Split this range into a BibleRangeList of smaller consecutive ranges.
        
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
                    start_verse = book.min_verse(chap, flags)
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
                end = start.add(num_verses - 1, flags)
                while end is not None and end < bible_range.end:
                    verse_split.append(BibleRange(start.book, start.chap, start.verse, end.book, end.chap, end.verse))
                    start = end.add(1, flags)
                    end = start.add(num_verses-1, flags)
                verse_split.append(BibleRange(start.book, start.chap, start.verse,
                                   bible_range.end.book, bible_range.end.chap, bible_range.end.verse))
            return BibleRangeList(verse_split)
        else:
            return BibleRangeList(chap_split)

    # TODO: Add set-style methods.

    def __iter__(self):
        verse = self.start
        while verse <= self.end:
            yield verse
            verse = verse.add(1, BibleFlag.ALLOW_MULTIBOOK)

    def __repr__(self):
        return f"BibleRange({self.string()})"
    
    def __str__(self):
        return self.string()

    def string(self, abbrev=False, alt_sep=False, nospace=False, flags: BibleFlag = None):
        '''Returns a configurable string representation of this BibleRange.

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
        
        if self.is_whole_book(flags) or self.is_whole_chap(flags) or self.is_single_verse(): # Single reference
            end_str = ""
            range_sep = ""
        else: 
            range_sep = data.RANGE_SEP
            if self.end.book != self.start.book:
                at_verse_level = False
            
            if self.spans_end_book(flags):
                end_parts = BibleVersePart.BOOK
            elif not at_verse_level and self.spans_end_chap(flags):
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
    '''A list of BibleRanges, allowing for grouping and set-style operations.

    Currently implemented as a doubly-linked list, though this should be treated
    as an implementation detail, and not relied upon.
    '''
    def __init__(self, *args, flags: BibleFlag = None):
        flags = flags or globals()['flags']

        if len(args) == 1:
            if isinstance(args[0], str):
                range_groups_list = parser._parse(args[0], flags)
                super().__init__()
                for group in range_groups_list:
                    self.append_group(group)
            elif isinstance(args[0], BibleRangeList):
                super().__init__()
                for group in args[0].groups:
                    self.append_group(group)
            else:
                super().__init__(*args)
        else:
            super().__init__(args)

    def _check_type(self, value):
        if not isinstance(value, BibleRange):
            raise TypeError(f"Item is not a BibleRange: {value}")

    def verse_0_to_1(self):
        '''Modifies the BibleRangeList in-place by calling verse_0_to_1() on every
        BibleRange in the list and using the result to replace the original range.
        The value of the module 'flags' attribute is ignored. Returns None.'''
        for node in self._node_iter():
            node.value = node.value.verse_0_to_1()
        return None

    def verse_1_to_0(self):
        '''Modifies the BibleRangeList in-place by calling verse_1_to_0() on every
        BibleRange in the list and using the result to replace the original range.
        The value of the module 'flags' attribute is ignored. Returns None.'''
        for node in self._node_iter():
            node.value = node.value.verse_1_to_0()
        return None

    def __str__(self):
        return self.string()

    def string(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
               preserve_groups: bool = True, flags: BibleFlag = None):
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
                if bible_range.spans_start_book(flags): # Range start includes an entire book
                    # Even if already in same book, whole book references repeat the whole book name.
                    start_parts = BibleVersePart.BOOK
                    cur_chap = None
                    at_verse_level = False
                elif bible_range.spans_start_chap(flags): # Range start includes an entire chap
                    if cur_book == bible_range.start.book: # Continuing same book
                        if at_verse_level: # We're in a list of verses
                            if not preserve_groups: # Use major list sep to return to chapters
                                list_sep = data.MAJOR_LIST_SEP
                                start_parts = BibleVersePart.CHAP
                                at_verse_level = False
                            else: # Preserving groups
                                if list_sep == data.MAJOR_LIST_SEP:
                                    # We're straight after a major list ref, so must return to chap level
                                    start_parts = BibleVersePart.CHAP
                                    at_verse_level = False
                                else: # We're after a minor list ref, so we can't return to chap level,
                                      # so we force display the whole range
                                    start_parts = BibleVersePart.CHAP_VERSE
                                    at_verse_level = True
                                    force_dual_ref = True
                        else: # We're in a list of chapters
                            if not preserve_groups: # Use major list sep between chapters
                                list_sep = data.MAJOR_LIST_SEP
                                start_parts = BibleVersePart.CHAP
                                at_verse_level = False
                            else: # Preserving groups
                                if list_sep == data.MAJOR_LIST_SEP:
                                    # We're straight after a major list ref, so can return to chap level
                                    start_parts = BibleVersePart.CHAP
                                    at_verse_level = False
                                else: # We're after a minor list ref
                                    if bible_range.spans_end_chap(flags):
                                        # This range is a whole set of chapters, do just display chapters
                                        start_parts = BibleVersePart.CHAP
                                        at_verse_level = False
                                    else:
                                        # This range involves verses, in a list that's otherwise chapters,
                                        # so it's clearer to display using verses
                                        start_parts = BibleVersePart.CHAP_VERSE
                                        at_verse_level = True
                                        force_dual_ref = True
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

                if not force_dual_ref and (bible_range.is_whole_book(flags) or
                                           bible_range.is_whole_chap(flags) or \
                                           bible_range.is_single_verse()):
                    # Single reference
                    end_str = ""
                    range_sep = ""
                else:
                    range_sep = data.RANGE_SEP
                    if bible_range.end.book != bible_range.start.book:
                        at_verse_level = False

                    if bible_range.spans_end_book(flags): # Range end includes an entire book
                        end_parts = BibleVersePart.BOOK
                        cur_chap = None
                        at_verse_level = False
                    elif not at_verse_level and bible_range.spans_end_chap(flags): # Range end includes an entire chap
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
            at_verse_level=False
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
            full_title_pattern = full_title_pattern.replace("1 ", r"(1\s*|I\s+)") 
            full_title_pattern = full_title_pattern.replace("2 ", r"(2\s*|II\s+)")
            full_title_pattern = full_title_pattern.replace("3 ", r"(3\s*|III\s+)")
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
            abbrev = abbrev.replace(" ",r"\s*") # Allow for variable whitespace
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
            book._verse_0s = set()


_add_abbrevs_and_titles()
_add_regexes()
_add_order()
_add_max_verses()
_add_verse_0s()
