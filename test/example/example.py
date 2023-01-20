from bibleref import *
# Parse a string of Bible ranges...
range_list = BibleRangeList("Mark 2-3:6; 4; 6:1-6, 30-44, 56; Luke 2")
print(range_list)               # Convert back to string
len(range_list)
range_list[0]                   # Indiv ranges from a list
range_list[5].start             # Start and...
range_list[5].end               # ...end verses of a range.
range_list[5].end.book          # Verse attributes
range_list[5].end.chap_num
range_list[5].end.verse_num
len(range_list.groups)
range_list.groups[2]            # Range groups from a list
range_list.groups[2][0]         # Indiv ranges within the group
range_list.groups[2][1]        
range_list.groups[2][2]
BibleVerse('Mark 2:23') + 10    # Verse addition / subtraction
BibleRange('1 John').split(by_chap=True, num_verses=10) # Range splits
for verse in BibleRange('Mark 6:1-3'): 
    print(verse)                # Range iteration

BibleRange('Matt 2:3-John 4:5', flags=BibleFlag.MULTIBOOK) # Multibook ranges
list_1 = BibleRangeList("Matt 2-4; Mark 6-8; Luke 10-12; John 14-16")
list_2 = BibleRangeList("John 1-3; Luke 9-11, 13; Matt 3-5; Mark 12")
list_1 | list_2                 # Union of range lists
list_1 & list_2                 # Intersection range lists
list_1 - list_2                 # Difference of range lists
list_1 ^ list_2                 # Symmetric difference of range lists
