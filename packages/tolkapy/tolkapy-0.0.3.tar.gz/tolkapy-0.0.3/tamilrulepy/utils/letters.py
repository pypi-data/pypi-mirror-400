import tamil


def get_last_letter(word: str) -> str:
    try:
        return tamil.utf8.get_letters(word)[-1]
    except IndexError:
        return ""


def get_first_letter(word: str) -> str:
    try:
        return tamil.utf8.get_letters(word)[0]
    except IndexError:
        return ""


def get_root_letter(letter: str) -> str:
    return tamil.utf8.splitMeiUyir(letter)[0]
