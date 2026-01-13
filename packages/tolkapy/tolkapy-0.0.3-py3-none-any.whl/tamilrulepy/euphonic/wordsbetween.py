from tamilstring import String
from tamil.utf8 import joinMeiUyir
from . import previous

# from tamilstring.utf8 import make_letter


def relative_constant_for_second_word_ka_sa_tha_pa(data):
    """
    if second word starting comes with any of the constants ['க்','ச்','த்','ப்']` this rule modify
    the first words endings with relative consonents ['ங்','ஞ்','ந்','ம்']
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    if_has_letters = ["க்", "ச்", "த்", "ப்"]
    was_to_change = ["ங்", "ஞ்", "ந்", "ம்"]
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            first_word.singleton(-1).kind == "COM"
            and second_word.singleton(0).kind == "COM"
            and second_word.singleton(0).consonent in if_has_letters
        ):
            list_index = if_has_letters.index(second_word.singleton(0).consonent)
            if list_index:
                changes = True
                data.copy[index] = String(first_word + was_to_change[list_index])
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


# தொகை-2
def if_words_ending_letters(data):
    """
    #TODO
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    if_has_letters = ["க்", "ச்", "த்", "ப்"]
    was_to_change = ["ங்", "ஞ்", "ந்", "ம்"]
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            second_word.singleton(0).kind == "COM"
            and first_word.singleton(-1).vowel == "உ"
            and second_word.singleton(0).consonent in if_has_letters
        ):
            list_index = if_has_letters.index(second_word.singleton(0).consonent)
            if list_index:
                changes = True
                data.copy[index] = String(first_word + was_to_change(list_index))
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


# தொகை-3
def ஞ்ந்ம்(data):
    """
    first_word_ending_na_na_constants
    # TODO
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    if_has_letters = ["ஞ்", "ந்", "ம்"]
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            second_word.singleton(0).kind == "COM"
            and first_word.singleton(-1).vowel == "உ"
            and second_word.singleton(0).consonent in if_has_letters
        ):
            list_index = if_has_letters.index(second_word.singleton(0).consonent)
            if list_index:
                changes = True
                data.copy[index] = String(
                    first_word + second_word.singleton(0).consonent
                )
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


# தொகை - 4
def first_word_ending_na3_na5_consonents(data):
    """
    if first word comes with any of the constants ['ன்','ண்'] at the ending then it will try to match other rules such as
    1) if second word starts with this consonents ['ய்','ஞ்'] then it will convert the `ய்` into `ஞ்`, no need to converts `ஞ்` into again it
    2) if second word starts with ["க்", "ச்", "ட்", "த்", "ப்", "ற்"] then it converts `ண்` into `ட்`
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if first_word.singleton(-1).consonent in ["ன்", "ண்"]:
            if second_word.singleton(0).consonent in ["ய்", "ஞ்"]:
                changes = True
                second_word[0] = joinMeiUyir("ஞ்", second_word.singleton(0).vowel)
                data.copy[index + 1] = second_word
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

            if second_word.singleton(0).consonent in ["க்", "ச்", "ட்", "த்", "ப்", "ற்"]:
                changes = True
                first_word[-1] = (
                    "ட்" if first_word.singleton(-1).consonent == "ண்" else "ற்"
                )
                data.copy[index + 1] = second_word
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))

    return (changes, updata)


# தொகை - 5
def first_word_ending_la1_na5_consonents(data):
    """
    if first word comes with any of the constants ['ல்','ன்'] at the ending then it will make some modifications are
    'ந்' into 'ன்' and 'த்' into 'ற்'(it does not stop with  'த்' into 'ற்' also converts first words ending consonents into 'ற்')
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    updata = []
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if first_word.singleton(-1).consonent in ["ல்", "ன்"]:
            if second_word.singleton(0).consonent in ["ந்"]:
                changes = True
                second_word[0] = joinMeiUyir("ன்", second_word.singleton(0).vowel)
                data.copy[index + 1] = second_word
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
            if second_word.singleton(0).consonent in ["த்"]:
                changes = True
                first_word[-1] = "ற்"
                second_word[0] = joinMeiUyir("ற்", second_word.singleton(0).vowel)
                data.copy[index + 1] = second_word
                updata.append(data.rules_manager("இயல்பாகத்திரியும்"))
    return (changes, updata)


def apply(data):
    """
    it apply all the particals(சாரியை) rules and give the result of the words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """

    status = []

    previous_apply = previous.apply(data)
    if len(previous_apply) > 0:
        status.append(previous_apply[1])

    grammar_methods = [
        relative_constant_for_second_word_ka_sa_tha_pa,
        first_word_ending_na3_na5_consonents,
        first_word_ending_la1_na5_consonents,
    ]
    for grammar in grammar_methods:
        return_responce = grammar(data)
        if return_responce[0] == True:
            status.append(return_responce[1])

    return status
