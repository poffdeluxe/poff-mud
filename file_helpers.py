def read_until_tilde(fp):
    result = ""
    last_char = ""

    while True:
        last_char = fp.read(1)

        if last_char == "~":
            break
        elif last_char == "":
            # EOF
            return result

        result = result + last_char

    fp.read(1)  # Get past \n

    return result


def read_flagset(fp):
    flagset = []

    last_char = fp.read(1)
    while last_char not in [" ", "\n"]:
        if last_char != "0":
            flagset.append(last_char)

        last_char = fp.read(1)

    return flagset


def read_string(fp):
    result = ""

    last_char = fp.read(1)
    while last_char not in [" ", "\n"]:
        result = result + last_char

        last_char = fp.read(1)

    return result


def read_number(fp):
    result = ""

    last_char = fp.read(1)
    while last_char not in [" ", "\n"]:
        result = result + last_char

        last_char = fp.read(1)

    if result == "":
        return 0

    return int(result)


def read_letter(fp):
    """Read the next A-Z letter"""
    last_char = fp.read(1)
    while last_char in [" ", "\n"] and last_char.isnumeric():
        last_char = fp.read(1)

    if last_char == "":
        return ""

    # CAREFUL! This does not move past the next whitespace/newline
    return last_char
