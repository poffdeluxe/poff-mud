from termcolor import colored


def get_room_display_str(room, player, gs):
    # send the player back the description of their current room
    display_str = f"""{colored(room.header, "cyan", attrs=["bold"])}\n"""
    display_str += f"{room.desc}\n"

    playershere = []
    # go through every player in the game
    for pid, pl in gs.players.items():
        # if they're in the same room as the player
        if gs.players[pid]["room"] == player["room"]:
            # ... and they have a name to be shown
            if gs.players[pid]["name"] is not None:
                name = gs.players[pid]["name"]
                if pid != player["id"]:
                    # add their name to the list
                    playershere.append(name)

    # send player a message containing the list of exits from this room
    exit_str = f"""[Exits: {", ".join(room.exits.keys())}]"""
    display_str += f"""{colored(exit_str, "yellow")}\n\n"""

    # send player a message containing the list of players in the room
    for player in playershere:
        display_str += f"{player} is here.\n"

    for mob in room.mobs:
        display_str += f"{mob.long_desc}\n"

    for obj in room.objects:
        display_str += f"{obj.long_desc}\n"

    return display_str
