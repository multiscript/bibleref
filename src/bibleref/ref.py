
# TODO: Implement chapter difference between two verses?s
# TODO: All groups in range lists to be cleared, or set to group by chapter
# TODO: Create context manager to temporarily set or unset particular flags
# TODO: Create module method to make it easier to keep existing flags but set/unset particular flags

from dataclasses import dataclass
from enum import Enum, Flag, auto
from typing import Union

from bibleref import BibleRefException, bible_data, flags

#
# Set-style operations in this module are derived from the python-ranges module
# at https://github.com/Superbird11/ranges, under the MIT Licence
#

class BibleFlag(Flag):
    '''Flags used for controlling various behaviours throughout the package. These can be set globally for the package
    using the `bibleref.ref.flags` attribute, or per-method for methods that includes a `flags` keyword argument.
    '''
    NONE = 0
    '''No `BibleFlag` flags are set. Default value for `bibleref.flags`.'''

    MULTIBOOK = auto()
    '''When set, a `BibleRange` can be constructed that spans multiple Bible books. Existing multibook
    ranges behave correctly even when `MULTIBOOK` is unset.'''

    VERSE_0 = auto()
    '''When set, a `BibleVerse` can be constructed where the first verse number of some chapters
    is 0, not 1. (This is currently true only for the Psalms that have superscriptions.) When you need to mix
    references that do or don't allow for verse 0, it may be easier to set or clear `VERSE_0` for all your code, and
    then use the `verse_0_to_1()` and `verse_1_to_0()` methods on `BibleVerse`, `BibleRange` and `BibleRangeList`
    as necessary.'''

    ALL = MULTIBOOK | VERSE_0
    '''All `BibleFlag` flags are set.'''

flags = BibleFlag.NONE # Default setting for global flags attribute.


class BibleBook(Enum):
    '''An enum of books in the Bible.

    A `BibleBook` has the following extra attributes (added during package import):
      - `abbrev`:   The abbreviated name of the book
      - `title`:    The full title of the book.
      - `regex`:    A regex which matches any acceptable name/abbrev for the book.
      - `order`:    An integer indicating its ordering in the collection of books (0-based).
    
    Two `BibleBook`s can be compared using the standard comparison operators, which compare the
    books' position in the book ordering.
    '''
    # Extra private attributes:
    # _max_verses:  List of max verse number for each chapter (ascending by chapter).
    #                 Len of list is number of chapters. None if no max_verse data supplied.
    # _verse_0s:    Set of chapter numbers (1-indexed) that can begin with a verse 0. Empty set
    #                 if no chapters can begin with a verse 0.
    #
    Gen     = "Gen" 
    Exod    = "Exod"
    Lev     = "Lev"
    Num     = "Num"
    Deut    = "Deut"
    Josh    = "Josh"
    Judg    = "Judg"
    Ruth    = "Ruth"
    ISam    = "1Sam"
    IISam   = "2Sam"
    IKgs    = "1Kgs"
    IIKgs   = "2Kgs"
    IChr    = "1Chr"
    IIChr   = "2Chr"
    Ezra    = "Ezra"
    Neh     = "Neh"
    Esth    = "Esth"
    Job     = "Job"
    Psa     = "Psa"
    Prov    = "Prov"
    Eccl    = "Eccl"
    Song    = "Song"
    Isa     = "Isa"
    Jer     = "Jer"
    Lam     = "Lam"
    Ezek    = "Ezek"
    Dan     = "Dan"
    Hos     = "Hos"
    Joel    = "Joel"
    Amos    = "Amos"
    Obad    = "Obad"
    Jonah   = "Jonah"
    Mic     = "Mic"
    Nah     = "Nah"
    Hab     = "Hab"
    Zeph    = "Zeph"
    Hag     = "Hag"
    Zech    = "Zech"
    Mal     = "Mal"
    Matt    = "Matt"
    Mark    = "Mark"
    Luke    = "Luke"
    John    = "John"
    Acts    = "Acts"
    Rom     = "Rom"
    ICor    = "1Cor"
    IICor   = "2Cor"
    Gal     = "Gal"
    Eph     = "Eph"
    Phil    = "Phil"
    Col     = "Col"
    ITh     = "1Th"
    IITh    = "2Th"
    ITim    = "1Tim"
    IITim   = "2Tim"
    Titus   = "Titus"
    Phlm    = "Phlm"
    Heb     = "Heb"
    Jam     = "Jam"
    IPet    = "1Pet"
    IIPet   = "2Pet"
    IJn     = "1Jn"
    IIJn    = "2Jn"
    IIIJn   = "3Jn"
    Jude    = "Jude"
    Rev     = "Rev"

    @classmethod
    def from_str(cls, string: str, raise_error: bool = False) -> 'BibleBook':
        '''Return the BibleBook matching the given string name.
        Whitespace in `string` is stripped before matching.
        
        If no book matches and raise_error is False (the default), None is returned.
        If no book matches and raise_error is True, an `InvalidReferenceError` is raised.
        '''
        string = string.strip()
        match = False
        for book in BibleBook:
            if book.regex is not None and book.regex.fullmatch(string) is not None:
                match = True
                break
        if match:
            return book
        else:
            if raise_error:
                raise InvalidReferenceError(f"No book found for string '{string}'")
            else:
                return None

    def verse_count(self, flags: BibleFlag = None) -> int:
        '''Returns the number of verses in this `BibleBook`.'''
        count = 0
        for i in range(self.chap_count()):
            count += (self.max_verse_num(i+1) - self.min_verse_num(i+1, flags=flags) + 1)
        return count

    def chap_count(self) -> int:
        '''Returns the number of chapters in this `BibleBook`.
        '''
        return (self.max_chap_num() - self.min_chap_num() + 1)

    def min_chap_num(self) -> int:
        '''Return lowest chapter number (currently always 1) for this `BibleBook`.
        '''
        if self._max_verses is None:
            return 0
        else:
            return 1    # Currently always 1. Perhaps in future some books may have a chapter-0 prologue included?

    def max_chap_num(self) -> int:
        '''Return highest chapter number for this `BibleBook`.
        '''
        if self._max_verses is None:
            return 0
        else:
            return len(self._max_verses)

    def min_verse_num(self, chap_num: int, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (0 or 1) for the specified chapter number of this `BibleBook`.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        if chap_num < self.min_chap_num() or chap_num > self.max_chap_num():
            raise InvalidReferenceError(f"No chapter {chap_num} in {self.title}")
        return 0 if (BibleFlag.VERSE_0 in flags and chap_num in self._verse_0s) else 1

    def max_verse_num(self, chap_num: int) -> int:
        '''Return the highest verse number for the specified chapter number of this `BibleBook`.
        '''
        if chap_num < self.min_chap_num() or chap_num > self.max_chap_num():
            raise InvalidReferenceError(f"No chapter {chap_num} in {self.title}")
        return self._max_verses[chap_num-1]

    def first_verse(self, chap_num: int = None, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a `BibleVerse` for the first verse of the specified chapter of this `BibleBook`.
        If chap is `None`, it returns the first verse of the entire book.
        '''
        if chap_num is None:
            chap_num = self.min_chap_num()
        return BibleVerse(self, chap_num, self.min_verse_num(chap_num, flags))        

    def last_verse(self, chap_num: int = None) -> 'BibleVerse':
        '''Returns a `BibleVerse` for the last verse of the specified chapter of this `BibleBook`.
        If chap is `None`, it returns the last verse of the entire book.
        '''
        if chap_num is None:
            chap_num = self.max_chap_num()
        return BibleVerse(self, chap_num, self.max_verse_num(chap_num))        

    def next(self) -> 'BibleBook':
        '''Returns the next `BibleBook` in the book ordering, or `None` if this is the final book,
        or is not part of the ordering.
        '''
        if self.order is None or self.order == len(bible_data().book_order)-1:
            return None
        else:
            return bible_data().book_order[self.order+1]

    def prev(self) -> 'BibleBook':
        '''Returns the previous `BibleBook` in the book ordering, or `None` if this is the first book,
        or is not part of the ordering.
        '''
        if self.order is None or self.order == 0:
            return None
        else:
            return bible_data().book_order[self.order-1]

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
    '''Flags for referring to the 3 primary attributes of a BibleVerse.
    
    Mainly used internally for converting Bible references strings, to indicate which attributes will display in
    a string representation.
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
     - `book`:       The `BibleBook` of the book of the reference.
     - `chap_num`:   The chapter number (indexed from 1) of the reference.
     - `verse_num`:  The verse number (indexed from 0 or 1) of the reference.

    BibleVerses are immutable. They can be compared using the standard comparison operators, which compare the
    `book`, `chap_num` and `verse_num` in that order.
    '''
    book:       BibleBook
    chap_num:   int
    verse_num:  int

    def __init__(self, *args, flags: BibleFlag = None):
        '''A `BibleVerse` can be constructed in any of the following ways:

        1. From a single string: `BibleVerse("Mark 2:3")`

           Raises a `BibleRefParsingError` if the string cannot be parsed.

        2. From a Bible book, chapter and verse numbers. The Bible book can be a string name, or a `BibleBook` enum:
           `BibleVerse("Mark", 2, 3)`, or `BibleVerse(BibleBook.Mark, 2, 3)`
            
        3. As a copy of another BibleVerse: `BibleVerse(existing_bible_verse)`

        If the supplied arguments are not a valid verse, an `InvalidReferenceError` is raised.
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
        '''Return lowest chapter number (indexed from 1) of the `BibleBook` containing this verse.
        '''
        return self.book.min_chap_num()

    def max_chap_num(self) -> int:
        '''Return highest chapter number (indexed from 1) of the `BibleBook` containing this verse.
        '''
        return self.book.max_chap_num()
    
    def chap_count(self):
        '''Returns the number of chapters in the `BibleBook` containing this verse.
        '''
        return self.book.chap_count()

    def min_verse_num(self, chap_num: int = None, flags: BibleFlag = None) -> int:
        '''Return the lowest verse number (0 or 1) for the specified chapter of the `BibleBook` containing
        this verse. If no chapter is specified, it returns the lowest verse number of the chapter containing
        this `BibleVerse`.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.min_verse_num(chap_num, flags=flags)

    def max_verse_num(self, chap_num: int) -> int:
        '''Return the highest verse number for the specified chapter of the `BibleBook` containing this verse.
        If no chapter is specified, it returns the highest verse number of the chapter containing this `BibleVerse`.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.max_verse_num(chap_num)

    def first_verse(self, chap_num: int = None, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns the first `BibleVerse` of the specified chapter of the `BibleBook` containing
        this verse. If chap is `None`, it returns the first `BibleVerse` of the chapter containing this
        `BibleVerse`.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.first_verse(chap_num, flags=flags)

    def last_verse(self, chap_num: int = None) -> 'BibleVerse':
        '''Returns the last `BibleVerse` of the specified chapter of the `BibleBook` containing
        this verse. If chap is `None`, it returns the last `BibleVerse` of the chapter containing this
        `BibleVerse`.
        '''
        if chap_num is None:
            chap_num = self.chap_num
        return self.book.last_verse(chap_num)

    def verse_0_to_1(self) -> 'BibleVerse':
        '''If the `verse_num` of this `BibleVerse` is 0, returns an identical BibleVerse except with `verse_num`
        set to 1. Otherwise, returns the original `BibleVerse`.'''
        if self.verse_num == 0:
            return BibleVerse(self.book, self.chap_num, 1)
        else:
            return self
    
    def verse_1_to_0(self) -> 'BibleVerse':
        '''If the `verse_num` of this `BibleVerse` is 1, and a verse 0 is possible for the
        same chapter, returns an identical `BibleVerse` except with `verse_num` set to 0. Otherwise, returns the
        original `BibleVerse`. **Note**: The value of the global attribute `bibleref.ref.flags` is *ignored*.'''
        if self.verse_num == 1 and self.min_verse_num(self.chap_num, flags=BibleFlag.VERSE_0) == 0:
            return BibleVerse(self.book, self.chap_num, 0, flags=BibleFlag.VERSE_0)
        else:
            return self

    def add(self, num_verses: int, flags: BibleFlag = None) -> 'BibleVerse':
        '''Returns a new `BibleVerse` that is `num_verses` after this `BibleVerse`.
        
        If `BibleFlag.MULTIBOOK` is set (either by the `flags` argument or, if `None`, by the global attribute), and
        the result would be beyond the current book, a verse in the next book is returned. Otherwise, if the verse
        does not exist, `None` is returned. If the `verse_num` of this `BibleVerse` is already 0,
        `BibleFlag.VERSE_0` is force set on the `flags` argument for this call.

        Using the `+` operator is equivalent to calling `add()` with `flags = None`.
        '''
        if not isinstance(num_verses, int):
            raise TypeError(f"Cannot add a {type(num_verses)} to a BibleVerse")
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

    def subtract(self, other: Union[int, 'BibleVerse'], flags: BibleFlag = None) -> Union[int, 'BibleVerse']:
        '''
        - If `other` is an `int`, returns a new `BibleVerse` that is `other` verses before this `BibleVerse`.
        
          If `BibleFlag.MULTIBOOK` is set (either set by the `flags` argument or, if `None`, the global attribute),
          and the result would be before the current book, a verse in the previous book is returned. Otherwise, if
          the verse does not exist, None is returned. If the `verse_num` of this `BibleVerse` is already 0,
          `BibleFlag.VERSE_0` is force set on the `flags` argument for this call.

        - If `other` is another `BibleVerse`, returns the integer number of verses between this BibleVerse and `other`.
          The number is positive if this verse > `other`, or negative if this verse < `other`.

        Using the `-` operator is equivalent to calling `subtract()` with `flags = None`.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        if isinstance(other, int):
            book = self.book
            chap_num = self.chap_num
            if self.verse_num == 0:
                flags = flags | BibleFlag.VERSE_0 # Honour existing verse 0s
            verse_num = self.verse_num - other
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
        elif isinstance(other, BibleVerse):
            bible_range = BibleRange(start=self, end=other) # Bible will swap start and end as necessary
            difference = bible_range.verse_count() - 1
            if self < other:
                difference *= -1
            return difference
        else:
            raise TypeError(f"Cannot subtract a {type(other)} from a BibleVerse")

    def __add__(self, num_verses: int) -> 'BibleVerse':
        if not isinstance(num_verses, int):
            return NotImplemented
        return self.add(num_verses)
    
    def __sub__(self, other: Union[int, 'BibleVerse']) -> Union[int, 'BibleVerse']:
        if not isinstance(other, int) and not isinstance(other, BibleVerse):
            return NotImplemented
        return self.subtract(other)

    def __repr__(self):
        return f"BibleVerse({self.str(abbrev=True)})"

    def __str__(self):
        return self.str()

    def str(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
            verse_parts: BibleVersePart = BibleVersePart.FULL_REF) -> str:
        '''Returns a configurable string representation of this BibleVerse, as follows:

        - If `abbrev` is True, the abbreviated name of the book is used (instead of the full name).
        - If `alt_sep` is True, chapter and verse numbers are separated by the alternate
          separator (`.` by default) instead of the standard separator (`:` by default).
        - If `nospace` is True, no spaces are included in the string.
        - `verse_parts` is a combination of `BibleVersePart` flags, controlling what combination of book,
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
            verse_sep = bible_data().verse_sep_alt if alt_sep else bible_data().verse_sep_std
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
     - `start`:  The first `BibleVerse` in the range (inclusive).
     - `end`:    The last `BibleVerse` in the range (inclusive).
    
    BibleRanges are immutable. They can be compared using the standard comparison operators, which compare the
    `start` and `end` in that order.

    Iterating over a `BibleRange` returns each `BibleVerse` contained within the range.
    '''
    start: BibleVerse
    end: BibleVerse

    @classmethod
    def whole_bible(cls, flags: BibleFlag = None) -> 'BibleRange':
        '''Returns a `BibleRange` representing the whole Bible.
        '''
        flags = flags or globals()['flags'] or BibleFlag.NONE
        # By definition, we need to allow multibook to encompass whole Bible
        flags |= BibleFlag.MULTIBOOK
        start_book = bible_data().book_order[0]
        end_book = bible_data().book_order[len(bible_data().book_order)-1]
        return BibleRange(start=start_book.first_verse(flags=flags),
                          end=end_book.last_verse(), flags=flags)

    # TODO: Consider allowing a book and verse, without a chapter. Assume first or last chapter as necessary.
    def __init__(self, *args, start: BibleVerse = None, end: BibleVerse = None,
                 flags: BibleFlag = None):
        '''A `BibleRange` can be constructed in any of the following ways:

        1. From a single string: `BibleRange("Mark 3:1-4:2")`

           Raises a `BibleRefParsingError` if the string cannot be parsed.

        2. From a start and end `BibleVerse`, which must be specified using the keyword arguments
           `start` and `end`: `BibleRange(start=BibleVerse("Mark 3:1"), end=BibleVerse("Mark 4:2"))`

        3. As a copy of an existing BibleRange: `BibleRange(existing_bible_range)`

        4. From positional arguments in the following order:
           Start book, start `chap_num`, start `verse_num`, end book, end `chap_num`, end `verse_num`.
           Start and end books can be string names or `BibleBook` enums.
           Later arguments can be omitted or set to `None`, as in these examples:

           `BibleRange(BibleBook.Matt, 2, 3, BibleBook.John, 4, 6, flags=BibleFlag.MULTIBOOK) # Matt 2:3-John 4:6`
           
           `BibleRange(BibleBook.Matt) # Entire book: Matt 1:1-28:20`
           
           `BibleRange(BibleBook.Matt, 2) # Entire chapter: Matt 2:1-23`
           
           `BibleRange(BibleBook.Matt, 2, 3) # Single verse: Matt 2:3`
           
           `BibleRange(BibleBook.Matt, None, None, BibleBook.John, flags=BibleFlag.MULTIBOOK) # Matt 1:1-John 21:25`
           
           `BibleRange(BibleBook.Matt, None, None, None, 4) # Matt 1:1-4:25`
           
           `BibleRange(BibleBook.Matt, None, None, None, None, 6) # Matt 1:1-1:6`
           
           `BibleRange(BibleBook.Matt, 2, 3, None, 4, 6) # Matt 2:3-4:6`

       If the start verse is obviously greater than the end verse, they are swapped around.
        Note that it is sometimes not possible to distinguish a swapped start and end from
        misformed arguments.

        If the supplied arguments are not a valid verse, an `InvalidReferenceError` is raised.
        If the start and end verses are from different `BibleBooks` and `BibleFlag.MULTIBOOK` is not set globally
        or using the `flags` argument, a `MultibookRangeNotAllowedError` is raised. If the arguments are of an
        incorrect number or type, a `ValueError` is raised.     
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
        '''Returns a new `BibleRange` created by calling `verse_0_to_1()` on both the `start` and `end`
        `BibleVerse` attributes.'''
        return BibleRange(start=self.start.verse_0_to_1(), end=self.end.verse_0_to_1(),
                          flags=BibleFlag.ALL)

    def verse_1_to_0(self) -> 'BibleRange':
        '''Returns a new `BibleRange` created by calling `verse_1_to_0()` on both the `start` and `end`
        `BibleVerse` attributes. **Note**: The value of the global attribute `bibleref.ref.flags` is *ignored*.'''
        return BibleRange(start=self.start.verse_1_to_0(), end=self.end.verse_1_to_0(),
                          flags=BibleFlag.ALL)

    def is_whole_book(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` exactly spans one whole book, else `False`.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(None, flags)) and \
                (self.end == self.end.book.last_verse())

    def spans_start_book(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` includes the whole book that contains the `start` verse,
        else `False`.'''
        return  (self.start == self.start.book.first_verse(None, flags)) and \
                (self.end >= self.start.book.last_verse())

    def spans_end_book(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` includes the whole book that contains the `end` verse,
        else `False`.'''
        return  (self.end == self.end.book.last_verse()) and \
                (self.start <= self.end.book.first_verse(None, flags))

    def is_whole_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` exactly spans one whole chapter, else `False`.'''
        return  (self.start.book == self.end.book) and \
                (self.start == self.start.book.first_verse(self.start.chap_num, flags=flags)) and \
                (self.end == self.end.book.last_verse(self.start.chap_num))

    def spans_start_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` includes the whole chapter that contains the `start` verse,
        else `False`.'''
        return  (self.start == self.start.book.first_verse(self.start.chap_num, flags=flags)) and \
                (self.end >= self.start.book.last_verse(self.start.chap_num))

    def spans_end_chap(self, flags: BibleFlag = None) -> bool:
        '''Returns `True` if this `BibleRange` includes the whole chapter that contains the `end` verse,
        else `False`.'''
        return  (self.end == self.end.book.last_verse(self.end.chap_num)) and \
                (self.start <= self.end.book.first_verse(self.end.chap_num, flags=flags))

    def is_single_verse(self) -> bool:
        '''Returns `True` if the `BibleRange` exactly contains a single verse, else `False`.'''
        return  (self.start == self.end)

    def verse_count(self, flags: BibleFlag = None):
        '''Returns the number of verses in this range.'''
        # We split the range into chapters, which is not the most efficient approach, but makes the counting simple.
        bible_ranges = self.split(by_chap=True) # Each range will thus be within its own chapter
        count = 0
        for bible_range in bible_ranges:
            count += (bible_range.end.verse_num - bible_range.start.verse_num + 1)
        return count

    def chap_count(self, whole: bool = False, flags: BibleFlag = None):
        '''Returns the number of chapters in this range.
        
        If `whole` is True, only whole chapters are counted. Otherwise partial chapters are also included in the
        count.'''
        # We split the range into chapters, which is not the most efficient approach, but makes the counting simple.
        bible_ranges = self.split(by_chap=True)
        count = len(bible_ranges)
        if whole:
            if not bible_ranges[0].is_whole_chap():
                count -= 1
            if len(bible_ranges) > 1 and not bible_ranges[-1].is_whole_chap():
                count -= 1
        return count

    def book_count(self, whole: bool = False, flags: BibleFlag = None):
        '''Returns the number of Bible books in this range.
        
        If `whole` is True, only whole books are counted. Otherwise, partial books are also included in the count.'''
        # We split the range into books, which is not the most efficient approach, but makes the counting simple.
        bible_ranges = self.split(by_book=True)
        count = len(bible_ranges)
        if whole:
            if not bible_ranges[0].is_whole_book():
                count -= 1
            if len(bible_ranges) > 1 and not bible_ranges[-1].is_whole_book():
                count -= 1
        return count

    def split(self, *, by_book: bool = False, by_chap: bool = False, num_verses: bool = None,
              flags: BibleFlag = None):
        '''Split this `BibleRange` into a `BibleRangeList` of smaller consecutive ranges, as follows:
        
        - If `by_book` is `True`, splits are made at the end of each book.
        - If `by_chap` is `True`, splits are made end of each chapter.
        - If `num_verses` is specified, splits are made after (no more than) the specified number of verses.
        - `by_book`, `by_chap` and `num_verses` can be set in any combination, but one of them must be not `None`,
          otherwise a `ValueError` will be raised.
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
        '''Returns `True` if this range doesn't overlap with any verses in `other_ref`, otherwise `False`.
        '''
        if isinstance(other_ref, BibleRangeList):
            return other_ref.is_disjoint(self) # is_disjoint() is commutative, so use the list implementation
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):
            lower, higher = (self, other_ref) if self < other_ref else (other_ref, self)
            return lower.end < higher.start
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def is_adjacent(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> bool:
        '''Returns `True` if this range is adjacent to `other_ref`, otherwise `False`.
        
        A `BibleRange` is considered adjacent to another `BibleVerse` or `BibleRange` if their bounds are a single
        verse apart. A `BibleRange` is considered adjacent to a `BibleRangeList` if it is disjoint
        to the entire list and adjacent to at least one `BibleRange` in the list.
        '''
        if isinstance(other_ref, BibleRangeList):
            # BibleRangeList doesn't define is_adjacent(), so we have to implement here
            return other_ref.is_disjoint(self) and \
                   any(self.is_adjacent(other_range) for other_range in other_ref) 
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):        
            lower, higher = (self, other_ref) if self < other_ref else (other_ref, self)
            return (lower.end.add(1, flags=flags) == higher.start)
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def contains(self, other_ref: 'BibleRef') -> bool:
        '''Returns `True` if all the verses in `other_ref` fall within this `BibleRange`. Otherwise
        returns `False`.

        The same result is returned using the 'in' operator (i.e. `other_ref in bible_range`).
        '''
        if isinstance(other_ref, BibleRangeList):
            # contains() is not commutative, but we still use the BibleRangeList implementation.
            return BibleRangeList([self]).contains(other_ref)
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):
            return (other_ref.start >= self.start and other_ref.start <= self.end) and \
                   (other_ref.end >= self.start and other_ref.end <= self.end)
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def surrounds(self, other_ref: 'BibleRef') -> bool:
        '''Returns `True` if all the verses in `other_ref` fall within this `BibleRange`, *without*
        including this range's `start` or `end` `BibleVerse`. Otherwise, returns `False`.
        '''
        if isinstance(other_ref, BibleRangeList):
            # BibleRangeList doesn't define surrounds(), so we have to implement here
            return all(self.surrounds(other_range) for other_range in other_ref) 
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):
            return (other_ref.start > self.start and other_ref.start < self.end) and \
                   (other_ref.end > self.start and other_ref.end < self.end)
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def union(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new `BibleRangeList` of verses that are either in this range or `other_ref`.
        
        If this range and `other_ref` overlap or are adjacent, the resulting `BibleRangeList` contains one element:
        a single `BibleRange` encompassing them both. Otherwise, the list contains two elements:
        this `BibleRange` and `other_ref` (converted to a `BibleRange` if necessary).

        Using the `|` operator is equivalent to calling `union()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleRangeList):
            # Use the BibleRangeList implementation
            return other_ref.union(self, flags=flags)
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):
            if self.is_disjoint(other_ref) and not self.is_adjacent(other_ref, flags=flags):
                lower, higher = (self, other_ref) if self < other_ref else (other_ref, self) 
                return BibleRangeList([lower, higher], flags=BibleFlag.ALL)
            else:
                start = min(self.start, other_ref.start)
                end = max(self.end, other_ref.end)
                return BibleRangeList([BibleRange(start=start, end=end, flags=flags)], flags=BibleFlag.ALL)
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def intersection(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new `BibleRangeList` of verses that are common to both this range and `other_ref`.
        
        If there are verses in common, the list contains a single `BibleRange` element.
        If there are no verses in common, the list is empty.

        Using the `&` operator is equivalent to calling `intersection()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleRangeList):
            # Use the BibleRangeList implementation
            return other_ref.intersection(self, flags=flags)
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRange (and we don't enforce existing flags for conversions)
            other_ref = BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)
        if isinstance(other_ref, BibleRange):
            if self.is_disjoint(other_ref):
                return BibleRangeList()
            else:
                start = max(self.start, other_ref.start)
                end = min(self.end, other_ref.end)
                return BibleRangeList([BibleRange(start=start, end=end, flags=flags)], flags=BibleFlag.ALL)
        else:
            raise ValueError(f"{other_ref} is not a valid BibleRef")

    def difference(self, other_ref: Union[BibleVerse, 'BibleRange'],
                   flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new `BibleRangeList` of verses that are in this range, but not in `other_ref`.

        If this range and `other_ref` are disjoint, the list contains one element: a copy of this `BibleRange`.
        If this range surrounds `other_ref`, the list contains two elements:
            a lower-section `BibleRange`, and an upper-section `BibleRange`.
        If `other_ref` contains this range, the list is empty.

        Using the `-` operator is equivalent to calling `difference()` with `flags = None`.
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
        '''Returns a new `BibleRangeList` of verses that are either in this range, or in `other_ref`,
        but not both.

        Depending on this range and `other_ref`, the `BibleRangeList` contains either one or two
        `BibleRange` elements. If this range and `other_ref` are exactly equal, this list is empty.

        Using the `^` operator is equivalent to calling `sym_difference()` with `flags = None`.
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

    def __contains__(self, bible_ref) -> bool:
        '''Returns True if item is a BibleRef that falls within this range, otherwise False.
        '''
        return self.contains(bible_ref)
    
    def __or__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.union(other_ref)

    def __and__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.intersection(other_ref)

    def __sub__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.difference(other_ref)

    def __xor__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.sym_difference(other_ref)

    def __repr__(self):
        return f"BibleRange({self.str()})"
    
    def __str__(self):
        return self.str()

    def str(self, abbrev=False, alt_sep=False, nospace=False, flags: BibleFlag = None):
        '''Returns a configurable string representation of this `BibleRange`, as follows:

        - If `abbrev` is `True`, the abbreviated name of the book is used (instead of the full name).
        - If `alt_sep` is `True`, chapter and verse numbers are separated by the alternate
          separator (defaults to `.`) instead of the standard separator (defaults to `:`).
        - If `nospace` is `True`, no spaces are included in the string.
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
            range_sep = bible_data().range_sep
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
                if self.start.chap_num == self.end.chap_num:
                    end_parts &= ~BibleVersePart.CHAP # Omit chapter
            
            end_str = self.end.str(abbrev, alt_sep, nospace, end_parts) 
        
        result = f"{start_str}{range_sep}{end_str}"
        if nospace:
            return result.replace(" ", "")
        else:
            return result.strip()


class BibleRangeList(util.GroupedList):
    '''A list of `BibleRange` elements, allowing for grouping and set-style operations.

    Currently the grouping functionality is provided via a superclass (`bibleref.util.GroupedList`, a doubly-linked
    list), though this should be considered an implementation detail.
    '''
    def __init__(self, *args, flags: BibleFlag = None):
        '''A BibleRange can be constructed in any of the following ways:

        1. From a single string: `BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")`

           Raises a `BibleRefParsingError` if the string cannot be parsed.

           When parsing a string, each major group-separator (`;` by default) places subsequent
           Bible ranges into a new group. Each minor group-separator (`,` by default) places subsequent
           passages into the same group.

            ```python
            >>> from bibleref import *
            >>> range_list = BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")
            >>> len(range_list.groups)
            3
            >>> range_list.groups[0]
            GroupView([BibleRange(Mark 3-4:2)])
            >>> range_list.groups[1]
            GroupView([BibleRange(Mark 5:6-5:8), BibleRange(Mark 5:10)])
            >>> range_list.groups[2]
            GroupView([BibleRange(Matthew 4)])
            >>> range_list.groups[1][0]
            BibleRange(Mark 5:6-5:8)
            >>> range_list.groups[1][1]
            BibleRange(Mark 5:10)
            ```
        2. From any iterable containing BibleRanges:
           `BibleRangeList([BibleRange("Mark 3:1-4:2"), BibleRange("Mark 5:6-8"),
                            BibleRange("Mark 5:10"), BibleRange("Matt 4")])`
            
        3. As a copy of an existing BibleRangeList: `BibleRangeList(existing_bible_range_list)`
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

    @property
    def groups(self) -> util.GroupedList.GroupViews:
        '''Returns the `bibleref.util.GroupedList.GroupViews` collection for this list.'''
        return super().groups    

    def _check_type(self, value):
        if not isinstance(value, BibleRange):
            raise TypeError(f"Item is not a BibleRange: {value}")

    def verse_0_to_1(self):
        '''Modifies this list *in-place* by calling `verse_0_to_1()` on every `BibleRange` in the list
        and using the result to replace the original range. Returns `None`.'''
        for node in self._node_iter():
            node.value = node.value.verse_0_to_1()
        return None

    def verse_1_to_0(self):
        '''Modifies this list *in-place* by calling `verse_1_to_0()` on every `BibleRange` in the list
        and using the result to replace the original range. Returns `None`.
        **Note**: The value of the global attribute `bibleref.ref.flags` is *ignored*.'''
        for node in self._node_iter():
            node.value = node.value.verse_1_to_0()
        return None

    def verse_count(self, flags: BibleFlag = None):
        '''Returns the total number of verses in the ranges in the list.'''
        return sum([bible_range.verse_count(flags=flags) for bible_range in self])

    def chap_count(self, whole: bool = False, flags: BibleFlag = None):
        '''Returns the total number of chapters in the ranges in the list.
        
        If `whole` is True, only whole chapters are counted. Otherwise partial chapters are also included in the
        count.'''
        return sum([bible_range.chap_count(whole=whole, flags=flags) for bible_range in self])

    def book_count(self, whole: bool = False, flags: BibleFlag = None):
        '''Returns the total number of Bible books in the ranges in the list.
        
        If `whole` is True, only whole books are counted. Otherwise, partial books are also included in the count.'''
        return sum([bible_range.book_count(whole=whole, flags=flags) for bible_range in self])

    def consolidate(self, flags: BibleFlag = None):
        '''Sorts this list in-place and merges ranges wherever possible. The result is the smallest
        list of disjoint, non-adjacent `BibleRange` elements spanning the same verses as in the original
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
        '''Returns `True` if every `BibleRange` is disjoint with all the verses in `other_ref`, otherwise `False`.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        return all(self_range.is_disjoint(other_range) for self_range in self for other_range in other_ref)

    def contains(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> bool:
        '''Returns `True` if all the verses in `other_ref` fall within at least one of the `BibleRange` elements
        in this list. Otherwise returns `False`.

        The same result is returned using the 'in' operator (i.e. `other_ref in bible_range_list`).
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        # Create a consolidated copy of ourselves
        self_copy = BibleRangeList(self)
        self_copy.consolidate(flags=flags)
        # Every one of the other list's ranges must be contained by at least one of the our ranges
        return all(any(self_range.contains(other_range) for self_range in self_copy) for other_range in other_ref)

    def union(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Creates a new `BibleRangeList` that contains all the verses in this `BibleRangeList`
        and all the verses in `other_ref`, then consolidates the result and returns it.

        Using the `|` operator is equivalent to calling `union()` with `flags = None`.
        '''
        new_list = BibleRangeList(self)
        new_list.union_update(other_ref, flags=flags)
        return new_list

    def union_update(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Updates this list to be the union of its existing elements and `other_ref`, then consolidates this list.

        Using the `|=` operator is equivalent to calling `union_update()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        if not isinstance(other_ref, BibleRangeList):
            raise ValueError(f"{other_ref} is not a valid BibleRef")        

        self.extend(other_ref)
        self.consolidate(flags=flags)

    def intersection(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Creates a new `BibleRangeList` of verses that are common to both this `BibleRangeList` and `other_ref`,
        then consolidates the result and returns it. If there are no verses in common, the returned list is empty.

        Using the `&` operator is equivalent to calling `intersection()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        if not isinstance(other_ref, BibleRangeList):
            raise ValueError(f"{other_ref} is not a valid BibleRef")        

        # Each BibleRefList is effectively a union of its elements.
        # Key set theory identity:
        #   (A0 ∪ A1) ∩ (B0 ∪ B1) = (A0 ∩ B0) ∪ (A0 ∩ B1) ∪ (A1 ∩ B0) ∪ (A1 ∩ B1)
        # So the intersection of two BibleRefLists is a new list of the intersection of each item
        # combination.
        new_list = BibleRangeList()
        for self_range in self:
            for other_range in other_ref:
                item_intersection_list = self_range.intersection(other_range, flags=flags)
                if len(item_intersection_list) > 0:
                    new_list.append(item_intersection_list[0])
        new_list.consolidate(flags=flags)
        return new_list

    def intersection_update(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Updates this list to be the intersection of its existing elements and `other_ref`, then consolidates
        this list.

        Using the `&=` operator is equivalent to calling `intersection_update()` with `flags = None`.
        '''
        intersection_list = self.intersection(other_ref, flags=flags)
        self.clear()
        self.extend(intersection_list)

    def difference(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new `BibleRangeList` of verses that are in this `BibleRangeList`, but not in `other_ref`.

        Using the `-` operator is equivalent to calling `difference()` with `flags = None`.
        '''
        new_list = BibleRangeList(self)
        new_list.difference_update(other_ref, flags=flags)
        return new_list

    def difference_update(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Updates this list to be the difference of its existing elements and `other_ref`, then consolidates
        this list.

        Using the `-=` operator is equivalent to calling `difference_update()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        if not isinstance(other_ref, BibleRangeList):
            raise ValueError(f"{other_ref} is not a valid BibleRef")        

        # Each BibleRefList is effectively a union of its elements.
        # Key set theory identity: (where \ means set difference, so A \ B = A - B)
        #   (A0 ∪ A1) \ (B0 ∪ B1) = [(A0 \ B0) \ B1] ∪ [(A1 \ B0) \ B1]
        # So the difference of two BibleRefLists is a new list of the cumulative difference of each
        # item in the second list from each item in the first list.
        #
        # What's a little difficult is that the difference of two items can itself result in a list
        # (of two items). As a result, it's easiest to calculate the difference in-place.
        #
        # In-place set difference requires us to make many updates to this list during iteration,
        # beyond what a for-loop can cope with. Therefore we use a while loop.
        self_node = self._first
        while self_node is not None:
            for other_range in other_ref:
                self_range = self_node.value
                item_difference_list = self_range.difference(other_range, flags=flags)
                if len(item_difference_list) > 0:
                    # This item_difference_list now should replace self_node, and self_node
                    # changed to point to the first of the result items. The easiest
                    # way to do this is to insert the result items starting from the end:
                    old_self_node = self_node
                    for difference_range in reversed(item_difference_list):
                        self._insert_before(self_node, difference_range)
                        self_node = self_node.prev
                    self._pop_node(old_self_node)
            self_node = self_node.next
        self.consolidate()

    def sym_difference(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Returns a new `BibleRangeList` of verses that are either in this `BibleRangeList`, or in `other_ref`,
        but not both.

        Using the `^` operator is equivalent to calling `sym_difference()` with `flags = None`.
        '''
        if isinstance(other_ref, BibleVerse):
            # Convert to BibleRangeList (and we don't enforce existing flags for conversions)
            other_ref = BibleRangeList([BibleRange(start=other_ref, end=other_ref, flags=BibleFlag.ALL)])
        elif isinstance(other_ref, BibleRange):
            other_ref = BibleRangeList([other_ref])
        if not isinstance(other_ref, BibleRangeList):
            raise ValueError(f"{other_ref} is not a valid BibleRef")        
        
        union_list = self.union(other_ref, flags=flags)
        intersection_list = self.intersection(other_ref, flags=flags)
        return union_list.difference(intersection_list, flags=flags)

    def sym_difference_update(self, other_ref: 'BibleRef', flags: BibleFlag = None) -> 'BibleRangeList':
        '''Updates this list to be the symmetric difference of its existing elements and `other_ref`, then
        consolidates this list.

        Using the `^=` operator is equivalent to calling `sym_difference_update()` with `flags = None`.
        '''
        sym_difference_list = self.sym_difference(other_ref, flags=flags)
        self.clear()
        self.extend(sym_difference_list)

    def __contains__(self, bible_ref) -> bool:
        '''Returns True if item is a BibleRef that falls within this range, otherwise False.
        '''
        return self.contains(bible_ref)

    def __or__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.union(other_ref)
    
    def __and__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.intersection(other_ref)

    def __sub__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.difference(other_ref)

    def __xor__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.sym_difference(other_ref)

    def __ior__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.union_update(other_ref)    

    def __iand__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.intersection_update(other_ref)

    def __isub__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.difference_update(other_ref)

    def __ixor__(self, other_ref: 'BibleRef') -> 'BibleRangeList':
        return self.sym_difference_update(other_ref)

    def __repr__(self):
        return f'BibleRangeList("{self.str()}")'
    
    def __str__(self):
        return self.str()

    def str(self, abbrev: bool = False, alt_sep: bool = False, nospace: bool = False,
               preserve_groups: bool = True, flags: BibleFlag = None):
        '''Returns a configuratble string representation of this BibleRangeList, as follows:

        - If `abbrev` is `True`, the abbreviated name of the book is used (instead of the full name).
        - If `alt_sep` is `True`, chapter and verse numbers are separated by the alternate
          separator (defaults to `.`) instead of the standard separator (defaults to `:`).
        - If `nospace` is `True`, no spaces are included in the string.
        - If `preserve_groups` is `True`, the major group separator is always used between groups,
          and only between groups, with the minor group separator used exclusively within
          groups. Parsing the resulting string should yield an equivalent `BibleRangeList`.
        - If `preserve_groups` is `False`, major and minor group separators are used as necessary
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
                                list_sep = bible_data().major_list_sep
                                start_parts = BibleVersePart.CHAP
                                at_verse_level = False
                            else: # Preserving groups
                                if list_sep == bible_data().major_list_sep:
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
                                list_sep = bible_data().major_list_sep
                                start_parts = BibleVersePart.CHAP
                                at_verse_level = False
                            else: # Preserving groups
                                if list_sep == bible_data().major_list_sep:
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
                            list_sep = bible_data().major_list_sep
                        start_parts = BibleVersePart.BOOK_CHAP
                        at_verse_level = False
                    cur_chap = bible_range.start.chap_num
                else: # Range start is just a particular verse
                    if cur_book == bible_range.start.book: # Continuing same book
                        if at_verse_level and cur_chap == bible_range.start.chap_num: # Continuing same chap
                            start_parts = BibleVersePart.VERSE
                        else: # At chap level or verse level in a different chap
                            if not preserve_groups: # Use major list sep between chapters
                                list_sep = bible_data().major_list_sep
                            start_parts = BibleVersePart.CHAP_VERSE
                    else: # Different book
                        if not preserve_groups: # Use major list sep between books
                            list_sep = bible_data().major_list_sep
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
                    range_sep = bible_data().range_sep
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

                list_sep = bible_data().minor_list_sep # Minor list separator by default within groups
            
            # We've have completed the group
            if preserve_groups:
                list_sep = bible_data().major_list_sep # Major list separator between groups
                at_verse_level=False
        
        # We've completed all groups
        return result_str

    #
    # We wrap our public superclass methods, so that pdoc auto-generates our documentation, and also to emphasise
    # that the implementation could change.
    #

    def index(self, value, min_index: int = None, limit_index: int =None):
        return super().index(value, min_index, limit_index)

    def count(self, value):
        return super().count(value)

    def prepend(self, value, new_group: bool = False):
        return super().prepend(value, new_group)
    
    def append(self, value, new_group: bool = False):
        return super().append(value, new_group)

    def append_group(self, iterable):
        return super().append_group(iterable)

    def extend(self, iterable):
        return super().extend(iterable)
    
    def insert(self, index: int, value):
        return super().insert(index, value)

    def pop(self, index: int = None):
        return super().pop(index)

    def remove(self, value):
        return super().remove(value)

    def clear(self):
        return super().clear()
    
    def reverse(self):
        return super().reverse()
    
    def sort(self):
        return super().sort()

    def equals(self, other_iterable, compare_groups=True) -> bool:
        return super().equals(other_iterable, compare_groups)


BibleRef = Union[BibleVerse, BibleRange, BibleRangeList]
'''A convenience type to indicate either a `BibleVerse`, `BibleRange` or `BibleRangeList`.'''


class MultibookRangeNotAllowedError(BibleRefException):
    '''Raised when trying to create a `BibleRange` with a different start and end `BibleBook` and
    `BibleFlag.MULTIBOOK` is not set (either globally or in a `flags` method argument).'''


class InvalidReferenceError(BibleRefException):
    '''Raided when trying to instantiate a BibleBook, BibleVerse or BibleRange that is not a valid
    Bible reference.'''


class BibleRefParsingError(BibleRefException):
    '''Raised when there is an error parsing a string into a Bible reference.
    
    Contains two extra attributes:
    
     - `start_pos`: index of the first unexpected character in the string for parsing.
     - `end_pos`:   index of the last unexpected character in the string for parsing.
    '''
    def __init__(self, mesg, start_pos=None, end_pos=None, *args, **kwargs):
        super().__init__(mesg, *args, **kwargs)
        self.start_pos = start_pos
        self.end_pos = end_pos

