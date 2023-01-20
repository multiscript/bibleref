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
>>> from bibleref import *
>>> # Parse a string of Bible ranges...
>>> range_list = BibleRangeList("Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2")
>>> print(range_list)               # Convert back to string
Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2
>>> len(range_list)
6
>>> range_list[0]                   # Indiv ranges from a list
BibleRange(Mark 2-3:6)
>>> range_list[5].start             # Start and...
BibleVerse(Luke 2:1)
>>> range_list[5].end               # ...end verses of a range.
BibleVerse(Luke 2:52)
>>> range_list[5].end.book          # Verse attributes
<BibleBook.Luke: 'Luke'>
>>> range_list[5].end.chap_num
2
>>> range_list[5].end.verse_num
52
>>> len(range_list.groups)
4
>>> range_list.groups[2]            # Range groups from a list
GroupView([BibleRange(Mark 6:1-6), BibleRange(Mark 6:30-44), BibleRange(Mark 6:56)])
>>> range_list.groups[2][0]         # Indiv ranges within the group
BibleRange(Mark 6:1-6)
>>> range_list.groups[2][1]        
BibleRange(Mark 6:30-44)
>>> range_list.groups[2][2]
BibleRange(Mark 6:56)
>>> BibleVerse('Mark 2:23') + 10    # Verse addition / subtraction
BibleVerse(Mark 3:5)
>>> BibleRange('1 John').split(by_chap=True, num_verses=10) # Range splits
BibleRangeList("1 John 1, 2:1-10, 11-20, 21-29, 3:1-10, 11-20, 21-24, 4:1-10, 11-20, 21, 5:1-10, 11-20, 21")
>>> for verse in BibleRange('Mark 6:1-3'): 
...     print(verse)                # Range iteration
... 
Mark 6:1
Mark 6:2
Mark 6:3
>>> BibleRange('Matt 2:3-John 4:5', flags=BibleFlag.MULTIBOOK) # Multibook ranges
BibleRange(Matthew 2:3-John 4:5)
>>> list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
>>> list_2 = BibleRangeList("John 1-3; Luke 9-11, 13; Matt 3-5; Mark 12")
>>> list_1 | list_2                 # Union of range lists
BibleRangeList("Matthew 2-5, Mark 6-8, 12, Luke 9-13, John 1-3, 14-16")
>>> list_1 & list_2                 # Intersection range lists
BibleRangeList("Matthew 3-4, Luke 10-11")
>>> list_1 - list_2                 # Difference of range lists
BibleRangeList("Matthew 2, Mark 6-8, Luke 12, John 14-16")
>>> list_1 ^ list_2                 # Symmetric difference of range lists
BibleRangeList("Matthew 2, 5, Mark 6-8, 12, Luke 9, 12-13, John 1-3, 14-16")
```

# Build Instructions

Use these instructions if you’re building from the source. bibleref has been developed on Python 3.10, but should
work on earlier versions as well.

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

