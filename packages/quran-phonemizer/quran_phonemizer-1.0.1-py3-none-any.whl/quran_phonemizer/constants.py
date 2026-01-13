# Mapping Arabic Uthmani characters to phonetic representation
CONSONANT_MAP = {
    'ء': '2',   'آ': '2aa', 'أ': '2',   'ؤ': '2',   'إ': '2',   'ئ': '2',
    'ا': 'aa',  'ب': 'b',   'ت': 't',   'ث': 'th',  'ج': 'j',   'ح': 'H',
    'خ': 'kh',  'د': 'd',   'ذ': 'dh',  'ر': 'r',   'ز': 'z',   'س': 's',
    'ش': 'sh',  'ص': 'S',   'ض': 'D',   'ط': 'T',   'ظ': 'Z',   'ع': '3',
    'غ': 'gh',  'ف': 'f',   'ق': 'q',   'ك': 'k',   'ل': 'l',   'م': 'm',
    'ن': 'n',   'ه': 'h',   'و': 'w',   'ى': 'aa',  'ي': 'y',   'ة': 't',
    'ٱ': '',    'ٰ': 'aa',   'ۥ': 'uu',   'ۦ': 'ii',
}

DIACRITIC_MAP = {
    '\u064E': 'a', '\u064F': 'u', '\u0650': 'i',
    '\u064B': 'an', '\u064C': 'un', '\u064D': 'in',
    '\u0651': '', '\u0652': '',
}

# Formal Inventory for ML Training (VITS/FastSpeech Compatible)
# Removed 'an', 'in', 'un' to force atomic splitting (e.g. 'a', 'n')
ATOMIC_TOKEN_MAP = {
    ":::": "M3",  # Madd 6 counts
    "::":  "M2",  # Madd 4 counts
    ":":   "M1",  # Madd 2 counts
    "_Q":  "QK",  # Qalqalah
    "ŋ":   "GN",  # Ghunnah
    "LL":  "L_H", # Heavy Lam
    "RR":  "R_H", # Heavy Ra
    "sh": "sh", "th": "th", "kh": "kh", "gh": "gh", "dh": "dh",
    "aa": "aa", "ii": "ii", "uu": "uu",
    "2": "2", "3": "3", "H": "H", "S": "S", "D": "D", "T": "T", "Z": "Z", "R": "R",
    "a": "a", "i": "i", "u": "u", "b": "b", "t": "t", "j": "j", "d": "d", "r": "r",
    "z": "z", "s": "s", "f": "f", "q": "q", "k": "k", "l": "l", "m": "m", "n": "n", "h": "h", "w": "w", "y": "y"
}

MUQATTAAT_MAP = {
    "الم": "2alif laa:::m mii:::m",
    "حم": "Haa mii:::m",
    "طه": "Taa haa",
    "يس": "yaa sii:::n",
    "ص": "Saa:::d",
    "ق": "qaa:::f",
    "ن": "nuu:::n"
}