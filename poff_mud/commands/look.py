from termcolor import colored

from poff_mud.room import code_to_direction, exit_shorthand_to_dir
from poff_mud.room_utils import get_room_display_str
from .base_command import BaseCommand


class LookCommand(BaseCommand):
    name = "look"
    keywords = ["l", "look"]

    def execute(self, player, params, command_used):
        # store the player's current room
        rm = self.gs.rooms[player["room"]]

        if params:
            # Look at mobs
            for m in rm.mobs:
                for kw in m.keywords:
                    if params == kw:
                        yield m.look_desc
                        return

            # Look at objects
            for o in rm.objects:
                for kw in o.extra_description:
                    if params == kw:
                        yield o.extra_description[kw]
                        return

            # TODO: Look at players

            # Look items in room (extra)
            if params in rm.extra:
                yield rm.extra[params]
                return

            # Look direction
            if params in code_to_direction or params in exit_shorthand_to_dir.keys():
                direction = exit_shorthand_to_dir.get(params, params)

                if direction in rm.exits:
                    yield rm.exits[direction]["look_description"]
                    # TODO: show door state too
                    return

            yield f"There's nothing called '{params}' to look at here..."
            return

        # No params so look in room
        yield get_room_display_str(rm, player, self.gs)

    @property
    def help(self):
        return "This is the look command. Use l or look"
