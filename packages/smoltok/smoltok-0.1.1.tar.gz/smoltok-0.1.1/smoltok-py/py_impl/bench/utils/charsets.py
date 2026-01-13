import string
from typing import Final

# Character sets for different languages/scripts
CHARSET_ASCII: Final[str] = string.printable

# Latin extended - https://en.wikipedia.org/wiki/Latin-1_Supplement + https://en.wikipedia.org/wiki/Latin_Extended-A
CHARSET_LATIN_WITH_DIACRITICS: Final[str] = "".join(chr(c) for c in range(0x00C0, 0x0180))

# Cyrillic - https://en.wikipedia.org/wiki/Cyrillic_%28Unicode_block%29
CHARSET_CYRILLIC: Final[str] = "".join(chr(c) for c in range(0x0400, 0x0500))

# Greek - https://en.wikipedia.org/wiki/Greek_and_Coptic
CHARSET_GREEK: Final[str] = "".join(chr(c) for c in range(0x0370, 0x0400))

# Arabic - https://en.wikipedia.org/wiki/Arabic_%28Unicode_block%29
CHARSET_ARABIC: Final[str] = "".join(chr(c) for c in range(0x0600, 0x0700))

# Chinese subset - https://en.wikipedia.org/wiki/CJK_Unified_Ideographs
CHARSET_CHINESE: Final[str] = "".join(chr(c) for c in range(0x4E00, 0x4F00))  # first 256 common chars

# Japanese Hiragana  + Katakana
# https://en.wikipedia.org/wiki/Hiragana_%28Unicode_block%29 + https://en.wikipedia.org/wiki/Katakana_%28Unicode_block%29
CHARSET_JAPANESE: Final[str] = "".join(chr(c) for c in range(0x3040, 0x30A0)) + "".join(
    chr(c) for c in range(0x30A0, 0x3100)
)

# Korean Hangul Syllables subset - https://en.wikipedia.org/wiki/Hangul_Syllables
CHARSET_KOREAN: Final[str] = "".join(chr(c) for c in range(0xAC00, 0xAD00))  # first 256 syllables

# Thai - https://en.wikipedia.org/wiki/Thai_%28Unicode_block%29
CHARSET_THAI: Final[str] = "".join(chr(c) for c in range(0x0E00, 0x0E80))

# Hebrew - https://en.wikipedia.org/wiki/Hebrew_%28Unicode_block%29
CHARSET_HEBREW: Final[str] = "".join(chr(c) for c in range(0x0590, 0x0600))

# Devanagari - https://en.wikipedia.org/wiki/Devanagari_%28Unicode_block%29
CHARSET_DEVANAGARI: Final[str] = "".join(chr(c) for c in range(0x0900, 0x0980))

# Emoji subset - https://en.wikipedia.org/wiki/Emoticons_(Unicode_block)
CHARSET_EMOJI: Final[str] = "".join(chr(c) for c in range(0x1F600, 0x1F650))

# Combined multilingual charset
CHARSET_MULTILINGUAL: Final[str] = (
    CHARSET_ASCII
    + CHARSET_LATIN_WITH_DIACRITICS
    + CHARSET_CYRILLIC
    + CHARSET_GREEK
    + CHARSET_ARABIC
    + CHARSET_CHINESE
    + CHARSET_JAPANESE
    + CHARSET_KOREAN
    + CHARSET_THAI
    + CHARSET_HEBREW
    + CHARSET_DEVANAGARI
    + CHARSET_EMOJI
)

CHARSET_OPTIONS: Final[dict[str, str]] = {
    "ascii": CHARSET_ASCII,
    "latin": CHARSET_ASCII + CHARSET_LATIN_WITH_DIACRITICS,
    "cyrillic": CHARSET_CYRILLIC,
    "greek": CHARSET_GREEK,
    "arabic": CHARSET_ARABIC,
    "chinese": CHARSET_CHINESE,
    "japanese": CHARSET_JAPANESE,
    "korean": CHARSET_KOREAN,
    "thai": CHARSET_THAI,
    "hebrew": CHARSET_HEBREW,
    "devanagari": CHARSET_DEVANAGARI,
    "emoji": CHARSET_EMOJI,
    "multilingual": CHARSET_MULTILINGUAL,
}
