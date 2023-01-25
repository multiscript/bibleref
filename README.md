# bibleref

**bibleref is a Python package for handling references to Bible books, verses and verse-ranges, including string
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

# Docs

See [multiscript.app/bibleref](https://multiscript.app/bibleref)

# Examples

```python
>>> import bibleref
>>> from bibleref import *
>>>                             # Parse from string
>>> range_list = BibleRangeList("Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2")
>>> print(range_list)           # Convert back to a string
Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2
>>> len(range_list)
6
>>> range_list[0]               # Individual ranges from a list
BibleRange(Mark 2-3:6)
>>> range_list[1]
BibleRange(Mark 4)
>>> range_list[5].start         # Start and...
BibleVerse(Luke 2:1)
>>> range_list[5].end           # ...end verses of a range.
BibleVerse(Luke 2:52)
>>> range_list[5].end.book      # Verse attributes
<BibleBook.Luke: 'Luke'>
>>> range_list[5].end.chap_num
2
>>> range_list[5].end.verse_num
52
>>> len(range_list.groups)
4
>>> range_list.groups[2]        # Indivdual range groups from a list
GroupView([BibleRange(Mark 6:1-6), BibleRange(Mark 6:30-44), BibleRange(Mark 6:56)])
>>> range_list.groups[2][0]     # Individual ranges within the group
BibleRange(Mark 6:1-6)
>>> range_list.groups[2][1]        
BibleRange(Mark 6:30-44)
>>> range_list.groups[2][2]
BibleRange(Mark 6:56)
>>> BibleVerse('Mark 2:23') + 10 # Verse addition / subtraction
BibleVerse(Mark 3:5)
>>> BibleVerse('Mark 3:5') - BibleVerse('Mark 2:23')
10
>>> BibleRange('1 John').split(by_chap=True, num_verses=15) # Range splits
BibleRangeList("1 John 1, 2:1-15, 16-29, 3:1-15, 16-24, 4:1-15, 16-21, 5:1-15, 16-21")
>>> for verse in BibleRange('Mark 6:1-3'): # Range iteration
...     print(verse)
... 
Mark 6:1
Mark 6:2
Mark 6:3
>>> bibleref.flags = BibleFlag.MULTIBOOK   # Enable multi-book ranges
>>> BibleRange('Matt 10-John 10')
BibleRange(Matthew 10-John 10)
>>> list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
>>> list_2 = BibleRangeList("John 1-3; Luke 9; Matt 3-5; Mark 12")
>>> list_1 | list_2                     # Union
BibleRangeList("Matthew 2-5; Mark 6-8; 12; Luke 9-12; John 1-3; 14-16")
>>> list_1 & list_2                     # Intersection
BibleRangeList("Matthew 3-4")
>>> list_1 - list_2                     # Difference
BibleRangeList("Matthew 2; Mark 6-8; Luke 10-12; John 14-16")
>>> list_1 ^ list_2                     # Symmetric difference
BibleRangeList("Matthew 2; 5; Mark 6-8; 12; Luke 9-12; John 1-3; 14-16")
>>> range_list = BibleRangeList("Mark 3:2-4:5; 1 John 1:5-3 John 8;")
>>> range_list.verse_count()            # Count of verses
161
>>> range_list.chap_count()             # Count of chapters (incl partial)
9
>>> range_list.chap_count(whole=True)   # Count of chapters (whole only)
5
>>> range_list.book_count()             # Count of books (incl partial)
4
>>> range_list.book_count(whole=True)   # Count of books (whole only)
1
```

# Attribution

The set operations and linked-list implementation in this package are derived from
[python-ranges](https://github.com/Superbird11/ranges), under the MIT Licence.

Other ideas in this package were developed from [python-scriptures](https://github.com/davisd/python-scriptures),
under the BSD-3-Clause license.

# Installation

   `pip install bibleref`

# Build Instructions

Use these instructions if you’re building from the source. bibleref has been developed on Python 3.10, but should
work on several earlier versions as well.

1. `git clone https://github.com/multiscript/bibleref/`
1. `cd bibleref`
1. `python3 -m venv venv` (Create a virtual environment.)
   - On Windows: `python -m venv venv`
1. `source venv/bin/activate` (Activate the virtual environment.)
   - In Windows cmd.exe: `venv\Scripts\activate.bat`
   - In Windows powershell: `.\venv\Scripts\Activate.ps1` You may first need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
1. For development work...
   - `pip install -e .` (Creates an editable local install)
1. ...or to build the package:
   - `pip install build`
   - `python -m build`

