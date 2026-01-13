from tamilstring import String


def add_joining_consonents(data):
    """
    it will add if required joining consonents letter in between two words (ய்,வ்)
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if second_word.singleton(0).kind == "VOL" and second_word.string != "ஐ":
            if (
                first_word.singleton(-1).kind == "VOL"
                or first_word.singleton(-1).kind == "COM"
            ):
                changes = True
                if second_word.singleton(0).letter in ["இ", "ஈ", "ஐ"]:
                    data.copy[index] = String(first_word + "வ்")
                else:
                    data.copy[index] = String(first_word + "ய்")
                data.rule = "add_joining_consonents"
    return (changes, data.status())


def make_double_required_ending_consonents(data):
    """
    it makes double if ending consonents letter is ற் or ட்
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            second_word.singleton(0).kind == "VOL"
            and first_word.singleton(-1).kind == "CON"
        ):
            if first_word.singleton(-1).letter in ["ற்", "ட்"]:
                # TODO
                if first_word.singleton(-2).kind == "CON":
                    continue
                else:
                    changes = True
                    data.copy[index] = String(
                        first_word + first_word.singleton(-1).letter
                    )
                    data.rule = "make_double_required_ending_consonents"
    return (changes, data.status())


def adding_relative_consonents(data):
    """
    it adds the relative consonents (ங்,ஞ்,ண்,ந்,ம்,ன்) letter for this consonents (க்,ச்,ட்,த்,ப்,ற்)
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    letters = ["க்", "ச்", "ட்", "த்", "ப்", "ற்"]
    related_letter = ["ங்", "ஞ்", "ண்", "ந்", "ம்", "ன்"]
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            first_word.singleton(-1).kind == "COM"
            and second_word.singleton(0).kind == "COM"
            or first_word.singleton(-1).kind == "VOL"
            and second_word.singleton(0).kind == "COM"
        ):
            if second_word.singleton(0).consonent in letters:
                changes = True
                data.copy[index] = String(
                    first_word
                    + related_letter[
                        letters.index(data.words.next_word.singleton(0).consonent)
                    ]
                )
                data.rule = "adding_relative_consonents"
    return (changes, data.status())


def adding_ka_sa_tha_pa_consonents(data):
    """
    it adds the required excess consonents (க்,ச்,ப்) for containing this (க்,ச்,ப்) composite letters
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if (
            first_word.singleton(-1).kind == "COM"
            and second_word.singleton(0).kind == "COM"
            or first_word.singleton(-1).kind == "VOL"
            and second_word.singleton(0).kind == "COM"
        ):
            if second_word.singleton(0).consonent in ["க்", "ச்", "ப்"]:
                changes = True
                data.copy[index] = String(
                    first_word + second_word.singleton(0).consonent
                )
                data.rule = "adding_ka_sa_tha_pa_consonents"
    return (changes, data.status())


def remove_ending_consonent_u(data):
    """
    it removes the vowel (உ) from the ending of the word that containing composite letters
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    changes = False
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        if second_word.singleton(0).kind == "VOL":
            if (
                first_word.singleton(-1).kind == "COM"
                and first_word.singleton(-1).vowel == "உ"
            ):
                if len(first_word.letters) >= 2:
                    changes = True
                    if (
                        first_word.singleton(-2).consonent
                        == first_word.singleton(-1).consonent
                        and first_word.singleton(-1).consonent == "த்"
                    ):
                        data.copy[index] = String(first_word[:-1])
                    else:
                        data.copy[index] = String(first_word - "உ")
                    data.rule = "remove_ending_consonent_u"
                else:
                    continue
    return (changes, data.status())


def joining_consonents_with_vowel(data):
    """
    it joins the consonents with vowel in required concardinating two words
    Args:
        data (WordsGenerator): list of words that you want to apply this grammar rule
    Return:
        list: [bool,dict]
    """
    final_word = None
    for index, (first_word, second_word) in enumerate(
        zip(data.copy[:-1], data.copy[1:])
    ):
        final_word = (
            String(first_word + second_word)
            if final_word == None
            else String(final_word + second_word)
        )
        data.rule = "joining_consonents_with_vowel"
    data.copy = [final_word]
    return (True, data.status())


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
        remove_ending_consonent_u,
        make_double_required_ending_consonents,
        adding_ka_sa_tha_pa_consonents,
        add_joining_consonents,
        joining_consonents_with_vowel,
    ]

    for grammar in grammar_methods:
        return_responce = grammar(data)
        if return_responce[0] == True:
            status.append(return_responce[1])

    return status
