import csv
import re

from baseline.constants import NOT_A_TOKEN_IN_USE
from data_prep_tools import get_data
from tools.find_resource_in_project import get_path


def get_programming_symbols_map():
    # source = https://blog.codinghorror.com/ascii-pronunciation-rules-for-programmers/
    symbol_to_name = {}
    with open(get_path("data/programming_symbols.csv"), "r") as csvfile:
        csvfile.readline()
        rows = csv.reader(csvfile, delimiter=",")
        current_symbol = ""
        for row in rows:
            if not row[0][0].isalpha():
                if current_symbol:
                    if current_symbol == "\\\"":
                        symbol_to_name["\""] = current_names
                    else:
                        symbol_to_name[current_symbol] = current_names
                current_symbol = row[0]
                current_names = set()
                row = row[1:]
            for cell in row:
                current_names.update([re.sub(r'\(.*\)',"",x.strip(" ")) for x in cell.split("\n")])
    keys_to_remove = []
    new_symbols = {}
    for key in symbol_to_name.keys():
        if " " in key:
            keys_to_remove.append(key)
            symbols = key.split(" ")
            values = [set(),set()]
            for name in symbol_to_name[key]:
                name.replace(" / ","/")
                individual = [x.strip(" ") for x in name.split("/")]
                text = re.search(r' .*$',individual[1])
                if text:
                    individual[0] += text.group(0)
                values[0].add(individual[0])
                values[1].add(individual[1])
            new_symbols[symbols[0]] = values[0]
            new_symbols[symbols[1]] = values[1]
    for key in keys_to_remove:
        symbol_to_name.pop(key)
    symbol_to_name.update(new_symbols)
    return symbol_to_name


def get_pseudocode_tokens(tokenized_pseudocode_files=None):
    tokens_present = set()
    if not tokenized_pseudocode_files:
        pseudocode_list = get_data.get_data_from_directory("/pseudocode_simplified/")
        tokenized_pseudocode_files = [x.split(" ") for x in pseudocode_list]
    for pseudocode_file in tokenized_pseudocode_files:
        for token in pseudocode_file:
            if len(token) > 1 and not token[0].isalpha() and not token[0].isdigit():
                tokens_present.add(token[0])
                token = token[1:]
            if len(token) > 1:
                tokens_present.add(token)

    symbol_to_name = get_programming_symbols_map()
    token_to_symbol = {}
    # this orders the subsequent for loop so that the key words always override any name mappings (e.g. and vs &)
    tokens_present = sorted(list(tokens_present),key=lambda x: 1 if x.isalpha() else 0)
    for token in tokens_present:
        if token in symbol_to_name.keys():
            for name in symbol_to_name[token]:
                token_to_symbol[name] = token
        else:
            token_to_symbol[token] = token
    return token_to_symbol

if __name__ == "__main__":
    print()
    print()
    print(get_pseudocode_tokens())

