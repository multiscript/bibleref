'''A module for storing and manipulating references to Bible books, verses and ranges.

This module defines the following primary classes:
    BibleBook:      An Enum of books in the Bible, with extra methods.
    BibleVerse:     A reference to a single Bible verse (e.g. Matt 2:3)
    BibleRange:     A reference to a continuous range of Bible verses (e.g. Matt 2:3-4:5)
    BibleRangeList: A list of BibleRanges, allowing for grouping and set-style operations.

    (There is no BibleChapter class, as chapters are usually best handled as a BibleRange.)

The module attribute 'flags' is a BibleFlag enum whose elements control the following
module behaviours:
    MULTIBOOK: Defaults to unset. When set, BibleRanges can be constructed that span
                 multiple books. Existing multibook ranges behave correctly even when
                 MULTIBOOK is unset. 
    VERSE_0:   Defaults to unset. When set, BibleVerses can be constructed where the
                 first verse number of some chapters is 0, not 1. (This is currently
                 just the Psalms that have superscriptions.) When you need to mix
                 references that do or don't allow for verse 0, it may be easier to
                 choose one value for all your code, and then use the verse_0_to_1()
                 and verse_1_to_0() methods on BibleVerses, BibleRanges and
                 BibleRangeLists as necessary.

Many methods take a 'flags' argument that takes overrides the module-level attribute during
the execution of that method.

The Bible book, chapter and verse data is specified in the sibling 'data' module.
'''
# TODO: Create module method to make it easier to keep existing flags but set/unset particular flags
# TODO: Create context manager to temporarily set or unset particular flags
# TODO: Implement add and subtract operators for BibleVerses
# TODO: Implement count of chapters and verses in a BibleRange and BibleRangeList
# TODO: Implement set operators as standard operators
from dataclasses import dataclass
from enum import Enum, Flag, auto
import re
from typing import Union

#
# Set-style operations in this module are derived from the python-ranges module
# at https://github.com/Superbird11/ranges, under the MIT Licence
#

class BibleFlag(Flag):
    '''A Flag used for controlling various behaviours throughout the module.'''
    NONE = 0
    MULTIBOOK = auto()
    VERSE_0 = auto()
    ALL = MULTIBOOK | VERSE_0

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

    def min_chap_num(self) -> int:
        '''Return lowest chapter number (indexed from 1) for this BibleBook.
        '''
        return 1    # Currently always 1. Perhaps in future some books may have a chapter-0 prologue included?

    def max_chap_num(self) -> int:
        '''Return highest chapter number (indexed from 1) for this BibleBook.
        '''
        return len(self._max_verses)
    
    def chap_count(self):
        '''Returns the number of chapters in this BibleBook.
        '''
        return (self.max_chap_num() - self.min_chap_num() + 1)

    def min_verse_num(self, chap_num: int, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the specified chapter
        of this BibleBook.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        if chap_num < self.min_chap_num() or chap_num > self.max_chap_num():
            raise InvalidReferenceError(f"No chapter {chap_num} in {self.title}")
        return 0 if (BibleFlag.VERSE_0 in flags and chap_num in self._verse_0s) else 1

    def max_verse_num(self, chap_num: int) -> int:
        '''Return the highest verse number (usually indexed from 1) for the specified chapter
        number of this BibleBook.
        '''
        if chap_num < self.min_chap_num() or chap_num > self.max_chap_num():
            raise InvalidReferenceError(f"No chapter {chap_num} in {self.title}")
        return self._max_verses[chap_num-1]

    def first_verse(self, chap_num: int = None, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a BibleVerse for the first verse of the specified chapter of the BibleBook.
        If chap is None, it returns the first verse of the enitre book.
        '''
        if chap_num is None:
            chap_num = self.min_chap_num()
        return BibleVerse(self, chap_num, self.min_verse_num(chap_num, flags))        

    def last_verse(self, chap_num: int = None) -> 'BibleVerse':
        '''Returns a BibleVerse for the last verse of the specified chapter of the BibleBook.
        If chap is None, it returns the last verse of the entire book.
        '''
        if chap_num is None:
            chap_num = self.max_chap_num()
        return BibleVerse(self, chap_num, self.max_verse_num(chap_num))        

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
    book:       BibleBook
    chap_num:   int
    verse_num:  int

    def __init__(self, *args, flags: BibleFlag = None):
        '''BibleVerses can be constructed in any of the following ways:

            1. From a single string: BibleVerse("Mark 2:3")

            2. From a Bible book, chapter and verse numbers. The Bible book can
                 be a string name (), or a BibleBook enum:
                 BibleVerse("Mark", 2, 3), or BibleVerse(BibleBook.Mark, 2, 3)
            
            3. As a copy of another BibleVerse: BibleVerse(existing_bible_verse)

        If the supplied arguments are not a valid verse, raises an InvalidReferenceError.
        '''
        if len(args) == 1:
            if isinstance(args[0], str):
                range_list = BibleRangeList(args[0], flags=flags)
                if len(range_list) != 1 or not range_list[0].is_single_verse():
                    raise InvalidReferenceError(f"String is not a single verse: {args[0]}")
                object.__setattr__(self, "book", range_list[0].start.book)
                object.__setattr__(self, "chap_num", range_list[0].start.chap_num)
                object.__setattr__(self, "verse_num", range_list[0].start.verse_num)
            elif isinstance(args[0], BibleVerse):
                # We have to use object.__setattr__ because the class is frozen
                object.__setattr__(self, "book", args[0].book)
                object.__setattr__(self, "chap_num", args[0].chap_num)
                object.__setattr__(self, "verse_num", args[0].verse_num)
            else:
                raise ValueError("Single argument to BibleVerse can only be a string or another BibleVerse")
        elif len(args) > 3:
            raise ValueError("Too many arguments supplied to BibleVerse")
        elif len(args) < 3:
            raise ValueError("Too few arguments supplied to BibleVerse")
        else:
            book = args[0]
            chap_num: int = args[1]
            verse_num: int = args[2]
            if isinstance(book, str):
                book = BibleBook.from_str(book, raise_error=True)
            elif not isinstance(book, BibleBook):
                raise ValueError(f"{book} must be a string or an instance of BibleBook")
            if not isinstance(chap_num, int):
                raise ValueError(f"{chap_num} is not an integer chapter number")
            if not isinstance(verse_num, int):
                raise ValueError(f"{chap_num} is not an integer verse number")
            if chap_num < book.min_chap_num() or chap_num > book.max_chap_num():
                raise InvalidReferenceError(f"No chapter {chap_num} in {book.title}")
            if verse_num < book.min_verse_num(chap_num, flags) or verse_num > book.max_verse_num(chap_num):
                raise InvalidReferenceError(f"No verse {verse_num} in {book.title} {chap_num}")
            object.__setattr__(self, "book", book) # We have to use object.__setattr__ because the class is frozen
            object.__setattr__(self, "chap_num", chap_num)
            object.__setattr__(self, "verse_num", verse_num)

    def min_chap_num(self) -> int:
        '''Return lowest chapter number (indexed from 1) of the BibleBook containing this verse.
        '''
        return self.book.min_chap_num()

    def max_chap_num(self) -> int:
        '''Return highest chapter number (indexed from 1) of the BibleBook containing this verse.
        '''
        return self.book.max_chap_num()
    
    def chap_count(self):
        '''Returns the number of chapters in the BibleBook containing this verse.
        '''
        return self.book.chap_count()

    def min_verse_num(self, chap_num: int = None, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (usually indexed from 1) for the specified chapter
        of the BibleBook containing this verse. If no chapter is specified, it returns the
        lowest verse number of the chapter containing this verse.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.min_verse_num(chap_num, flags=flags)

    def max_verse_num(self, chap_num: int) -> int:
        '''Return the highest verse number (usually indexed from 1) for the specified chapter
        of the BibleBook containing this verse. If no chapter is specified, it returns the
        highest verse number of the chapter containing this verse.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.max_verse_num(chap_num)

    def first_verse(self, chap_num: int = None, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns the first BibleVerse of the specified chapter of the BibleBook containing
        this verse. If chap is None, it returns the first BibleVerse of the chapter
        containing this verse.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.first_verse(chap_num, flags=flags)

    def last_verse(self, chap_num: int = None) -> 'BibleVerse':
        '''Returns the last BibleVerse of the specified chapter of the BibleBook containing
        this verse. If chap is None, it returns the last BibleVerse of the chapter
        containing this verse.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.last_verse(chap_num)

    def verse_0_to_1(self) -> 'BibleVerse':
        '''If this BibleVerse refers to a verse number 0, returns an identical BibleVerse
        except with a verse number of 1. Otherwise, returns the original BibleVerse.'''
        if self.verse_num == 0:
            return BibleVerse(self.book, self.chap_num, 1)
        else:
            return self
    
    def verse_1_to_0(self) -> 'BibleVerse':
        '''If this BibleVerse refers to a verse number 1, and a verse 0 is possible for the
        same chapter, returns an identical BibleVerse except with a verse number of 0.
        Otherwise, returns the original BibleVerse. The value of the module 'flags'
        attribute is ignored.'''
        if self.verse_num == 1 and self.min_verse_num(self.chap_num, flags=BibleFlag.VERSE_0) == 0:
            return BibleVerse(self.book, self.chap_num, 0, flags=BibleFlag.VERSE_0)
        else:
            return self

    def add(self, num_verses: int, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a new BibleVerse that is num_verses after this BibleVerse.
        
        If BibleFlag.MULTIBOOK is set (either set by the 'flags' argument or,
        if None, by the module attribute), and the result would be beyond the current
        book, a verse in the next book is returned. Otherwise, if the verse
        does not exist, None is returned. If this BibleVerse already refers to
        verse number 0, VERSE_0 is set on the flags argument for this call.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        book = self.book
        chap_num = self.chap_num
        if self.verse_num == 0:
            flags = flags | BibleFlag.VERSE_0 # Honour existing verse 0s
        verse_num = self.verse_num + num_verses
        max_verse_num = book.max_verse_num(chap_num)
        while verse_num > max_verse_num:
            chap_num += 1
            if chap_num > book.max_chap_num():
                if BibleFlag.MULTIBOOK not in flags:
                    return None
                else:
                    book = book.next()
                    if book is None:
                        return None
                    chap_num = book.min_chap_num()
            
            verse_num = verse_num - max_verse_num + book.min_verse_num(chap_num, flags) - 1 
            max_verse_num = book.max_verse_num(chap_num)

        return BibleVerse(book, chap_num, verse_num, flags=flags)

    def subtract(self, num_verses: int, flags: BibleFlag = None) -> 'BibleVerse':
        '''Return a new BibleVerse that is num_verses before this BibleVerse.
        
        If BibleFlag.MULTIBOOK is set (either set by the 'flags' argument or,
        if None, the module attribute), and the result would be before the current
        book, a verse in the previous book is returned. Otherwise, if the verse
        does not exist, None is returned. If this BibleVerse already refers to
        verse number 0, VERSE_0 is set on the flags argument for this call.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        book = self.book
        chap_num = self.chap_num
        if self.verse_num == 0:
            flags = flags | BibleFlag.VERSE_0 # Honour existing verse 0s
        verse_num = self.verse_num - num_verses
        min_verse_num = book.min_verse_num(chap_num, flags)
        while verse_num < min_verse_num:
            chap_num -= 1
            if chap_num < book.min_chap_num():
                if BibleFlag.MULTIBOOK not in flags:
                    return None
                else:
                    book = book.prev()
                    if book is None:
                        return None
                    chap_num = book.max_chap_num()
             
            verse_num = verse_num + book.max_verse_num(chap_num) - min_verse_num + 1 
            min_verse_num = book.min_verse_num(chap_num)

        return BibleVerse(book, chap_num, verse_num, flags=flags)

    def __repr__(self):
        return f"BibleVerse({self.str(abbrev=True)})"

    def __str__(self):
        return self.str()

    def str(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
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
        
        chap_str = str(self.chap_num) if BibleVersePart.CHAP in verse_parts else ""
        verse_str = str(self.verse_num) if BibleVersePart.VERSE in verse_parts else ""
        
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

    @classmethod
    def whole_bible(cls, flags: BibleFlag = None) -> 'BibleRange':
        '''Returns a BibleRange representing the whole Bible.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        # By definition, we need to allow multibook to encompass whole Bible
        flags |= BibleFlag.MULTIBOOK
        start_book = data.order[0]
        end_book = data.order[len(data.order)-1]
        return BibleRange(start=start_book.first_verse(flags=flags),
                          end=end_book.last_verse(), flags=flags)

    # TODO: Consider allowing a book and verse, without a chapter. Assume first or last chapter as necessary.
    def __init__(self, *args, start: BibleVerse = None, end: BibleVerse = None,
                 flags: BibleFlag = None):
        '''A BibleRange can be constructed in any of the following ways:

            1. From a single string: e.g. BibleRange("Mark 3:1-4:2")

            2. From positional arguments in the following order:
               Start book, start chap num, start verse num, end book, end chap num, end verse num
               Start and end books can be string names or BibleBook enums.
               Later arguments can be omitted or set to None, as in these examples:

                BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 4, 6, flags=BibleFlag.MULTIBOOK) # Matt 2:3-John 4:6
                BibleRange(BibleBook.Matt) # Entire book: Matt 1:1-28:20
                BibleRange(BibleBook.Matt, 2) # Entire chapter: Matt 2:1-23
                BibleRange(BibleBook.Matt, 2, 3) # Single verse: Matt 2:3
                BibleRange(BibleBook.Matt, None, None, BibleBook.John, flags=BibleFlag.MULTIBOOK) # Matt 1:1-John 21:25
                BibleRange(BibleBook.Matt, None, None, None, 4) # Matt 1:1-4:25
                BibleRange(BibleBook.Matt, None, None, None, None, 6) # Matt 1:1-1:6
                BibleRange(BibleBook.Matt, 2, 3, None, 4, 6) # Matt 2:3-4:6

            3. From a start and end BibleVerse, which must be specified using the keywords
               start and end.
               e.g. BibleRange(start=BibleVerse("Mark 3:1"), end=BibleVerse("Mark 4:2"))

            4. As a copy of an existing BibleRange: BibleRange(existing_bible_range)

        If the start reference is obviously larger than the end reference, they are swapped around.
        Note that it is sometimes not possible to distinguish a swapped start and end from
        misformed arguments.           
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        if len(args) == 0:
            if BibleFlag.MULTIBOOK not in flags and start.book != end.book:
                raise MultibookRangeNotAllowedError(f"Multi-book ranges not allowed " + 
                                                    f"({start.book.abbrev} and {end.book.abbrev} are different)")
            if start > end:
                (start, end) = (end, start)
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

        if start_book is not None and isinstance(start_book, str):
            start_book = BibleBook.from_str(start_book, raise_error=True)
        elif start_book is not None and not isinstance(start_book, BibleBook):
            raise InvalidReferenceError(f"{start_book} is not a valid BibleBook")

        if end_book is not None and isinstance(end_book, str):
            end_book = BibleBook.from_str(end_book, raise_error=True)
        elif end_book is not None and not isinstance(end_book, BibleBook):
            raise InvalidReferenceError(f"{end_book} is not a valid BibleBook")

        # If start > end, swap around. The logic is messy due to implied values when args are None.
        if start_book is not None:
            if end_book is not None and start_book > end_book:
                (start_book, end_book) = (end_book, start_book)
                (start_chap, end_chap) = (end_chap, start_chap)
                (start_verse, end_verse) = (end_verse, start_verse)
            elif (end_book is None or end_book == start_book) and start_chap is not None:
                if end_chap is not None and start_chap > end_chap:
                    (start_chap, end_chap) = (end_chap, start_chap)
                    (start_verse, end_verse) = (end_verse, start_verse)
                elif (end_chap is None or end_chap == start_chap) and start_verse is not None:
                    if end_verse is not None and start_verse > end_verse:
                        (start_verse, end_verse) = (end_verse, start_verse)

        have_end = (end_book is not None) or (end_chap is not None) or (end_verse is not None)

        if start_book is None:
            raise InvalidReferenceError(f"A start book is needed for a BibleRange")
        if start_chap is None and start_verse is not None:
            raise InvalidReferenceError("Start verse is missing a start chapter")

        if start_chap is None: # Start is book only
            start = start_book.first_verse(None, flags)
            if not have_end:
                end = start_book.last_verse()
        elif start_verse is None: # Start is book and chap only
            start = start_book.first_verse(int(start_chap), flags=flags)
            if not have_end:
                end = start_book.last_verse(int(start_chap))
        else: # Start is book, chap and verse
            start = BibleVerse(start_book, int(start_chap), int(start_verse), flags=flags)
            if not have_end: # Single verse reference, so end is same as start
                end = BibleVerse(start_book, int(start_chap), int(start_verse), flags=flags)
        
        if have_end: # We have end-point info
            if end_book is None:
                end_book = start_book
            
            if end_chap is None and end_verse is None: # End is book only
                end = end_book.last_verse()
            elif end_verse is None: # End is book and chap only
                end = end_book.last_verse(int(end_chap))
            elif end_chap is None: # End is book and verse only
                if start_book != end_book:
                    raise InvalidReferenceError("End verse is missing an end chapter")
                else:
                    end = BibleVerse(end_book, int(start.chap_num), int(end_verse), flags=flags)
            else:
                end = BibleVerse(end_book, int(end_chap), int(end_verse), flags=flags)

        if BibleFlag.MULTIBOOK not in flags and start.book != end.book:
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
                (self.start == self.start.book.first_verse(self.start.chap_num, flags=flags)) and \
                (self.end == self.end.book.last_verse(self.start.chap_num))

    def spans_start_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans the whole chapter containing the
        starting verse, else False.'''
        return  (self.start == self.start.book.first_verse(self.start.chap_num, flags=flags)) and \
                (self.end >= self.start.book.last_verse(self.start.chap_num))

    def spans_end_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns True if this BibleRange exactly spans the whole chapter containing the
        ending verse, else False.'''
        return  (self.end == self.end.book.last_verse(self.end.chap_num)) and \
                (self.start <= self.end.book.first_verse(self.end.chap_num, flags=flags))

    def is_single_verse(self) -> bool:
        '''Returns True if the BibleRange exactly spans a single verse, else False.'''
        return  (self.start == self.end)

    def split(self, *, by_book: bool = False, by_chap: bool = False, num_verses: bool = None,
              flags: BibleFlag = None):
        '''Split this range into a BibleRangeList of smaller consecutive ranges.
        
        If by_book is true, splits are made at the end of each book.
        If by_chap is true, splits are made end of each chapter.
        If num_verses is specified, splits are made after (no more than) the specified number of verses.
        by_book, by_chap and num_verses can be set in any combination, but one of them must be True,
          otherwise a ValueError will be raised.
        '''
        if not (by_book or by_chap or num_verses):
            raise ValueError("Must split by at least one of book, chapter, or number of verses")

        flags = (flags or globals()['flags'] or BibleFlag.NONE)
        # Set flags if our attributes imply they should be set
        if self.start.book != self.end.book:
            flags |= BibleFlag.MULTIBOOK
        if self.start.verse_num == 0 or self.end.verse_num == 0:
            flags |= BibleFlag.VERSE_0

        split_result = [self]
        
        if by_book:
            new_split = []
            for range_to_split in split_result:
                range_start = range_to_split.start
                range_end = range_start.book.last_verse()
                while range_end < range_to_split.end:
                    new_split.append(BibleRange(start=range_start, end=range_end, flags=flags))
                    range_start = range_end.add(1, flags=flags)
                    range_end = range_start.book.last_verse()
                new_split.append(BibleRange(start=range_start, end=range_to_split.end, flags=flags))
            split_result = new_split

        if by_chap:
            new_split = []
            for range_to_split in split_result:
                range_start = range_to_split.start
                range_end = range_start.last_verse()
                while range_end < range_to_split.end:
                    new_split.append(BibleRange(start=range_start, end=range_end, flags=flags))
                    range_start = range_end.add(1, flags=flags)
                    range_end = range_start.last_verse()
                new_split.append(BibleRange(start=range_start, end=range_to_split.end, flags=flags))
            split_result = new_split

        if num_verses is not None:
            new_split = []
            for range_to_split in split_result:
                range_start = BibleVerse(range_to_split.start, flags=flags)
                range_end = range_start.add(num_verses - 1, flags)
                while range_end is not None and range_end < range_to_split.end:
                    new_split.append(BibleRange(start=range_start, end=range_end, flags=flags))
                    range_start = range_end.add(1, flags)
                    range_end = range_end.add(num_verses, flags)
                new_split.append(BibleRange(start=range_start, end=range_to_split.end, flags=flags))
            split_result = new_split
        
        return BibleRangeList(split_result, flags=flags)

    def is_disjoint(self, other_ref: 'BibleRef') -> bool:
        '''Returns True if this range doesn't overlap with other_ref, otherwise False.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        elif isinstance(other_ref, BibleRangeList):
            return other_ref.is_disjoint(self)
        # Now other_ref should be BibleRange
        lower, higher = (self, other_ref) if self < other_ref else (other_ref, self)
        return lower.end < higher.start

    def is_adjacent(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> bool:
        '''Returns True if this range is adjacent to other_ref, otherwise False.
        A range is adjacent to another verse or range if their bounds are just one verse apart.
        A range is adjacent to a range list if it is disjoint to the entire list and adjacent
        to at least one range in the list
        '''
        if isinstance(other_ref, BibleRangeList):
            return other_ref.is_disjoint(self) and \
                   any(self.is_adjacent(other_range) for other_range in other_ref) 
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        lower, higher = (self, other_ref) if self < other_ref else (other_ref, self)
        return (lower.end.add(1, flags=flags) == higher.start)

    def contains(self, ref: Union[BibleVerse, 'BibleRange']) -> bool:
        '''Returns True if ref is a BibleVerse that falls within this range, or another
        BibleRange whose verses are all contained within this range. Otherwise returns False.

        The same result is returned using the 'in' operator: ref in bible_range
        '''
        if isinstance(ref, BibleVerse):
            return (ref >= self.start and ref <= self.end)
        elif isinstance(ref, BibleRange):
            return (ref.start >= self.start and ref.start <= self.end) and \
                   (ref.end >= self.start and ref.end <= self.end)
        else:
            raise ValueError(f"{ref} is neither a BibleVerse nor BibleRange")

    def surrounds(self, ref: Union[BibleVerse, 'BibleRange']) -> bool:
        '''Returns True if ref is a BibleVerse or BibleRange that falls within this range,
        without including this range's first or last verse. Otherwise, returns False.
        '''
        if isinstance(ref, BibleVerse):
            return (ref > self.start and ref < self.end)
        elif isinstance(ref, BibleRange):
            return (ref.start > self.start and ref.start < self.end) and \
                   (ref.end > self.start and ref.end < self.end)
        else:
            raise ValueError(f"{ref} is neither a BibleVerse nor BibleRange")

    def union(self, other_ref: Union[BibleVerse, 'BibleRange'],
              flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new BibleRangeList of verses that are in this range or other_ref.
        other_ref can be a BibleVerse or BibleRange.
        
        If this range and other_ref overlap or are adjacent, the resulting list contains
        a single BibleRange encompassing them both. Otherwise, the list contains two elements:
        this range and other_ref (converted to a BibleRange if necessary).
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if self.is_disjoint(other_ref) and not self.is_adjacent(other_ref, flags=flags):
            lower, higher = (self, other_ref) if self < other_ref else (other_ref, self) 
            return BibleRangeList([lower, higher], flags=BibleFlag.ALL)
        else:
            start = min(self.start, other_ref.start)
            end = max(self.end, other_ref.end)
            return BibleRangeList([BibleRange(start=start, end=end, flags=flags)], flags=BibleFlag.ALL)

    def intersection(self, other_ref: Union[BibleVerse, 'BibleRange'],
                     flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new BibleRange of verses that are common to both this range and other_ref.
        other_ref can be a BibleVerse or BibleRange.
        If there are verses in common, the list contains a single range.
        If there are no verses in common, the list is empty.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if self.is_disjoint(other_ref):
            return BibleRangeList()
        else:
            start = max(self.start, other_ref.start)
            end = min(self.end, other_ref.end)
            return BibleRangeList([BibleRange(start=start, end=end, flags=flags)], flags=BibleFlag.ALL)

    def difference(self, other_ref: Union[BibleVerse, 'BibleRange'],
                   flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new BibleRangeList of verses that are in this range, but not in other_ref.
        other_ref can be a BibleVerse or BibleRange.

        If this range and other_ref are disjoint, the list contains one item: this range itself.
        If this range surrounds other_ref, the list contains two items:
            a lower-section BibleRange, and an upper-section BibleRange.
        If other_ref contains this range, the list is empty.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if self.is_disjoint(other_ref):
            return BibleRangeList([self], flags=BibleFlag.ALL)
        if other_ref.contains(self):
            return BibleRangeList()

        lower_range = BibleRange(start=self.start, end=other_ref.start.subtract(1, flags=flags))
        upper_range = BibleRange(start=other_ref.end.add(1, flags=flags), end=self.end)
        if self.surrounds(other_ref):
            return BibleRangeList([lower_range, upper_range], flags=BibleFlag.ALL)
        if self < other_ref:
            return BibleRangeList([lower_range], flags=BibleFlag.ALL)
        else:
            return BibleRangeList([upper_range], flags=BibleFlag.ALL)

    def sym_difference(self, other_ref: Union[BibleVerse, 'BibleRange'],
                   flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new BibleRangeList of verses that are either in this range, or in other_ref,
        but not both. other_ref can be a BibleVerse or BibleRange.

        Depending on this range or other_ref, the list contains either one or two BibleRanges.
        If this range and other_ref are exactly equal, this list is empty.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if self == other_ref:
            return BibleRangeList()
        union = self.union(other_ref, flags=flags)
        intersection = self.intersection(other_ref, flags=flags)
        if len(union) > 1 or len(intersection) == 0:
            # Self and other_ref are disjoint and/or adjacent, so the union is the same
            # as the symmetric difference
            return union
        else: # Self and other_ref overlap
            return union[0].difference(intersection[0])

    def __iter__(self):
        verse = self.start
        while verse <= self.end:
            yield verse
            verse = verse.add(1, BibleFlag.MULTIBOOK)

    def __contains__(self, item) -> bool:
        '''Returns True if items is a BibleVerse that falls within this range, otherwise False.
        '''
        return self.contains(item)

    def __repr__(self):
        return f"BibleRange({self.str()})"
    
    def __str__(self):
        return self.str()

    def str(self, abbrev=False, alt_sep=False, nospace=False, flags: BibleFlag = None):
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
        start_str = self.start.str(abbrev, alt_sep, nospace, start_parts) 
        
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
            end_str = self.end.str(abbrev, alt_sep, nospace, end_parts) 
        
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
        '''A BibleRange can be constructed in any of the following ways:

            1. From a single string:
                 BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")

            2. From any iterable containing BibleRanges:
                 BibleRangeList([BibleRange("Mark 3:1-4:2"), BibleRange("Mark 5:6-8"),
                                 BibleRange("Mark 5:10"), BibleRange("Matt 4")])
            
            3. As a copy of an existing BibleRangeList:
                 BibleRangeList(existing_bible_range_list)
        '''
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

    def compress(self, flags: BibleFlag = None):
        '''Sorts this list and merges ranges wherever possible. The result is the smallest
        list of disjoint, non-adjacent ranges spanning the same verses as in the original
        list.

        All groups are removed and replaced with a single group.
        '''
        self.sort()
        node = self._first
        while node is not None and node.next is not None:
            union = node.value.union(node.next.value, flags=flags)
            if len(union) == 1: # Can merge these two ranges with their union
                node.value = union[0]
                self._pop_after(node)
                # We don't move on yet, so we can compare the newly merged range
                # with the (new) next node
            else:
                # The two ranges can't be merged, so move on
                node = node.next

    def is_disjoint(self, other_ref: 'BibleRef') -> bool:
        '''Returns True if this range list doesn't overlap with other_ref, otherwise False.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        return all(self_range.is_disjoint(other_range) for self_range in self for other_range in other_ref)

    def __repr__(self):
        return f'BibleRangeList("{self.str()}")'
    
    def __str__(self):
        return self.str()

    def str(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
               preserve_groups: bool = True, flags: BibleFlag = None):
        '''Returns a string representation of this BibleRangeList.

        If abbrev is True, the abbreviated name of the book is used (instead of the full name).
        If alt_sep is True, chapter and verse numbers are separated by the alternate
          separator (defaults to '.') instead of the standard separator (defaults to ':').
        If nospace is True, no spaces are included in the string.
        If preserve_groups is True, the major group separator is always used between groups,
           and only between groups, with the minor group separator used exclusively within
           groups. Parsing the resulting string should yield an equivalent BibleRangeList.
        If preserve_groups is False, major and minor group separators are used as necessary
           to create the most conventional resulting string, which may result in different
           passage groupings.
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
                                        # This range is a whole set of chapters, so just display chapters
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
                    cur_chap = bible_range.start.chap_num
                else: # Range start is just a particular verse
                    if cur_book == bible_range.start.book: # Continuing same book
                        if at_verse_level and cur_chap == bible_range.start.chap_num: # Continuing same chap
                            start_parts = BibleVersePart.VERSE
                        else: # At chap level or verse level in a different chap
                            if not preserve_groups: # Use major list sep between chapters
                                list_sep = data.MAJOR_LIST_SEP
                            start_parts = BibleVersePart.CHAP_VERSE
                    else: # Different book
                        if not preserve_groups: # Use major list sep between books
                            list_sep = data.MAJOR_LIST_SEP
                        start_parts = BibleVersePart.FULL_REF
                    cur_chap = bible_range.start.chap_num
                    at_verse_level = True # All single verses move us to verse level
                cur_book = bible_range.start.book
                start_str = bible_range.start.str(abbrev, alt_sep, nospace, start_parts) 

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
                        cur_chap = bible_range.end.chap_num
                        at_verse_level = False
                    else: # Range end is a whole chap after a particular verse, or a particular verse
                        if cur_book == bible_range.end.book: # Continuing same book
                            if cur_chap == bible_range.end.chap_num: # Continuing same chap
                                end_parts = BibleVersePart.VERSE
                            else: # Different chap
                                end_parts = BibleVersePart.CHAP_VERSE
                        else: # Different book
                            end_parts = BibleVersePart.FULL_REF
                        cur_chap = bible_range.end.chap_num
                        at_verse_level = True
                    cur_book = bible_range.end.book
                    end_str = bible_range.end.str(abbrev, alt_sep, nospace, end_parts) 
                
                if first_range:
                    list_sep = ""
                    first_range = False
                range_str = f"{list_sep} {start_str}{range_sep}{end_str}"

                if nospace:
                    result_str += range_str.replace(" ", "")
                else:
                    result_str += range_str.strip()

                list_sep = data.MINOR_LIST_SEP # Minor list separator by default within groups
            
            # We've have completed the group
            if preserve_groups:
                list_sep = data.MAJOR_LIST_SEP # Major list separator between groups
                at_verse_level=False
        
        # We've completed all groups
        return result_str


BibleRef = Union[BibleVerse, BibleRange, BibleRangeList]


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
