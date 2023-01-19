'''
# Overview

**bibleref is a Python package for manipulating references to Bible books, verses and verse-ranges, including string
parsing and conversion.** It's designed for future use with [Multiscript](https://multiscript.app), but it can be
used as a standalone package. Its only dependency is the [Lark](https://github.com/lark-parser/lark) parsing toolkit.

`bibleref` defines the following primary classes:
  - `bibleref.ref.BibleBook`:      An Enum of books in the Bible, with extra methods.
  - `bibleref.ref.BibleVerse`:     A reference to a single Bible verse (e.g. Matt 2:3)
  - `bibleref.ref.BibleRange`:     A reference to a continuous range of Bible verses (e.g. Matt 2:3-4:5)
  - `bibleref.ref.BibleRangeList`: A specialised list of `BibleRange` elements, allowing for grouping and
  set-style operations.

(There is no `BibleChapter` class, as chapters are usually best handled as a `BibleRange`.)

For convenience these classes can be directly imported from `bibleref`. They can each convert to and from strings.
`BibleRange` and `BibleRangeList` implement common set operations (such as union, intersection, difference and 
symmetric difference).

# Example

```python
>>> from bibleref import *
>>> range_list = BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")
>>> print(range_list)
Mark 3-4:2; 5:6-8, 10; Matthew 4
>>> range_list[1]
BibleRange(Mark 5:6-5:8)
>>> range_list[1].start
BibleVerse(Mark 5:6)
>>> range_list[1].end
BibleVerse(Mark 5:8)
>>> range_list[1].end.book
<BibleBook.Mark: 'Mark'>
>>> for verse in range_list[1]:
...     print(verse)
... 
Mark 5:6
Mark 5:7
Mark 5:8
```

# Data

The Bible book, chapter and verse data is specified in the `bibleref.data` sub-module.

# Global Flags
 
The global attribute `bibleref.ref.flags` is a `bibleref.ref.BibleFlag` enum whose elements control package-wide
behaviour. Many methods take a `flags` keyword-argument that overrides the global `flags` attribute during the
execution of that method.

# Top-Level Objects
'''
import bibleref


def bible_data():
    '''Returns the package-global `BibleData` instance, which can be used to modify the default Bible data
    used by the package.
    '''
    return _bible_data


class BibleData:
    def __init__(self):
        self._range_sep           = "-"
        self._major_list_sep      = ";"
        self._minor_list_sep      = ","
        self._verse_sep_std       = ":"
        self._verse_sep_alt       = "."
    
    @property
    def range_sep(self):
        '''Range separator character used to separate start and end of a Bible range.'''
        return self._range_sep
    
    @range_sep.setter
    def range_sep(self, value):
        self._range_sep = value
        bibleref.parser.recreate_parser()

    @property
    def major_list_sep(self):
        '''Major list separator character.

        Separates Bible ranges in different groups. Usually separates ranges in different chapters.'''
        return self._major_list_sep
    
    @major_list_sep.setter
    def major_list_sep(self, value):
        self._major_list_sep = value
        bibleref.parser.recreate_parser()

    @property
    def minor_list_sep(self):
        '''Minor list separator character.

        Separates Bible ranges in the same group. Usually separates ranges in the same chapter.'''
        return self._minor_list_sep
    
    @minor_list_sep.setter
    def minor_list_sep(self, value):
        self._minor_list_sep = value
        bibleref.parser.recreate_parser()

    @property
    def verse_sep_std(self):
        '''Standard verse separator character, used to separate chapter and verse numbers'''
        return self._verse_sep_std
    
    @verse_sep_std.setter
    def verse_sep_std(self, value):
        self._verse_sep_std = value
        bibleref.parser.recreate_parser()

    @property
    def verse_sep_alt(self):
        '''Alternate verse separator character, used to separate chapter and verse numbers'''
        return self._verse_sep_alt
    
    @verse_sep_alt.setter
    def verse_sep_alt(self, value):
        self._verse_sep_alt = value
        bibleref.parser.recreate_parser()


_bible_data = BibleData()


class BibleRefException(Exception):
    '''Parent class for all Exception types in this package.'''


from .ref import BibleBook, BibleFlag, BibleRange, BibleRangeList, BibleRef, BibleVerse, BibleVersePart
