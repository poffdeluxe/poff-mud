from .base_command import BaseCommand


class SayCommand(BaseCommand):
    name = "say"
    keywords = ["say"]

    def execute(self, player, params, command_used):
        # go through every player in the game
        for p in self.gs.get_players_in_room(player["room"]):
            if p["id"] != player["id"]:
                # send them a message telling them what the player said
                self.mud.send_message(pid, "{} says: {}".format(player["name"], params))

        yield ""

    @property
    def help(self):
        return "This is the say command. Use say"
