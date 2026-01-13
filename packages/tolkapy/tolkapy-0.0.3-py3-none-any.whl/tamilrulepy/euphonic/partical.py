from typing import Dict, Callable, Any
from .posTag import cardinal_degit, wh_adverb, Case, numbers_in_words


def partical_in(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `இன்`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    if data.previous_word.singleton(-1).vowel == "ஆ":
        changes = True
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
        data.current_word = "ன்"
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    if (
        data.previous_word.string in numbers_in_words
        and data.next_word.string in cardinal_degit
        or data.next_word.string in numbers_in_words
    ):
        changes = True
        data.current_word[-1] = "ற்"
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    if data.next_word.string in Case:
        if data.previous_word.string in numbers_in_words:
            pass
        elif data.previous_word.string in numbers_in_words:
            pass

        changes = True
        data.current_word[-1] = "ற்"
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    return (changes, updata)


def partical_varru(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `வற்று`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    if data.previous_word.string in wh_adverb:
        changes = True
        data.current_word[0] = "அ"
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    return (changes, updata)


def partical_an(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `ஆன்`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = True
    updata = []
    data.current_word[-1] = "ற்"
    updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    return (changes, updata)


def partical_attu(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `அத்து`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = True
    updata = []
    data.current_word[0] = ""
    updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


def partical_ikku(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `இக்கு`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = True
    updata = []
    data.current_word[0] = ""
    updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


def partical_akku(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `அக்கு`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = True
    updata = []
    data.current_word = "அ"
    updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


def partical_am(data) -> None:
    """
    it checks the possible words and required word repesentations to make modification around `அம்`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = True
    updata = []
    letters = ["க்", "ச்", "த்"]
    related_letter = ["ங்", "ஞ்", "ந்"]
    if data.next_word.singleton(0).consonent in letters:
        changes = True
        data.current_word[-1] = related_letter[
            letters.index(data.next_word.singleton(0).consonent)
        ]
        updata.append(
            data.rules_manager(
                "இயல்பாகத்திரியும்" if data.lang == "en" else "இயல்பாகத்திரியும்"
            )
        )
    else:
        changes = True
        data.current_word[-1] = ""
        updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    return (changes, updata)


def apply(data):
    """
    it apply all the particals(சாரியை) rules and give the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply all partical grammar rules
    Return:
        list: [bool,dict]
    """

    grammar_methods = {
        "இன்": partical_in,
        "வற்று": partical_varru,
        "ஆன்": partical_an,
        "அத்து": partical_attu,
        "இக்கு": partical_ikku,
        "அக்கு": partical_akku,
        "அம்": partical_am,
    }

    status = []
    return_responce = grammar_methods[data.current_word.string](data)
    if return_responce[0] == True:
        status.append(return_responce[1])
    return status
