import bibleref
from bibleref import *
                            # Parse from string
range_list = BibleRangeList("Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2")
print(range_list)           # Convert back to a string
len(range_list)
range_list[0]               # Individual ranges from a list
range_list[1]
range_list[5].start         # Start and...
range_list[5].end           # ...end verses of a range.
range_list[5].end.book      # Verse attributes
range_list[5].end.chap_num
range_list[5].end.verse_num
len(range_list.groups)
range_list.groups[2]        # Indivdual range groups from a list
range_list.groups[2][0]     # Individual ranges within the group
range_list.groups[2][1]        
range_list.groups[2][2]
BibleVerse('Mark 2:23') + 10 # Verse addition / subtraction
BibleVerse('Mark 3:5') - BibleVerse('Mark 2:23')
BibleRange('1 John').split(by_chap=True, num_verses=15) # Range splits
for verse in BibleRange('Mark 6:1-3'): # Range iteration
    print(verse)

bibleref.flags = BibleFlag.MULTIBOOK   # Enable multi-book ranges
BibleRange('Matt 10-John 10')
list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
list_2 = BibleRangeList("John 1-3; Luke 9; Matt 3-5; Mark 12")
list_1 | list_2                     # Union
list_1 & list_2                     # Intersection
list_1 - list_2                     # Difference
list_1 ^ list_2                     # Symmetric difference
range_list = BibleRangeList("Mark 3:2-4:5; 1 John 1:5-3 John 8;")
range_list.verse_count()            # Count of verses
range_list.chap_count()             # Count of chapters (incl partial)
range_list.chap_count(whole=True)   # Count of chapters (whole only)
range_list.book_count()             # Count of books (incl partial)
range_list.book_count(whole=True)   # Count of books (whole only)
