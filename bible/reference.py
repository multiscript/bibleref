from enum import Enum, auto
import re

class BibleBook(Enum):
    '''An enum for specifying books in the Bible.

    Note that Python identifiers can't start with a number. So books like
    1 Samuel are written here as _1Sam.

    BibleBooks have the following extra attributes (added in methods below):
      abbrev - The abbreviated name of the book
      title  - The full title of the book.
      regex  - A regex which matches any acceptable name/abbrev of the book.
      index  - An integer indicating its ordering in the collection of books (0-based).
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


name_data = {
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
    BibleBook.Rev:      ("Rev",     "Revelation",       2,   ["The Revelation", "The Revelation to John"])
}

order = [
    BibleBook.Gen,
    BibleBook.Exod,
    BibleBook.Lev,
    BibleBook.Num,
    BibleBook.Deut,
    BibleBook.Josh,
    BibleBook.Judg,
    BibleBook.Ruth,
    BibleBook._1Sam,
    BibleBook._2Sam,
    BibleBook._1Kgs,
    BibleBook._2Kgs,
    BibleBook._1Chr,
    BibleBook._2Chr,
    BibleBook.Ezra,
    BibleBook.Neh,
    BibleBook.Esth,
    BibleBook.Job,
    BibleBook.Psa,
    BibleBook.Prov,
    BibleBook.Eccl,
    BibleBook.Song,
    BibleBook.Isa,
    BibleBook.Jer,
    BibleBook.Lam,
    BibleBook.Ezek,
    BibleBook.Dan,
    BibleBook.Hos,
    BibleBook.Joel,
    BibleBook.Amos,
    BibleBook.Obad,
    BibleBook.Jonah,
    BibleBook.Mic,
    BibleBook.Nah,
    BibleBook.Hab,
    BibleBook.Zeph,
    BibleBook.Hag,
    BibleBook.Zech,
    BibleBook.Mal,
    BibleBook.Matt,
    BibleBook.Mark,
    BibleBook.Luke,
    BibleBook.John,
    BibleBook.Acts,
    BibleBook.Rom,
    BibleBook._1Cor,
    BibleBook._2Cor,
    BibleBook.Gal,
    BibleBook.Eph,
    BibleBook.Phil,
    BibleBook.Col,
    BibleBook._1Thess,
    BibleBook._2Thess,
    BibleBook._1Tim,
    BibleBook._2Tim,
    BibleBook.Titus,
    BibleBook.Phlm,
    BibleBook.Heb,
    BibleBook.James,
    BibleBook._1Pet,
    BibleBook._2Pet,
    BibleBook._1Jn,
    BibleBook._2Jn,
    BibleBook._3Jn,
    BibleBook.Jude,
    BibleBook.Rev
]

max_verses = {
    # Keys: Bible books
    # Values: List of max verse number for each chapter (ascending by chapter). Len of list is number of chapters.
    BibleBook.Gen:      [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26],
    BibleBook.Exod:     [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38],
    BibleBook.Lev:      [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34],
    BibleBook.Num:      [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13],
    BibleBook.Deut:     [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12],
    BibleBook.Josh:     [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33],
    BibleBook.Judg:     [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25],
    BibleBook.Ruth:     [22, 23, 18, 22],
    BibleBook._1Sam:    [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13],
    BibleBook._2Sam:    [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25],
    BibleBook._1Kgs:    [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53],
    BibleBook._2Kgs:    [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30],
    BibleBook._1Chr:    [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30],
    BibleBook._2Chr:    [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23],
    BibleBook.Ezra:     [11, 70, 13, 24, 17, 22, 28, 36, 15, 44],
    BibleBook.Neh:      [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31],
    BibleBook.Esth:     [22, 23, 15, 17, 14, 14, 10, 17, 32, 3],
    BibleBook.Job:      [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17],
    BibleBook.Psa:      [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6],
    BibleBook.Prov:     [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31],
    BibleBook.Eccl:     [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14],
    BibleBook.Song:     [17, 17, 11, 16, 16, 13, 13, 14],
    BibleBook.Isa:      [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24],
    BibleBook.Jer:      [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34],
    BibleBook.Lam:      [22, 22, 66, 22, 22],
    BibleBook.Ezek:     [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35],
    BibleBook.Dan:      [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13],
    BibleBook.Hos:      [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9],
    BibleBook.Joel:     [20, 32, 21],
    BibleBook.Amos:     [15, 16, 15, 13, 27, 14, 17, 14, 15],
    BibleBook.Obad:     [21],
    BibleBook.Jonah:    [17, 10, 10, 11],
    BibleBook.Mic:      [16, 13, 12, 13, 15, 16, 20],
    BibleBook.Nah:      [15, 13, 19],
    BibleBook.Hab:      [17, 20, 19],
    BibleBook.Zeph:     [18, 15, 20],
    BibleBook.Hag:      [15, 23],
    BibleBook.Zech:     [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21],
    BibleBook.Mal:      [14, 17, 18, 6],
    BibleBook.Matt:     [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20],
    BibleBook.Mark:     [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20],
    BibleBook.Luke:     [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53],
    BibleBook.John:     [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25],
    BibleBook.Acts:     [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31],
    BibleBook.Rom:      [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27],
    BibleBook._1Cor:    [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24],
    BibleBook._2Cor:    [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14],
    BibleBook.Gal:      [24, 21, 29, 31, 26, 18],
    BibleBook.Eph:      [23, 22, 21, 32, 33, 24],
    BibleBook.Phil:     [30, 30, 21, 23],
    BibleBook.Col:      [29, 23, 25, 18],
    BibleBook._1Thess:  [10, 20, 13, 18, 28],
    BibleBook._2Thess:  [12, 17, 18],
    BibleBook._1Tim:    [20, 15, 16, 16, 25, 21],
    BibleBook._2Tim:    [18, 26, 17, 22],
    BibleBook.Titus:    [16, 15, 15],
    BibleBook.Phlm:     [25],
    BibleBook.Heb:      [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25],
    BibleBook.James:    [27, 26, 18, 17, 20],
    BibleBook._1Pet:    [25, 25, 22, 19, 14],
    BibleBook._2Pet:    [21, 22, 18],
    BibleBook._1Jn:     [10, 29, 24, 21, 21],
    BibleBook._2Jn:     [13],
    BibleBook._3Jn:     [14],
    BibleBook.Jude:     [25],
    BibleBook.Rev:      [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
}

verse_0s = {
    # Keys: Bible books
    # Values: Set of chapter numbers (1-indexed) that can begin with a verse 0.
     BibleBook.Psa:      set(3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                        28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                        54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 78,
                        79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 98, 100, 101, 102, 103, 108, 109, 110, 120,
                        121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 138, 139, 140, 141, 142,
                        143, 144, 145)
}


def _add_abbrevs_and_titles():
    for book, data in name_data.items():
        book.abbrev = data[0]
        book.title = data[1]

def _add_regexes():
    '''Add a 'regex' attribute to each BibleBook for a regex matching acceptable names.

    For each book, several regex patterns are joined together.
    The main pattern is derived from the book's full title, and requires the min number of unique characters.
    Any characters beyond the minimum are optional, but must be correct.
    Extra patterns are derived from the list of any extra recognised abbreviations.
    '''
    for book, data in name_data.items():
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

def _add_order():
    for i in range(len(order)):
        order[i].index = i


_add_abbrevs_and_titles()
_add_regexes()
_add_order()


if __name__ == "__main__":
    while True:
        s = input("Enter book: ")
        for book in BibleBook:
            match = False
            if book.regex.fullmatch(s) is not None:
                print(book, book.abbrev, book.title, book.index)
                match = True
                break
        if not match:
            print("Not found!")