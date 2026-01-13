import tamil

from tamilrulepy.mozhimarabu.word_starting import (
    uyirmei_ka_check,
    uyirmei_ma_check,
    uyirmei_na_check,
    uyirmei_nga_check,
    uyirmei_pa_check,
    uyirmei_sa_check,
    uyirmei_ta_check,
    uyirmei_va_check,
    uyirmei_ya_check,
)

from tamilrulepy.mozhimarabu.word_ending import (
    uyir_check,
    mellinam_check,
    idaiyinam_check,
    alapedai_check,
    oorezhuthoorumozhi_check,
    suttu_check,
    vinaa_check,
)

WORD_STARTING_RULES = (
    uyirmei_ka_check,
    uyirmei_ma_check,
    uyirmei_na_check,
    uyirmei_nga_check,
    uyirmei_pa_check,
    uyirmei_sa_check,
    uyirmei_ta_check,
    uyirmei_va_check,
    uyirmei_ya_check,
)

WORD_ENDING_RULES = (
    uyir_check,
    mellinam_check,
    idaiyinam_check,
    alapedai_check,
    oorezhuthoorumozhi_check,
    suttu_check,
    vinaa_check,
)


def is_proper_word_starting(word: str) -> bool:
    results = []
    for rule in WORD_STARTING_RULES:
        result = rule(word)
        if result is None:
            continue
        results.append(result)
    return all(results) and len(results) != 0


def is_proper_word_ending(word: str) -> bool:
    results = []
    for rule in WORD_ENDING_RULES:
        try:
            result = rule(word)
            results.append(result)
        except Exception:
            continue  # TODO: Need to check if one letter word is coming how to handle rule check
    return any(results) and len(results) != 0
