from enum import Enum, auto


class BibleBook(Enum):
    '''An enum for specifying books in the Bible.

    Note that Python identifiers can't start with a number. So books like
    1 Samuel are written here as _1Sam . The enum name (minus any _)
    becomes the book abbreviation, while the enum value becomes the full
    book title.
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

    @property
    def abbrev(self):
        '''Abbreviated book name
        '''
        abbrev = self.name
        if abbrev[0] == "_":
            abbrev = abbrev[1:]
        return abbrev

    @property
    def title(self):
        '''Full book name
        '''
        return self.value


bible_book_names = {
    # Keys: Bible Book
    # Values: (Abbrev title, Full title, Min unique chars (excl. numbers), List of extra recognised abbrevs)
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