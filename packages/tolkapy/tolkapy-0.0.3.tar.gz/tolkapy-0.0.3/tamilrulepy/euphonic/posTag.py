from typing import List, Final

# For Tamil string literals
TamilString = str

# Case suffixes
Case: Final[List[TamilString]] = ["கு", "கண்", "அது"]

# Tamil particles
Particals: Final[List[TamilString]] = ["இன்", "வற்று", "அத்து", "அம்", "ஆன்", "அக்கு", "இக்கு"]


# numerical words representation

numbers_in_words = [
    "ஒன்று",
    "இரண்டு",
    "மூன்று",
    "நான்கு",
    "ஐந்து",
    "ஆறு",
    "ஏழு",
    "எட்டு",
    "ஒன்பது",
    "பத்து",
]

# Cardinal numbers
cardinal_degit: Final[List[TamilString]] = [
    "உழக்கு",
    "பானை",
    "கா",
    "ஆலாக்கு",
    "அகழ்",
    "அங்குலம்",
]


# Wh-adverbs (interrogative/relative adverbs)
wh_adverb: Final[List[TamilString]] = ["அவை", "இவை", "எவை", "அது", "இது", "எது"]

wh_adverb_e_i = [
    "அதோனி",
    "இதோனி",
    "உதோனி",
    "எதோனி",
    "ஆண்டை",
    "யாண்டை",
]

uyartiṇai = "யாவர்"


list_of_words = ["தாம்", "நாம்", "யான்"]
