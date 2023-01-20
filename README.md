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

