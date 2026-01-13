from tamilstring import Letter

phonetic_length_1 = [
    "அ",
    "இ",
    "உ",
    "எ",
    "ஒ",
]

phonetic_length_2 = ["ஆ", "ஈ", "ஊ", "ஏ", "ஐ", "ஓ", "ஔ"]


def apply(letter):
    """
    it apply the particals(சாரியை) rules for the single letters and gives the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    original_letter = letter

    return_value = []

    letter = Letter(letter)
    vowel = None

    rule = "எழுத்துச்சாரியை"

    if letter.kind == "VOL":
        vowel = original_letter
    elif letter.kind == "COM":
        consonents_, vowel_ = letter.split_letter
        vowel = vowel_

    if vowel in phonetic_length_2:
        return_value.extend([[{"words": [original_letter + "காரம்"], "rule": rule}]])
    if vowel in phonetic_length_1:
        word_list = [
            original_letter + "காரம்",
            original_letter + "கரம்",
            original_letter + "ஃகான்",
        ]
        return_value.extend([[{"words": [word], "rule": rule}] for word in word_list])
    if vowel in ["ஐ", "ஔ"]:
        return_value.append([{"words": [original_letter + "கான்"], "rule": rule}])

    if len(return_value) == 0:
        return [[{"words": letter}]]
    else:

        return return_value
