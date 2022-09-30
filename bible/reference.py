from enum import Enum, auto
import re

class BibleBook(Enum):
    '''An enum for specifying books in the Bible.

    Note that Python identifiers can't start with a number. So books like
    1 Samuel are written here as _1Sam.

    BibleBooks have 3 extra attributes:
      abbrev - The abbreviated name of the book
      title  - The full title of the book.
      regex  - A regex which matches any acceptable name/abbrev of the book.
    '''
    Gen = "Genesis" 
    Exod = "Exodus"
    Lev = "Leviticus"
    Num = "Numbers"
    Deut = "Deuteronomy"
    Josh = "Joshua"
    Judg = "Judges"
    Ruth = "Ruth"
    _1Sam = "1 Samuel"
    _2Sam = "2 Samuel"
    _1Kgs = "1 Kings"
    _2Kgs = "2 Kings"
    _1Chr = "1 Chronicles"
    _2Chr = "2 Chronicles"
    Ezra = "Ezra"
    Neh = "Nehemiah"
    Esth = "Esther"
    Job = "Job"
    Psa = "Psalms"
    Prov = "Proverbs"
    Eccl = "Ecclesiastes"
    Song = "Song of Songs"
    Isa = "Isaiah"
    Jer = "Jeremiah"
    Lam = "Lamentations"
    Ezek = "Ezekiel"
    Dan = "Daniel"
    Hos = "Hosea"
    Joel = "Joel"
    Amos = "Amos"
    Obad = "Obadiah"
    Jonah = "Jonah"
    Mic = "Micah"
    Nah = "Nahum"
    Hab = "Habakkuk"
    Zeph = "Zephaniah"
    Hag = "Haggai"
    Zech = "Zechariah"
    Mal = "Malachi"
    Matt = "Matthew"
    Mark = "Mark"
    Luke = "Luke"
    John = "John"
    Acts = "Acts"
    Rom = "Romans"
    _1Cor = "1 Corinthians"
    _2Cor = "2 Corinthians"
    Gal = "Galatians"
    Eph = "Ephesians"
    Phil = "Philippians"
    Col = "Colossians"
    _1Thess = "1 Thessalonians"
    _2Thess = "2 Thessalonians"
    _1Tim = "1 Timothy"
    _2Tim = "2 Timothy"
    Titus = "Titus"
    Phlm = "Philemon"
    Heb = "Hebrews"
    James = "James"
    _1Pet = "1 Peter"
    _2Pet = "2 Peter"
    _1Jn = "1 John"
    _2Jn = "2 John"
    _3Jn = "3 John"
    Jude = "Jude"
    Rev = "Revelation"


bible_book_names = {
    # Keys: Bible Book
    # Values: (Abbrev title, Full title, Min unique chars (excl. numbers), List of extra recognised abbrevs)
    #
    # The min unique chars is the minimum number of characters in the full title (after any initial "1 ",
    # "2 " or "3 " has been stripped out) needed to uniquely identify the book.
    #
    BibleBook.Gen:      ("Gen",     "Genesis",          2,   ["Gn"]),
    BibleBook.Exod:     ("Exod",    "Exodus",           2,   []),
    BibleBook.Lev:      ("Lev",     "Leviticus",        2,   ["Lv"]),
    BibleBook.Num:      ("Num",     "Numbers",          2,   ["Nm", "Nb"]),
    BibleBook.Deut:     ("Deut",    "Deuteronomy",      2,   ["Dt"]),
    BibleBook.Josh:     ("Josh",    "Joshua",           3,   ["Js", "Jsh"]),
    BibleBook.Judg:     ("Judg",    "Judges",           4,   ["Jg", "Jdg", "Jdgs"]),
    BibleBook.Ruth:     ("Ruth",    "Ruth",             2,   ["Ruth"]),
    BibleBook._1Sam:    ("1Sam",    "1 Samuel",         1,   ["1 Sm"]),
    BibleBook._2Sam:    ("2Sam",    "2 Samuel",         1,   ["2 Sm"]),
    BibleBook._1Kgs:    ("1Kgs",    "1 Kings",          1,   ["1 Kg", "1 Kgs"]),
    BibleBook._2Kgs:    ("2Kgs",    "2 Kings",          1,   ["2 Kg", "2 Kgs"]),
    BibleBook._1Chr:    ("1Chr",    "1 Chronicles",     2,   []),
    BibleBook._2Chr:    ("2Chr",    "2 Chronicles",     2,   []),
    BibleBook.Ezra:     ("Ezra",    "Ezra",             3,   []),
    BibleBook.Neh:      ("Neh",     "Nehemiah",         2,   []),
    BibleBook.Esth:     ("Esth",    "Esther",           2,   []),
    BibleBook.Job:      ("Job",     "Job",              3,   ["Jb"]),
    BibleBook.Psa:      ("Psa",     "Psalms",           2,   ["Pslm", "Psm", "Pss"]),
    BibleBook.Prov:     ("Prov",    "Proverbs",         2,   ["Prv"]),
    BibleBook.Eccl:     ("Eccl",    "Ecclesiastes",     2,   []),
    BibleBook.Song:     ("Song",    "Song of Songs",    2,   ["Song of Sol", "Song of Solo", "Song of Solomon", "SOS"]),
    BibleBook.Isa:      ("Isa",     "Isaiah",           2,   []),
    BibleBook.Jer:      ("Jer",     "Jeremiah",         2,   ["Jr"]),
    BibleBook.Lam:      ("Lam",     "Lamentations",     2,   []),
    BibleBook.Ezek:     ("Ezek",    "Ezekiel",          3,   ["Ezk"]),
    BibleBook.Dan:      ("Dan",     "Daniel",           2,   ["Dn"]),
    BibleBook.Hos:      ("Hos",     "Hosea",            2,   []),
    BibleBook.Joel:     ("Joel",    "Joel",             3,   ["Jl"]),
    BibleBook.Amos:     ("Amos",    "Amos",             2,   []),
    BibleBook.Obad:     ("Obad",    "Obadiah",          2,   ["Obd"]),
    BibleBook.Jonah:    ("Jonah",   "Jonah",            3,   ["Jnh"]),
    BibleBook.Mic:      ("Mic",     "Micah",            2,   ["Mc"]),
    BibleBook.Nah:      ("Nah",     "Nahum",            2,   []),
    BibleBook.Hab:      ("Hab",     "Habakkuk",         3,   ["Hbk"]),
    BibleBook.Zeph:     ("Zeph",    "Zephaniah",        3,   ["Zp", "Zph"]),
    BibleBook.Hag:      ("Hag",     "Haggai",           3,   ["Hg"]),
    BibleBook.Zech:     ("Zech",    "Zechariah",        3,   ["Zc"]),
    BibleBook.Mal:      ("Mal",     "Malachi",          3,   ["Ml"]),
    BibleBook.Matt:     ("Matt",    "Matthew",          3,   ["Mt"]),
    BibleBook.Mark:     ("Mark",    "Mark",             3,   ["Mk", "Mrk"]),
    BibleBook.Luke:     ("Luke",    "Luke",             2,   ["Lk"]),
    BibleBook.John:     ("John",    "John",             3,   ["Jn", "Jhn"]),
    BibleBook.Acts:     ("Acts",    "Acts",             2,   []),
    BibleBook.Rom:      ("Rom",     "Romans",           2,   ["Rm"]),
    BibleBook._1Cor:    ("1Cor",    "1 Corinthians",    2,   []),
    BibleBook._2Cor:    ("2Cor",    "2 Corinthians",    2,   []),
    BibleBook.Gal:      ("Gal",     "Galatians",        2,   []),
    BibleBook.Eph:      ("Eph",     "Ephesians",        2,   []),
    BibleBook.Phil:     ("Phil",    "Philippians",      5,   ["Pp", "Php"]),
    BibleBook.Col:      ("Col",     "Colossians",       2,   []),
    BibleBook._1Thess:  ("1Thess",  "1 Thessalonians",  2,   ["1 Ths"]),
    BibleBook._2Thess:  ("2Thess",  "2 Thessalonians",  2,   ["2 Ths"]),
    BibleBook._1Tim:    ("1Tim",    "1 Timothy",        2,   []),
    BibleBook._2Tim:    ("2Tim",    "2 Timothy",        2,   []),
    BibleBook.Titus:    ("Titus",   "Titus",            2,   []),
    BibleBook.Phlm:     ("Phlm",    "Philemon",         5,   ["Pm", "Phm"]),
    BibleBook.Heb:      ("Heb",     "Hebrews",          2,   []),
    BibleBook.James:    ("James",   "James",            2,   ["Jm", "Jas"]),
    BibleBook._1Pet:    ("1Pet",    "1 Peter",          1,   ["1 Pt"]),
    BibleBook._2Pet:    ("2Pet",    "2 Peter",          1,   ["2 Pt"]),
    BibleBook._1Jn:     ("1Jn",     "1 John",           1,   ["1 Jn", "1 Jhn"]),
    BibleBook._2Jn:     ("2Jn",     "2 John",           1,   ["2 Jn", "2 Jhn"]),
    BibleBook._3Jn:     ("3Jn",     "3 John",           1,   ["3 Jn", "3 Jhn"]),
    BibleBook.Jude:     ("Jude",    "Jude",             4,   []),
    BibleBook.Rev:      ("Rev",     "Revelation",       2,   ["The Revelation", "The Revelation to John"]),
}


def _add_abbrevs_and_titles():
    for book, data in bible_book_names.items():
        book.abbrev = data[0]
        book.title = data[1]

def _add_regexes():
    '''Add a 'regex' attribute to each BibleBook for a regex matching acceptable names.

    For each book, several regex patterns are joined together.
    The main pattern is derived from the book's full title, and requires the min number of unique characters.
    Any characters beyond the minimum are optional, but must be correct.
    Extra patterns are derived from the list of any extra recognised abbreviations.
    '''
    for book, data in bible_book_names.items():
        # For clarity, the comments show what happens for the example of "1 John"
        full_title = data[1]    # e.g. "1 John"
        min_chars = data[2]     # e.g. 1
        extra_abbrevs = data[3] #
        full_title_pattern = ""

        # Peel off any numeric prefix, and match variations on the prefix.
        # e.g. full_title_pattern = r"(1|I)\s*"
        #      full_title = "John"
        if full_title[0:2] == "1 " or full_title[0:2] == "2 " or full_title[0:2] == "3 ":
            full_title_pattern = full_title[0:2]
            full_title_pattern = full_title_pattern.replace("1 ", r"(1|I)\s*") 
            full_title_pattern = full_title_pattern.replace("2 ", r"(2|II)\s*")
            full_title_pattern = full_title_pattern.replace("3 ", r"(3|III)\s*")
            full_title = full_title[2:]
        
        # Add the minimum number of unique characters
        # e.g. full_title_pattern = r"(1|I)\s*J"
        full_title_pattern += full_title[0:min_chars]

        # Add the rest of full title characters as optional matches.
        # e.g. full_title_pattern = r"(1|I)\s*J(o(h(n)?)?)?"
        for char in full_title[min_chars:]:
            full_title_pattern += "(" + char
        full_title_pattern += ")?" * (len(full_title)-min_chars)

        # Allow for extra whitespace.
        full_title_pattern = full_title_pattern.replace(" ",r"\s+")

        # Collate the extra acceptable abbreviations, and combine everything into a final,
        # single regex for the book
        total_pattern = full_title_pattern
        for abbrev in extra_abbrevs:
            abbrev = abbrev.replace(" ",r"\s+") # Allow for extra whitespace
            total_pattern += "|" + abbrev
        book.regex = re.compile(total_pattern, re.IGNORECASE)


_add_abbrevs_and_titles()
_add_regexes()


if __name__ == "__main__":
    while True:
        s = input("Enter book: ")
        for book in BibleBook:
            match = False
            if book.regex.fullmatch(s):
                print(book, book.abbrev, book.title)
                match = True
                break
        if not match:
            print("Not found!")