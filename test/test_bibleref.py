
import pytest

from bibleref import bible_data, BibleRangeList


class TestBibleRef:
    def test_bible_data(self):
        bible_data_instance = bible_data()
        assert bible_data_instance is not None
        # Save existing characters
        range_sep = bible_data_instance.range_sep
        major_list_sep = bible_data_instance.major_list_sep
        minor_list_sep = bible_data_instance.minor_list_sep
        verse_sep_std = bible_data_instance.verse_sep_std
        verse_sep_alt = bible_data_instance.verse_sep_alt

        range_list_1 = BibleRangeList("Mark 3:1-4:2; 5:6-8, 10; Matt 4")

        # Try using some alternate characters
        bible_data_instance.range_sep = "_"
        bible_data_instance.major_list_sep = "|"
        bible_data_instance.minor_list_sep = "/"
        bible_data_instance.verse_sep_std = ","
        bible_data_instance.verse_sep_alt = "*"

        range_list_2 = BibleRangeList("Mark 3,1_4,2| 5,6_8/ 10| Matt 4")

        assert range_list_1 == range_list_2

        # Restore original characters
        bible_data_instance.range_sep = range_sep
        bible_data_instance.major_list_sep = major_list_sep
        bible_data_instance.minor_list_sep = minor_list_sep
        bible_data_instance.verse_sep_std = verse_sep_std
        bible_data_instance.verse_sep_alt = verse_sep_alt
