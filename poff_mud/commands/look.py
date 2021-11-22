from .base_command import BaseCommand


class LookCommand(BaseCommand):
    name = "look"
    keywords = ["l", "look"]

    def execute(self, player, params, command_used):
        # store the player's current room
        rm = self.gs.rooms[player["room"]]

        # send the player back the description of their current room
        yield rm["description"]

        playershere = []
        # go through every player in the game
        for pid, pl in self.gs.players.items():
            # if they're in the same room as the player
            if self.gs.players[pid]["room"] == player["room"]:
                # ... and they have a name to be shown
                if self.gs.players[pid]["name"] is not None:
                    # add their name to the list
                    playershere.append(self.gs.players[pid]["name"])

        # send player a message containing the list of players in the room
        yield "Players here: {}".format(", ".join(playershere))

        # send player a message containing the list of exits from this room
        yield "Exits are: {}".format(", ".join(rm["exits"]))

    @property
    def help(self):
        return "This is the look command. Use l or look"
