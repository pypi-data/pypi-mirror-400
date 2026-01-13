from tamilstring import String
from . import posTag


def remove_ending_consonent_mai(data):
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
        if first_word.singleton(-1).letter == "மை":
            if len(first_word.letters) >= 2:
                changes = True
                data.copy[index] = String(first_word[:-1])
                data.rule = "remove_ending_consonent_mai"
            else:
                continue
    return (changes, data.status())


def remove_ending_consonent_m(data):
    """
    if any last letter of word containing `ம்` having composite or consonent will be removed
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if first_word.singleton(-1).consonent == "ம்":
            if (
                len(first_word.letters) >= 2
                and first_word.string not in posTag.Particals
            ):
                changes = True
                data.copy[index] = String(first_word[:-1])
                data.rule = "remove_ending_consonent_m"
            else:
                continue
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

    grammar_methods = [remove_ending_consonent_m, remove_ending_consonent_mai]

    for grammar in grammar_methods:
        return_responce = grammar(data)
        if return_responce[0] == True:
            status.append(return_responce[1])

    if len(status) > 0:
        data.list = status[-1]["words"]

    return status
