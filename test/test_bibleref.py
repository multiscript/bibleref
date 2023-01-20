
import unittest

from bibleref import bible_data, BibleRangeList


class TestBibleRef(unittest.TestCase):
    def test_bible_data(self):
        # Save existing characters
        range_sep = bible_data().range_sep
        major_list_sep = bible_data().major_list_sep
        minor_list_sep = bible_data().minor_list_sep
        verse_sep_std = bible_data().verse_sep_std
        verse_sep_alt = bible_data().verse_sep_alt

        range_list_1 = BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")

        # Try using some alternate characters
        bible_data().range_sep = "_"
        bible_data().major_list_sep = "|"
        bible_data().minor_list_sep = "/"
        bible_data().verse_sep_std = ","
        bible_data().verse_sep_alt = "*"

        range_list_2 = BibleRangeList("Mark 3,1_4,2| 5,6_8/ 10| Matt 4")

        self.assertEqual(range_list_1, range_list_2)

        # Restore original characters
        bible_data().range_sep = range_sep
        bible_data().major_list_sep = major_list_sep
        bible_data().minor_list_sep = minor_list_sep
        bible_data().verse_sep_std = verse_sep_std
        bible_data().verse_sep_alt = verse_sep_alt
