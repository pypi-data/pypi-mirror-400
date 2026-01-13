from tamilrulepy.utils.letters import get_first_letter, get_last_letter, get_root_letter
from tamilrulepy.utils.rules import is_proper_word_ending, is_proper_word_starting
import tamil


def thogai_1(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil word (தொகை) by joining two given Tamil words
    based on specific phonetic rules.

    This function checks the following conditions:

    #. The last letter of ``first_word`` is a valid uyirmei (உயிர்மெய்) letter.
    #. The root of the first letter of ``second_word`` is one of
       {``க்``, ``ச்``, ``த்``, ``ப்``}.

    If both conditions are met, the function inserts the corresponding mei (மெய்)
    consonant between the words using a predefined mapping and returns the
    combined result.

    :param first_word: The first Tamil word.
    :type first_word: str
    :param second_word: The second Tamil word.
    :type second_word: str
    :return: A compound Tamil word formed by joining ``first_word`` and ``second_word``
             according to Tamil phonetic rules, or ``None`` if the conditions are not met.
    :rtype: str

    :raises None: This function does not raise exceptions directly.

    **Example:**

    >>> thogai_1("அழகு", "பூ")
    'அழகும் பூ'

    **Notes:**
        - Depends on helper functions: ``get_last_letter``, ``get_first_letter``, and ``get_root_letter``.
        - Uses ``tamil.utf8.uyirmei_letters`` for letter validation.
    """
    fw_last_letter = get_last_letter(first_word)
    if fw_last_letter not in tamil.utf8.uyirmei_letters:
        return None
    sw_first_letter = get_root_letter(get_first_letter(second_word))
    if sw_first_letter not in ("க்", "ச்", "த்", "ப்"):
        return None
    mei_map = {"க்": "ங்", "ச்": "ஞ்", "த்": "ந்", "ப்": "ம்"}
    return first_word + mei_map.get(sw_first_letter) + second_word


def thogai_2(first_word: str, second_word: str) -> str:
    """
    Joins two Tamil words to form a compound expression (தொகை)
    when the first word ends properly as per Tamil grammar rules.

    This function checks the following conditions:

    #. The ``first_word`` must end correctly according to Tamil grammatical rules.
       If not, a ``ValueError`` is raised.
    #. The root of the first letter of ``second_word`` must be one of
       {``ஞ்``, ``ந்``, ``ம்``, ``ய்``, ``வ்``}.

    If both conditions are satisfied, the two words are joined with a space
    and returned as a single string.

    :param first_word: The first Tamil word to be validated and joined.
    :type first_word: str
    :param second_word: The second Tamil word to be appended.
    :type second_word: str
    :return: The combined Tamil expression if valid, otherwise ``None``.
    :rtype: str

    :raises ValueError: If the ending of ``first_word`` is not proper as per grammar.

    **Example:**

    >>> thogai_2("அவன்", "வீடு")
    'அவன் வீடு'

    **Notes:**
        - Uses helper functions: ``is_proper_word_ending``, ``get_first_letter``, and ``get_root_letter``.
        - This function enforces Tamil grammatical correctness for word joining.
    """
    if not is_proper_word_ending(first_word):
        raise ValueError("First word ending is not proper as per grammar")
    if get_root_letter(get_first_letter(second_word)) not in ("ஞ்", "ந்", "ம்", "ய்", "வ்"):
        return None
    return first_word + " " + second_word


def thogai_3(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil word (தொகை) by joining two words,
    inserting the root consonant of the second word between them
    when the first word ends properly as per Tamil grammar.

    This function checks the following conditions:

    #. The ``first_word`` must end correctly according to Tamil grammatical rules.
       If not, a ``ValueError`` is raised.
    #. The root of the first letter of ``second_word`` must be one of
       {``ஞ்``, ``ந்``, ``ம்``}.

    If both conditions are satisfied, the function inserts the root consonant
    of ``second_word`` between the two words and returns the combined form.

    :param first_word: The first Tamil word to be validated and joined.
    :type first_word: str
    :param second_word: The second Tamil word whose root consonant may be inserted.
    :type second_word: str
    :return: The compound Tamil word formed by merging the two words
             with the appropriate consonant, or ``None`` if the rules do not match.
    :rtype: str

    :raises ValueError: If the ending of ``first_word`` is not proper as per grammar.

    **Example:**

    >>> thogai_3("அவன்", "மனைவி")
    'அவன்மனைவி'

    **Notes:**
        - Uses helper functions: ``is_proper_word_ending``, ``get_first_letter``, and ``get_root_letter``.
        - Enforces Tamil grammatical correctness before performing word joining.
    """
    if not is_proper_word_ending(first_word):
        raise ValueError("First word ending is not proper as per grammar")

    rl_second = get_root_letter(get_first_letter(second_word))
    if rl_second not in ("ஞ்", "ந்", "ம்"):
        return None
    return first_word + rl_second + second_word


def thogai_4(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil expression (தொகை) by applying a phonetic transformation
    between two Tamil words when specific grammatical and phonetic conditions are met.

    This function checks the following conditions:

    #. The last letter of ``first_word`` must be a mei (மெய்) letter or its root consonant.
    #. The root consonant of ``first_word`` must be either ``ண்`` or ``ன்``.
    #. The first letter of ``second_word`` must be either ``ஞா`` or ``யா``.
       (Future work: ``second_word`` should ideally be a verb.)

    If the conditions are satisfied, the function performs a phonetic interchange
    (``பொலி மாற்றம்``) between ``ஞா`` and ``யா`` using a predefined mapping and returns
    the modified combined word.

    :param first_word: The first Tamil word whose ending determines the phonetic rule.
    :type first_word: str
    :param second_word: The second Tamil word, which may undergo a phonetic transformation.
    :type second_word: str
    :return: The transformed compound Tamil word if all conditions are met,
             otherwise ``None``.
    :rtype: str

    :raises None: This function does not raise exceptions directly.

    **Example:**

    >>> thogai_4("தேன்", "யானை")
    'தேன்ஞானை'

    **Notes:**
        - Uses helper functions: ``get_last_letter``, ``get_first_letter``,
          and ``get_root_letter``.
        - Depends on ``tamil.utf8.mei_letters`` for validation.

    TODO::
        This function is **not fully complete**.
        It currently assumes ``second_word`` may start with ``ஞா`` or ``யா``,
        but future enhancement is required to ensure that ``second_word``
        is a verb as per Tamil grammatical rules.

    """
    if get_last_letter(first_word) not in tamil.utf8.mei_letters:
        first_word_last_mei_char = get_root_letter(get_last_letter(first_word))
    else:
        first_word_last_mei_char = get_last_letter(first_word)
    if first_word_last_mei_char not in ("ண்", "ன்"):
        return None
    fl_second = get_first_letter(second_word)
    if fl_second not in (
        "ஞா",
        "யா",
    ):  # TODO: second word needs to be a verb (future work)
        return None
    poli_map = {"ஞா": "யா", "யா": "ஞா"}
    changed_second = poli_map[fl_second] + "".join(
        tamil.utf8.get_letters(second_word)[1:]
    )
    return first_word + changed_second


def thogai_5(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil word (தொகை) by joining two words directly
    when the first word ends and the second word begins properly
    according to Tamil grammatical rules.

    This function checks the following conditions:

    #. The ``second_word`` must begin correctly as per Tamil grammar.
       If not, a ``ValueError`` is raised.
    #. The last letter of ``first_word`` must be a mei (மெய்) letter
       or its root consonant.
    #. The root consonant of ``first_word`` must be either ``ண்`` or ``ன்``.

    If all conditions are satisfied, the two words are concatenated directly
    without any phonetic transformation and returned as a combined Tamil word.

    :param first_word: The first Tamil word whose ending is validated before joining.
    :type first_word: str
    :param second_word: The second Tamil word whose beginning must be proper.
    :type second_word: str
    :return: The concatenated Tamil compound word if all grammatical conditions are met,
             otherwise ``None``.
    :rtype: str

    :raises ValueError: If ``second_word`` is not a proper Tamil word.

    **Example:**

    >>> thogai_5("அவன்", "நண்பன்")
    'அவன்னண்பன்'

    **Notes:**
        - Uses helper functions: ``is_proper_word_starting``, ``get_last_letter``,
          and ``get_root_letter``.
        - Depends on ``tamil.utf8.mei_letters`` for identifying consonant endings.
        - No intermediate phonetic changes are applied in this rule.
    """
    if not is_proper_word_starting(second_word):
        raise ValueError("Second word is not a proper tamil word")
    if get_last_letter(first_word) not in tamil.utf8.mei_letters:
        first_word_last_mei_char = get_root_letter(get_last_letter(first_word))
    else:
        first_word_last_mei_char = get_last_letter(first_word)
    if first_word_last_mei_char not in ("ண்", "ன்"):
        return None
    return first_word + second_word


def thogai_6(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil word (தொகை) by joining two words directly
    when the first word ends and the second word begins properly
    according to following thogaimarabu grammatical rules.

    1. When first_word ends with the following letters ``ன்``,``ண்`` then the joins will be normal joins
    2. When second_word starts with (வல்லினம்) vallinam letter second words first letter will be disort "ன்" |rarr| "ற்", "ண்" |rarr| "ட்" and join

    :param first_word: The first Tamil word whose ending is validated before joining
    :type first_word: str
    :param second_word: The second Tamil word whose beginning must be proper.
    :type second_word: str
    :return: The concatenated Tamil compound word if all grammatical conditions are met,
             otherwise ``None``.
    :rtype: str

    :raises ValueError: If ``second_word`` is not a proper Tamil word.

    **Example:**

    >>> thogai_6("பொன்","குடம்")
    'பொற்குடம்'

    **Notes:**
        - Uses helper functions: ``get_first_letter``, ``get_last_letter``,
          and ``get_root_letter``.
        - Depends on ``tamil.utf8.vallinam_letters`` for identifying second word starting.
        - No intermediate phonetic changes are applied in this rule.
    """
    if get_root_letter(get_first_letter(second_word)) in tamil.utf8.vallinam_letters:
        first_word_last_mei_char = get_last_letter(first_word)
        letter_map = {"ன்": "ற்", "ண்": "ட்"}
        return (
            "".join(tamil.utf8.get_letters(first_word)[:-1])
            + letter_map[first_word_last_mei_char]
            + second_word
        )
    else:
        return first_word + second_word


def thogai_7(first_word: str, second_word: str) -> str:
    """
    Forms a compound Tamil word (தொகை) by joining two words directly
    when the first word ends and the second word begins properly
    according to following thogaimarabu grammatical rules.

    1. when first word ends with ல், ன் second word starts with த, ந then second word's starting and first words ending changes into ற, ன

    :param first_word: The first Tamil word whose ending is validated before joining.
    :type first_word: str
    :param second_word: The second Tamil word whose beginning must be proper.
    :type second_word: str
    :return: The concatenated Tamil compound word if all grammatical conditions are met,
             otherwise ``None``.
    :rtype: str

    :raises ValueError: If ``second_word`` is not a proper Tamil word.

    **Example:**

    >>> thogai_6("பொன்","குடம்")
    'பொற்குடம்'

    **Notes:**
        - Uses helper functions: ``get_first_letter``, ``get_last_letter``,
          and ``get_root_letter``.
        - Depends on ``tamil.utf8.vallinam_letters`` for identifying second word starting.
        - No intermediate phonetic changes are applied in this rule.

    """
    second_word_first_letter = get_first_letter(second_word)
    second_word_first_letters_mei = get_root_letter(second_word_first_letter)
    if get_last_letter(first_word) in ["ல்", "ன்"] and second_word_first_letters_mei in [
        "த்",
        "ந்",
    ]:
        letter_map = {"த்": "ற்", "ந்": "ன்"}
        new_letter = tamil.utf8.join_letters_elementary(
            [
                letter_map[second_word_first_letters_mei],
                tamil.utf8.splitMeiUyir(second_word_first_letter)[1],
            ]
        )
        return (
            "".join(tamil.utf8.get_letters(first_word)[:-1])
            + letter_map[second_word_first_letters_mei]
            + new_letter
            + "".join(tamil.utf8.get_letters(second_word)[1:])
        )
    else:
        return ""


def thogai_8(first_word: str, second_word: str) -> str:
    """
    1. when first_word ends with ண்,ள் and second word starts with த, ந then resulting joining letter turns into ட, ண letters
    """
    second_word_first_letter = get_first_letter(second_word)
    second_word_first_letter_mei = get_root_letter(second_word_first_letter)
    if get_last_letter(first_word) in ["ண்", "ள்"] and second_word_first_letter_mei in [
        "த்",
        "ந்",
    ]:
        letter_map = {"த்": "ட்", "ந்": "ண்"}
        new_letter = tamil.utf8.join_letters_elementary(
            [
                letter_map[second_word_first_letter_mei],
                tamil.utf8.splitMeiUyir(second_word_first_letter)[1],
            ]
        )
        return (
            "".join(tamil.utf8.get_letters(first_word)[:-1])
            + letter_map[second_word_first_letter_mei]
            + new_letter
            + "".join(tamil.utf8.get_letters(second_word)[1:])
        )
    else:
        return ""


def thogai_9(first_word: str, second_word: str) -> str:
    """
    1.
    """


def thogai_10(first_word: str, second_word: str) -> str:
    """
    1.
    """


def thogai_11(first_word: str, second_word: str) -> str:
    """
    1.
    """


def thogai_12(first_word: str, second_word: str) -> str:
    """ """


def thogai_13(first_word: str, second_word: str) -> str:
    """ """


def thogai_14(first_word: str, second_word: str) -> str:
    """ """


def thogai_15(first_word: str, second_word: str) -> str:
    """ """
