import os
import csv
import re
import get_data


def get_programming_symbols_map():
    # source = https://blog.codinghorror.com/ascii-pronunciation-rules-for-programmers/
    symbol_to_name = {}
    with open("programming_symbols.csv", "r") as csvfile:
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
    symbol_to_name["\\n"] = set(["newline", "backslash n"])
    symbol_to_name["*"].add("multiplied by")
    symbol_to_name["*"].add("multiply")
    symbol_to_name["*"].add("times by")
    symbol_to_name["%"].add("percent")
    symbol_to_name["-"].add("subtract")
    symbol_to_name["="].add("equal")
    symbol_to_name["="].add("is")
    symbol_to_name["="].remove("gets")
    symbol_to_name["="].remove("takes")
    symbol_to_name["="].add("is equal to")
    symbol_to_name["="].add("is set to")
    symbol_to_name["/"].add("divided by")
    symbol_to_name["/"].add("divided")
    symbol_to_name["/"].add("divide")
    symbol_to_name["/"].add("div")
    symbol_to_name[">"].add("is greater than")
    symbol_to_name[">"].add("larger than")
    symbol_to_name[">"].add("bigger than")
    symbol_to_name["<"].remove("from")
    symbol_to_name[">"].remove("into")
    symbol_to_name["<"].add("is less than")
    symbol_to_name["<"].add("smaller than")
    symbol_to_name["("].add("open bracket")
    symbol_to_name[")"].add("close bracket")
    symbol_to_name["["].add("square bracket")
    symbol_to_name["["].add("open square bracket")
    symbol_to_name["["].remove("opening bracket")
    symbol_to_name["]"].remove("closing bracket")
    symbol_to_name["]"].add("close square bracket")
    symbol_to_name[":"].remove("dots")

    return symbol_to_name


def get_pseudocode_tokens():
    tokens_present = set()
    for pseudocode in get_data.get_data_from_directory("/pseudocode_simplified/"):
        tokens = pseudocode.split()
        for token in tokens:
            if len(token) > 1 and not token[0].isalpha() and not token[0].isdigit():
                tokens_present.add(token[0])
                token = token[1:]
            if len(token) > 1 and not token[-1].isalpha() and not token[-1].isdigit():
                tokens_present.add(token[1])
                token = token[:-1]
            tokens_present.add(token)

    symbol_to_name = get_programming_symbols_map()
    token_to_symbol = {}
    # this orders the subsequent for loop so that the key words always override any name mappings (e.g. and vs &)
    tokens_present = sorted(list(tokens_present),key=lambda x: 1 if x.isalpha() else 0)
    for token in tokens_present:
        if token in symbol_to_name.keys():
            for name in symbol_to_name[token]:
                token_to_symbol[name] = token
        elif token == "NEWLINE":
            token_to_symbol["new line"] = token
            token_to_symbol["backslash n"] = token
        elif token == "EMPTY_LIST":
            token_to_symbol["empty list"] = token
            token_to_symbol["empty"] = token
        else:
            token_to_symbol[token] = token


    # this is a horrid hack for now - should be implemented as a negative list
    token_to_symbol["end for"] = "NOT_A_TOKEN"
    token_to_symbol["end if"] = "NOT_A_TOKEN"
    token_to_symbol["end the if"] = "NOT_A_TOKEN"
    token_to_symbol["end the for"] = "NOT_A_TOKEN"
    token_to_symbol["increment"] = "+ ="
    token_to_symbol["decrement"] = "- ="
    token_to_symbol["different than"] = "! ="
    token_to_symbol["position"] = "index"
    token_to_symbol["location"] = "index"
    token_to_symbol["key"] = "index"
    token_to_symbol["otherwise"] = "else"

    return token_to_symbol

if __name__ == "__main__":
    print()
    print()
    print(get_pseudocode_tokens())
