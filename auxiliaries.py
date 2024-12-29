import re

# Regular expression to keep alphabetic characters and commas

def cleanse_string(s):
    return re.sub(r"[^a-zA-Z,]+", " ", s)


def parse_cell(cell):
    w = cleanse_string(cell)
    result = [ω.strip().upper() for ω in w.split(",") ]
    result = [ω for ω in result if len(ω) > 0]
    return(result)

def cell_check(cell, valid_entries):

    parsed = parse_cell(cell)
    return any([β not in valid_entries for β in parsed])

def validate_keys(keys):
    if any([not key.isupper() for key in keys]) or any("," in key for key in keys):
        warning = """WARNING: Some keys are either not upper case or contain commas. This has the
        potential of causing errors in the parsing of the columns."""
        print(warning)
    pass

