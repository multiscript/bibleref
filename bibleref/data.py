
from . import ref


range_sep           = "-"
'''Range separator character used to separate start and end of a Bible range.'''

major_list_sep      = ";"
'''Major list separator character.

Separates Bible ranges in different groups. Usually separates ranges in different chapters.'''

minor_list_sep      = ","
'''Minor list separator character.

Separates Bible ranges in the same group. Usually separates ranges in the same chapter.'''

verse_sep_std  = ":"
'''Standard verse separator character, used to separate chapter and verse numbers'''

verse_sep_alt   = "."
'''Alternate verse separator character, used to separate chapter and verse numbers'''

book_order = []
'''
List of Bible books in their sort order.
'''


default_book_order = [
    ref.BibleBook.Gen,
    ref.BibleBook.Exod,
    ref.BibleBook.Lev,
    ref.BibleBook.Num,
    ref.BibleBook.Deut,
    ref.BibleBook.Josh,
    ref.BibleBook.Judg,
    ref.BibleBook.Ruth,
    ref.BibleBook.ISam,
    ref.BibleBook.IISam,
    ref.BibleBook.IKgs,
    ref.BibleBook.IIKgs,
    ref.BibleBook.IChr,
    ref.BibleBook.IIChr,
    ref.BibleBook.Ezra,
    ref.BibleBook.Neh,
    ref.BibleBook.Esth,
    ref.BibleBook.Job,
    ref.BibleBook.Psa,
    ref.BibleBook.Prov,
    ref.BibleBook.Eccl,
    ref.BibleBook.Song,
    ref.BibleBook.Isa,
    ref.BibleBook.Jer,
    ref.BibleBook.Lam,
    ref.BibleBook.Ezek,
    ref.BibleBook.Dan,
    ref.BibleBook.Hos,
    ref.BibleBook.Joel,
    ref.BibleBook.Amos,
    ref.BibleBook.Obad,
    ref.BibleBook.Jonah,
    ref.BibleBook.Mic,
    ref.BibleBook.Nah,
    ref.BibleBook.Hab,
    ref.BibleBook.Zeph,
    ref.BibleBook.Hag,
    ref.BibleBook.Zech,
    ref.BibleBook.Mal,
    ref.BibleBook.Matt,
    ref.BibleBook.Mark,
    ref.BibleBook.Luke,
    ref.BibleBook.John,
    ref.BibleBook.Acts,
    ref.BibleBook.Rom,
    ref.BibleBook.ICor,
    ref.BibleBook.IICor,
    ref.BibleBook.Gal,
    ref.BibleBook.Eph,
    ref.BibleBook.Phil,
    ref.BibleBook.Col,
    ref.BibleBook.ITh,
    ref.BibleBook.IITh,
    ref.BibleBook.ITim,
    ref.BibleBook.IITim,
    ref.BibleBook.Titus,
    ref.BibleBook.Phlm,
    ref.BibleBook.Heb,
    ref.BibleBook.Jam,
    ref.BibleBook.IPet,
    ref.BibleBook.IIPet,
    ref.BibleBook.IJn,
    ref.BibleBook.IIJn,
    ref.BibleBook.IIIJn,
    ref.BibleBook.Jude,
    ref.BibleBook.Rev
]
'''
Default list of Bible books in their sort order.
'''


default_name_data = {
    ref.BibleBook.Gen:      ("Gen",     "Genesis",          2,   ["Gn"]),
    ref.BibleBook.Exod:     ("Exod",    "Exodus",           2,   []),
    ref.BibleBook.Lev:      ("Lev",     "Leviticus",        2,   ["Lv"]),
    ref.BibleBook.Num:      ("Num",     "Numbers",          2,   ["Nm", "Nb"]),
    ref.BibleBook.Deut:     ("Deut",    "Deuteronomy",      2,   ["Dt"]),
    ref.BibleBook.Josh:     ("Josh",    "Joshua",           3,   ["Js", "Jsh"]),
    ref.BibleBook.Judg:     ("Judg",    "Judges",           4,   ["Jg", "Jdg", "Jdgs"]),
    ref.BibleBook.Ruth:     ("Ruth",    "Ruth",             2,   ["Ruth"]),
    ref.BibleBook.ISam:     ("1Sam",    "1 Samuel",         1,   ["1 Sm"]),
    ref.BibleBook.IISam:    ("2Sam",    "2 Samuel",         1,   ["2 Sm"]),
    ref.BibleBook.IKgs:     ("1Kgs",    "1 Kings",          1,   ["1 Kg", "1 Kgs"]),
    ref.BibleBook.IIKgs:    ("2Kgs",    "2 Kings",          1,   ["2 Kg", "2 Kgs"]),
    ref.BibleBook.IChr:     ("1Chr",    "1 Chronicles",     2,   []),
    ref.BibleBook.IIChr:    ("2Chr",    "2 Chronicles",     2,   []),
    ref.BibleBook.Ezra:     ("Ezra",    "Ezra",             3,   []),
    ref.BibleBook.Neh:      ("Neh",     "Nehemiah",         2,   []),
    ref.BibleBook.Esth:     ("Esth",    "Esther",           2,   []),
    ref.BibleBook.Job:      ("Job",     "Job",              3,   ["Jb"]),
    ref.BibleBook.Psa:      ("Psa",     "Psalms",           2,   ["Pslm", "Psm", "Pss"]),
    ref.BibleBook.Prov:     ("Prov",    "Proverbs",         2,   ["Prv"]),
    ref.BibleBook.Eccl:     ("Eccl",    "Ecclesiastes",     2,   []),
    ref.BibleBook.Song:     ("Song",    "Song of Songs",    2,   ["Song of Sol", "Song of Solo", "Song of Solomon", "SOS"]),
    ref.BibleBook.Isa:      ("Isa",     "Isaiah",           2,   []),
    ref.BibleBook.Jer:      ("Jer",     "Jeremiah",         2,   ["Jr"]),
    ref.BibleBook.Lam:      ("Lam",     "Lamentations",     2,   []),
    ref.BibleBook.Ezek:     ("Ezek",    "Ezekiel",          3,   ["Ezk"]),
    ref.BibleBook.Dan:      ("Dan",     "Daniel",           2,   ["Dn"]),
    ref.BibleBook.Hos:      ("Hos",     "Hosea",            2,   []),
    ref.BibleBook.Joel:     ("Joel",    "Joel",             3,   ["Jl"]),
    ref.BibleBook.Amos:     ("Amos",    "Amos",             2,   []),
    ref.BibleBook.Obad:     ("Obad",    "Obadiah",          2,   ["Obd"]),
    ref.BibleBook.Jonah:    ("Jonah",   "Jonah",            3,   ["Jnh"]),
    ref.BibleBook.Mic:      ("Mic",     "Micah",            2,   ["Mc"]),
    ref.BibleBook.Nah:      ("Nah",     "Nahum",            2,   []),
    ref.BibleBook.Hab:      ("Hab",     "Habakkuk",         3,   ["Hbk"]),
    ref.BibleBook.Zeph:     ("Zeph",    "Zephaniah",        3,   ["Zp", "Zph"]),
    ref.BibleBook.Hag:      ("Hag",     "Haggai",           3,   ["Hg"]),
    ref.BibleBook.Zech:     ("Zech",    "Zechariah",        3,   ["Zc"]),
    ref.BibleBook.Mal:      ("Mal",     "Malachi",          3,   ["Ml"]),
    ref.BibleBook.Matt:     ("Matt",    "Matthew",          3,   ["Mt"]),
    ref.BibleBook.Mark:     ("Mark",    "Mark",             3,   ["Mk", "Mrk"]),
    ref.BibleBook.Luke:     ("Luke",    "Luke",             2,   ["Lk"]),
    ref.BibleBook.John:     ("John",    "John",             3,   ["Jn", "Jhn"]),
    ref.BibleBook.Acts:     ("Acts",    "Acts",             2,   []),
    ref.BibleBook.Rom:      ("Rom",     "Romans",           2,   ["Rm"]),
    ref.BibleBook.ICor:     ("1Cor",    "1 Corinthians",    2,   []),
    ref.BibleBook.IICor:    ("2Cor",    "2 Corinthians",    2,   []),
    ref.BibleBook.Gal:      ("Gal",     "Galatians",        2,   []),
    ref.BibleBook.Eph:      ("Eph",     "Ephesians",        2,   []),
    ref.BibleBook.Phil:     ("Phil",    "Philippians",      4,   ["Pp", "Php"]), # Phil acceptable abbrev
    ref.BibleBook.Col:      ("Col",     "Colossians",       2,   []),
    ref.BibleBook.ITh:   ("1Thess",  "1 Thessalonians",  2,   ["1 Ths"]),
    ref.BibleBook.IITh:  ("2Thess",  "2 Thessalonians",  2,   ["2 Ths"]),
    ref.BibleBook.ITim:     ("1Tim",    "1 Timothy",        2,   []),
    ref.BibleBook.IITim:    ("2Tim",    "2 Timothy",        2,   []),
    ref.BibleBook.Titus:    ("Titus",   "Titus",            2,   []),
    ref.BibleBook.Phlm:     ("Phlm",    "Philemon",         5,   ["Pm", "Phm", "Phlm"]), # Phil not acceptable abbrev
    ref.BibleBook.Heb:      ("Heb",     "Hebrews",          2,   []),
    ref.BibleBook.Jam:    ("James",   "James",            2,   ["Jm", "Jas"]),
    ref.BibleBook.IPet:     ("1Pet",    "1 Peter",          1,   ["1 Pt"]),
    ref.BibleBook.IIPet:    ("2Pet",    "2 Peter",          1,   ["2 Pt"]),
    ref.BibleBook.IJn:      ("1Jn",     "1 John",           1,   ["1 Jn", "1 Jhn"]),
    ref.BibleBook.IIJn:     ("2Jn",     "2 John",           1,   ["2 Jn", "2 Jhn"]),
    ref.BibleBook.IIIJn:    ("3Jn",     "3 John",           1,   ["3 Jn", "3 Jhn"]),
    ref.BibleBook.Jude:     ("Jude",    "Jude",             4,   []),
    ref.BibleBook.Rev:      ("Rev",     "Revelation",       2,   ["The Revelation", "The Revelation to John"])
}
'''
Keys: Bible Book
Values: (Abbrev title, Full title, Min unique chars (excl. numbers), List of extra recognised abbrevs)

The min unique chars is the minimum number of characters in the full title (after any initial "1 ",
"2 " or "3 " has been stripped out) needed to uniquely identify the book.
'''


default_max_verses = {
    ref.BibleBook.Gen:      [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26],
    ref.BibleBook.Exod:     [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38],
    ref.BibleBook.Lev:      [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34],
    ref.BibleBook.Num:      [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13],
    ref.BibleBook.Deut:     [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12],
    ref.BibleBook.Josh:     [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33],
    ref.BibleBook.Judg:     [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25],
    ref.BibleBook.Ruth:     [22, 23, 18, 22],
    ref.BibleBook.ISam:     [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13],
    ref.BibleBook.IISam:    [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25],
    ref.BibleBook.IKgs:     [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53],
    ref.BibleBook.IIKgs:    [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30],
    ref.BibleBook.IChr:     [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30],
    ref.BibleBook.IIChr:    [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23],
    ref.BibleBook.Ezra:     [11, 70, 13, 24, 17, 22, 28, 36, 15, 44],
    ref.BibleBook.Neh:      [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31],
    ref.BibleBook.Esth:     [22, 23, 15, 17, 14, 14, 10, 17, 32, 3],
    ref.BibleBook.Job:      [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17],
    ref.BibleBook.Psa:      [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6],
    ref.BibleBook.Prov:     [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31],
    ref.BibleBook.Eccl:     [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14],
    ref.BibleBook.Song:     [17, 17, 11, 16, 16, 13, 13, 14],
    ref.BibleBook.Isa:      [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24],
    ref.BibleBook.Jer:      [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34],
    ref.BibleBook.Lam:      [22, 22, 66, 22, 22],
    ref.BibleBook.Ezek:     [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35],
    ref.BibleBook.Dan:      [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13],
    ref.BibleBook.Hos:      [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9],
    ref.BibleBook.Joel:     [20, 32, 21],
    ref.BibleBook.Amos:     [15, 16, 15, 13, 27, 14, 17, 14, 15],
    ref.BibleBook.Obad:     [21],
    ref.BibleBook.Jonah:    [17, 10, 10, 11],
    ref.BibleBook.Mic:      [16, 13, 12, 13, 15, 16, 20],
    ref.BibleBook.Nah:      [15, 13, 19],
    ref.BibleBook.Hab:      [17, 20, 19],
    ref.BibleBook.Zeph:     [18, 15, 20],
    ref.BibleBook.Hag:      [15, 23],
    ref.BibleBook.Zech:     [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21],
    ref.BibleBook.Mal:      [14, 17, 18, 6],
    ref.BibleBook.Matt:     [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20],
    ref.BibleBook.Mark:     [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20],
    ref.BibleBook.Luke:     [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53],
    ref.BibleBook.John:     [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25],
    ref.BibleBook.Acts:     [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31],
    ref.BibleBook.Rom:      [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27],
    ref.BibleBook.ICor:     [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24],
    ref.BibleBook.IICor:    [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14],
    ref.BibleBook.Gal:      [24, 21, 29, 31, 26, 18],
    ref.BibleBook.Eph:      [23, 22, 21, 32, 33, 24],
    ref.BibleBook.Phil:     [30, 30, 21, 23],
    ref.BibleBook.Col:      [29, 23, 25, 18],
    ref.BibleBook.ITh:      [10, 20, 13, 18, 28],
    ref.BibleBook.IITh:     [12, 17, 18],
    ref.BibleBook.ITim:     [20, 15, 16, 16, 25, 21],
    ref.BibleBook.IITim:    [18, 26, 17, 22],
    ref.BibleBook.Titus:    [16, 15, 15],
    ref.BibleBook.Phlm:     [25],
    ref.BibleBook.Heb:      [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25],
    ref.BibleBook.Jam:      [27, 26, 18, 17, 20],
    ref.BibleBook.IPet:     [25, 25, 22, 19, 14],
    ref.BibleBook.IIPet:    [21, 22, 18],
    ref.BibleBook.IJn:      [10, 29, 24, 21, 21],
    ref.BibleBook.IIJn:     [13],
    ref.BibleBook.IIIJn:    [14],
    ref.BibleBook.Jude:     [25],
    ref.BibleBook.Rev:      [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
}
'''
Keys: Bible books
Values: List of max verse number for each chapter (ascending by chapter). Len of list is number of chapters.
'''


default_verse_0s = {
    ref.BibleBook.Psa:  set([3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                        28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                        54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 78,
                        79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 98, 100, 101, 102, 103, 108, 109, 110, 120,
                        121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 138, 139, 140, 141, 142,
                        143, 144, 145])
}
'''
Keys: Bible books
Values: Set of chapter numbers (1-indexed) that can begin with a verse 0.
'''