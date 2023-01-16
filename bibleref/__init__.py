'''
# Overview

**bibleref is a package for manipulating references to Bible books, verses and verse-ranges, including parsing and
string conversion.** It's designed for future use with [Multiscript](https://multiscript.app), but it can be used
as a standalone package. Its only dependency is the [Lark](https://github.com/lark-parser/lark) parsing toolkit.

`bibleref` defines the following primary classes:
  - `bibleref.ref.BibleBook`:      An Enum of books in the Bible, with extra methods.
  - `bibleref.ref.BibleVerse`:     A reference to a single Bible verse (e.g. Matt 2:3)
  - `bibleref.ref.BibleRange`:     A reference to a continuous range of Bible verses (e.g. Matt 2:3-4:5)
  - `bibleref.ref.BibleRangeList`: A specialised list of `BibleRange`s, allowing for grouping and
  set-style operations.

(There is no `BibleChapter` class, as chapters are usually best handled as a `BibleRange`.)

Each of these classes can also be directly imported from `bibleref`.

# Data

The Bible book, chapter and verse data is specified in the `bibleref.data` sub-module.

# Global Flags
 
The global attribute `bibleref.ref.flags` is a `bibleref.ref.BibleFlag` enum whose elements control
package-wide behaviour. Many methods take a `flags` keyword-argument that overrides the global `flags` attribute
during the execution of that method.

The effect of each flag is as follows:

### `bibleref.ref.BibleFlag.MULTIBOOK`

Defaults to unset. When set, `BibleRange`s can be constructed that span multiple books. Existing multibook ranges
behave correctly even when `MULTIBOOK` is unset.

### `bibleref.ref.BibleFlag.VERSE_0`

Defaults to unset. When set, BibleVerses can be constructed where the first verse number of some chapters is 0, not
1. (This is currently just the Psalms that have superscriptions.) When you need to mix references that do or don't
allow for verse 0, it may be easier to choose one value for all your code, and then use the `verse_0_to_1()` and
`verse_1_to_0()` methods on `BibleVerse`s, `BibleRange`s and `BibleRangeList`s as necessary.


'''
from .ref import BibleBook, BibleFlag, BibleRange, BibleRangeList, BibleRef, BibleVerse, BibleVersePart
