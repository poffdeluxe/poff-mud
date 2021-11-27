def peek_next_line(fp):
    pos = fp.tell()
    line = fp.readline()
    fp.seek(pos)

    return line


def read_until_delimiter(fp, demlimiter):
    result = ""
    last_char = ""

    # Skip through until we get to actual data
    while last_char in [" ", "\n"]:
        last_char = fp.read(1)

    while True:
        last_char = fp.read(1)

        if last_char == demlimiter:
            break
        elif last_char == "":
            # EOF
            return result

        result = result + last_char

    return result


def read_until_tilde(fp):
    result = read_until_delimiter(fp, "~")

    # TODO: This next line is a little hacky and might
    # cause confusion as we read one more character in order
    # to skip past the newline character or a space after the tilde.
    # This works for the use case of the area files since there is
    # almost always one of those delimter characters following the tilde
    fp.read(1)

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

    # Skip through until we get to actual data
    while last_char in [" ", "\n"]:
        last_char = fp.read(1)

    quote_mode = False
    while quote_mode or last_char not in [" ", "\n"]:
        if last_char == "'":
            quote_mode = not quote_mode
        else:
            result = result + last_char

        last_char = fp.read(1)

    return result


def read_number(fp, delimiter_group=[" ", "\n"]):
    result = ""

    last_char = fp.read(1)

    # Skip through until we get to actual data
    while last_char in [" ", "\n"]:
        last_char = fp.read(1)

    while last_char not in delimiter_group:
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
