from typing import List, Dict, Any, Optional
from tamilstring import String
from tamilstring import get_letters

from . import partical, posTag, singleletter, wordsbetween
from . import common
from . import wordsbetween
from . import previous
from . import specificword


class Maintainer:
    def __init__(self, words_list: List[str], lang: "ta") -> None:
        self.list: List[str] = words_list
        self.position: int = 0
        self.src = words_list
        self.copy: List[String] = [String(word) for word in self.list]
        self.rule: Optional[str] = None
        self.lang = lang
        # self.explination: Optional[str] = None

    def status(self) -> Dict[str, Any]:
        return {
            "words": [word.string for word in self.copy],
            "rule": self.rule,
            # "explination": self.explination
        }

    def words_status(self) -> List[str]:
        return [word.string for word in self.copy]

    def restore(self):
        self.copy: List[String] = [String(word) for word in self.src]

    def rules_manager(self, rule):

        status = {"words": self.words_status(), "rule": rule}

        self.restore()
        return status

    @property
    def previous_word(self) -> String:
        return self.copy[self.position - 1]

    @property
    def current_word(self) -> String:
        return self.copy[self.position]

    @property
    def next_word(self) -> String:
        try:
            return self.copy[self.position + 1]
        except IndexError:
            return String("")

    @previous_word.setter
    def previous_word(self, word: str) -> None:
        self.copy[self.position - 1].string = word

    @current_word.setter
    def current_word(self, word: str) -> None:
        self.copy[self.position].string = word

    @next_word.setter
    def next_word(self, word: str) -> None:
        self.copy[self.position + 1].string = word


class WordsGenerator:

    final_list: List[List[Dict[str, Any]]] = []

    def updata_final_list(self, result) -> None:
        self.final_list = result

    def get_words(self):
        return self.final_list

    def grammer_applyer(self, data, msg=[], previous_stage=None):
        """
        Returns :
            dict : containing all the applied grammar rules and modifications
        """
        if len(msg) < 1:

            self.final_list.append(common.apply(data))

        else:
            for each_type in msg:

                if len(each_type) > 1:
                    for each in each_type:
                        self.grammer_orginizer(each, data, previous_stage)
                else:
                    self.grammer_orginizer(each_type[0], data, previous_stage)

        # return self.final_list

    def grammer_orginizer(self, each_type, data, previous_stage):

        data.copy = [String(word) for word in each_type["words"]]

        after = common.apply(data)

        appending_list = [each_type]

        appending_list.extend(after)

        if len(previous_stage) > 0:
            appending_list = previous_stage + appending_list

        appending_list.insert(0, {"words": data.src, "rule": "given words"})

        self.final_list.append(appending_list)

    def config_grammer_rules(self, data: Maintainer):

        self.final_list = []

        len_of_words_list = len(data.list)

        previous_stage = previous.apply(data)

        if len_of_words_list == 1:
            word_letter = get_letters(data.list[0])
            if len(word_letter) == 1:
                self.final_list = singleletter.apply(word_letter[0])
            else:
                self.final_list = [[{"words": data.list[0]}]]

        elif len_of_words_list == 2:
            if data.list[-1] in posTag.Case:
                self.grammer_applyer(data, specificword.apply(data), previous_stage)

            elif data.list[-1] in ["குறை"]:
                self.grammer_applyer(data, specificword.apply(data), previous_stage)

            elif data.list[0] in ["அ", "இ", "எ"]:
                self.grammer_applyer(data, specificword.apply(data), previous_stage)

            elif data.list[0] in posTag.wh_adverb_e_i:
                self.grammer_applyer(data, wordsbetween.apply(data), previous_stage)

            elif data.list[0] in posTag.list_of_words:
                self.grammer_applyer(data, wordsbetween.apply(data), previous_stage)

            else:
                self.grammer_applyer(data, wordsbetween.apply(data), previous_stage)

        else:

            for word in data.list:
                if word in posTag.Particals and data.position < len(data.list) - 1:
                    self.grammer_applyer(data, partical.apply(data), previous_stage)

                data.position += 1
