from termcolor import colored


def get_room_display_str(room, player, gs):
    # send the player back the description of their current room
    display_str = f"""{colored(room.header, "cyan", attrs=["bold"])}\n"""
    display_str += f"{room.desc}\n\n"

    playershere = []
    # go through every player in the game
    for pid, pl in gs.players.items():
        # if they're in the same room as the player
        if gs.players[pid]["room"] == player["room"]:
            # ... and they have a name to be shown
            if gs.players[pid]["name"] is not None:
                name = gs.players[pid]["name"]

                if pid == player["id"]:
                    name += " (you)"

                # add their name to the list
                playershere.append(name)

    # send player a message containing the list of players in the room
    display_str += f"""Players here: {", ".join(playershere)}\n"""

    # send player a message containing the list of exits from this room
    display_str += f"""Exits are: {", ".join(room.exits.keys())}\n"""

    return display_str
