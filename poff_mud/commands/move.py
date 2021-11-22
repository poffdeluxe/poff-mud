from .base_command import BaseCommand

shorthand_to_dir = {"n": "north", "s": "south", "w": "west", "e": "east"}


class MoveCommand(BaseCommand):
    name = "move"
    keywords = [
        "north",
        "n",
        "south",
        "s",
        "east",
        "e",
        "west",
        "w",
        "up",
        "down",
        "inside",
        "outside",
        "go",
    ]

    def execute(self, player, params, command_used):
        ex = command_used

        if command_used == "go":
            # TODO: Check to make sure params is around when using go
            ex = params.lower()

        # store the player's current room
        rm = self.gs.rooms[player["room"]]

        ex = shorthand_to_dir.get(ex, ex)

        # if the specified exit is found in the room's exits list
        if ex in rm["exits"]:

            # go through all the gs.players in the game
            for pid, pl in self.gs.players.items():
                # if player is in the same room and isn't the player
                # sending the command
                if (
                    self.gs.players[pid]["room"] == player["room"]
                    and pid != player["id"]
                ):
                    # send them a message telling them that the player
                    # left the room
                    yield "{} left via exit '{}'".format(player["name"], ex)

            # update the player's current room to the one the exit leads to
            player["room"] = rm["exits"][ex]
            rm = self.gs.rooms[player["room"]]

            # go through all the players in the game
            for pid, pl in self.gs.players.items():
                # if player is in the same (new) room and isn't the player
                # sending the command
                if (
                    self.gs.players[pid]["room"] == player["room"]
                    and pid != player["id"]
                ):
                    # send them a message telling them that the player
                    # entered the room
                    self.mud.send_message(
                        pid, f"{player['name']} arrived via exit '{ex}'"
                    )

            # send the player a message telling them where they are now
            yield "You arrive at '{}'".format(player["room"])

        # the specified exit wasn't found in the current room
        else:
            # send back an 'unknown exit' message
            yield "Unknown exit '{}'".format(ex)

    @property
    def help(self):
        return "This is the movement command. Use l or look"
