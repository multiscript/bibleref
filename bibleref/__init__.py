'''
# Overview

**bibleref is a package for manipulating references to Bible books, verses and verse-ranges, including string parsing
and conversion.** It's designed for future use with [Multiscript](https://multiscript.app), but it can be used
as a standalone package. Its only dependency is the [Lark](https://github.com/lark-parser/lark) parsing toolkit.

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

# Top-Level Classes
'''
class BibleRefException(Exception):
    '''Parent class for all Exception types in this package.'''


from .ref import BibleBook, BibleFlag, BibleRange, BibleRangeList, BibleRef, BibleVerse, BibleVersePart


