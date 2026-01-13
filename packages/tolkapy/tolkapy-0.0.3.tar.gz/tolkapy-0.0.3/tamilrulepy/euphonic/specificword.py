from tamilstring import String
from tamilstring.utf8 import make_letter
from . import posTag


def specific_pointing_letters(data):
    """
    it removes `மை` at ending of any word and gives the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if first_word.string == "அ":
            if second_word.singleton(0).consonent in ["ந்", "ஞ்", "ம்"]:
                data.copy[index] = String(
                    first_word + second_word.singleton(0).consonent
                )
                data.rule = "remove_ending_consonent_mai"
            if second_word.singleton(0).consonent in ["ய்", "வ்"]:
                data.copy[index] = String(first_word + "வ்")
                data.rule = "remove_ending_consonent_mai"
            if second_word.singleton(0).kind == "VOL":
                data.copy[index] = String(first_word + "வ்வ்")
                data.rule = "remove_ending_consonent_mai"

    return (changes, data.status())


def cardinal_specific_degit(data):
    """
    it removes `மை` at ending of any word and gives the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if second_word.string == "குறை":
            if first_word.string in ["கா", "பனை"]:
                data.copy.insert(1, String("இன்"))
                data.rule = "remove_ending_consonent_mai"
            elif data.src[0] in ["கலம்"]:
                data.copy.insert(1, String("த்து"))
                data.rule = "remove_ending_consonent_mai"
            elif first_word.string in posTag.cardinal_degit:
                data.copy.insert(1, String("இன்"))
                data.rule = "remove_ending_consonent_mai"
            elif first_word.string in posTag.numbers_in_words:
                data.copy.insert(1, String("இன்"))
                data.rule = "remove_ending_consonent_mai"
    return (changes, data.status())


def specific_pointing_num(data):
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if data.src[0] == "நும்":
            if second_word.string == "அது":
                changes = True
                first_word.string = "நும்"
                data.rule = "specific_pointing_num"
            else:
                changes = True
                first_word.string = "நும"
                data.rule = "specific_pointing_num"
    return (changes, data.status())


def specific_pointing_list(data):
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        print(make_letter(first_word.singleton(0).consonent, "அ"))
        if data.src[0] in ["தாம்", "நாம்"]:
            changes = True
            first_word = String(
                make_letter(first_word.singleton(0).consonent, "அ") + "ம"
            )
            data.rule = "specific_pointing_list"
        elif data.src[0] == "யான்":
            changes = True
            first_word = String("எம")
            data.rule = "specific_pointing_list"
    return (changes, data.status())


def apply(data):
    """
    it apply all the common rules and give the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    status = []

    grammar_methods = [
        specific_pointing_letters,
        cardinal_specific_degit,
        specific_pointing_num,
        specific_pointing_list,
    ]

    for grammar in grammar_methods:
        return_responce = grammar(data)
        if return_responce[0] == True:
            status.append(return_responce[1])

    return status
