from tamilstring import get_letters
import sys
from .stackwords import WordsGenerator, Maintainer


try:
    from IPython.display import display, Markdown

    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False


def get(words_list, rules=False, IPY=True, lang="en"):
    """
    it is the common method to apply and get all the possible form of words that are derived by tamil grammar rules.
    Args:
        data (list): list of words that you want to apply grammar rules
        rules (bool): defalut is False, if you enable it as True, it will shows you what are the grammar rules that are applied by this library
        IPY (bool): default is True, it only works on Ipython. it helps to give output in ipython in a orginized way to visualize.
    Return:
        list:  by default it returns a list of list contains tamil words that are derived by tamil grammar rules
    """

    data = Maintainer(words_list, lang)

    finalizer = WordsGenerator()

    finalizer.config_grammer_rules(data)

    if rules:
        if "ipykernel" in sys.modules and IPY:
            return display(Markdown(convert_markdown_table(finalizer.get_words())))
        else:
            return finalizer.get_words()

    else:
        return [sublist[-1]["words"] for sublist in finalizer.get_words() if sublist]


def convert_markdown_table(data):
    tables = []

    for i, sublist in enumerate(data, start=1):
        headers = ["Words", "Rule"]
        md_table = f"### Table {i}\n\n"
        md_table += "| " + " | ".join(headers) + " |\n"
        md_table += "|---" * len(headers) + "|\n"

        for entry in sublist:
            words_str = " + ".join(entry["words"])
            rule_str = entry["rule"] if entry["rule"] is not None else "None"
            md_table += f"| {words_str} | {rule_str} |\n"

        tables.append(md_table)

    return "\n\n".join(tables)
