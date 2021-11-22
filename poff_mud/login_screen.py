from termcolor import colored, cprint

welcome = [
    " ____   __  ____  ____  _  _  _  _  ____ ",
    "(  _ \\ /  \\(  __)(  __)( \\/ )/ )( \\(    \\",
    " ) __/(  O )) _)  ) _) / \\/ \\) \\/ ( ) D (",
    "(__)   \\__/(__)  (__)  \\_)(_/\\____/(____/",
]


def send_login_welcome(mud_server, id):
    mud_server.send_message(id, "Welcome to...")

    for row in welcome:
        mud_server.send_message(id, colored(row, "red"))

    mud_server.send_message(id, "")
    mud_server.send_message(id, colored("What is your name?", "cyan", attrs=["bold"]))
