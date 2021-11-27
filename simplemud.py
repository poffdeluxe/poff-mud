#!/usr/bin/env python

import time
from signal import signal, SIGINT
from sys import exit
from termcolor import colored

# import the MUD server class
from mudserver import MudServer

from poff_mud.spawn_pool import SpawnPool
from poff_mud.gamestate import GameState
from poff_mud.commands import LookCommand, MoveCommand, SayCommand
from poff_mud.login_screen import send_login_welcome
from poff_mud.timer import TimerManager

from poff_mud.area import Area
from poff_mud.room_utils import get_room_display_str

if __name__ == "__main__":
    # Create the global spawn pool
    gsp = SpawnPool()

    areas = []

    # Load in school
    with open("areas/school.are") as fp:
        school_area = Area.load_from_file(fp, gsp=gsp)
        areas.append(school_area)

    # Load in midgaard
    with open("areas/midgaard.are") as fp:
        midgaard_area = Area.load_from_file(fp, gsp=gsp)
        areas.append(midgaard_area)

    # setup game state and add rooms 
    gs = GameState()
    gs.rooms = {}
    for a in areas:
        for room_vnum in a.rooms:
            gs.rooms[room_vnum] = a.rooms[room_vnum]

        a.reset(gsp)

    # stores the players in the game
    gs.players = {}

    # manages timers in our main loop
    gs.timer_manager = TimerManager()

    # start the server
    mud = MudServer()

    # build command look-up map
    commands = [LookCommand(gs, mud), MoveCommand(gs, mud), SayCommand(gs, mud)]
    commands_lookup = {}

    for c in commands:
        for keyword in c.keywords:
            if keyword in commands_lookup:
                print(f"Warning: keyword {keyword} already registered")
                continue

            commands_lookup[keyword] = c

    def shutdown_callback():
        mud.send_global_message(colored("Shutdown commencing. Until next time.", "red"))
        mud.shutdown()
        exit(0)

    def shutdown_handler(signal_received, frame):
        mud.send_global_message(
            colored(
                "Server will shutdown in 5 seconds... GET PREPARED.",
                "red",
                attrs=["bold"],
            )
        )
        gs.timer_manager.add_timer(5000, shutdown_callback)

    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, shutdown_handler)

    # main game loop. We loop forever (i.e. until the program is terminated)
    while True:
        # pause for 1/5 of a second on each loop, so that we don't constantly
        # use 100% CPU time
        time.sleep(0.2)

        # 'update' must be called in the loop to keep the game running and give
        # us up-to-date information
        mud.update()

        gs.timer_manager.run()

        # go through any newly connected players
        for id in mud.get_new_players():

            # add the new player to the dictionary, noting that they've not been
            # named yet.
            # The dictionary key is the player's id number. We set their room to
            # None initially until they have entered a name
            # Try adding more player stats - level, gold, inventory, etc
            gs.players[id] = {
                "name": None,
                "room": None,
                "id": id,
            }

            # send the new player a prompt for their name
            send_login_welcome(mud, id)

        # go through any recently disconnected players
        for id in mud.get_disconnected_players():

            # if for any reason the player isn't in the player map, skip them and
            # move on to the next one
            if id not in gs.players:
                continue

            # go through all the players in the game
            for pid, pl in gs.players.items():
                # send each player a message to tell them about the diconnected
                # player
                mud.send_message(pid, "{} quit the game".format(gs.players[id]["name"]))

            # remove the player's entry in the player dictionary
            del gs.players[id]

        # go through any new commands sent from players
        for id, command, params in mud.get_commands():
            try:
                # if for any reason the player isn't in the player map, skip them and
                # move on to the next one
                if id not in gs.players:
                    continue

                cmd_player = gs.players[id]

                mud.send_message(id, "")

                # if the player hasn't given their name yet, use this first command as
                # their name and move them to the starting room.
                if gs.players[id]["name"] is None:

                    gs.players[id]["name"] = command
                    gs.players[id]["room"] = "3700"

                    # go through all the players in the game
                    for pid, pl in gs.players.items():
                        # send each player a message to tell them about the new player
                        mud.send_message(
                            pid, "{} entered the game".format(gs.players[id]["name"])
                        )

                    # send the new player a welcome message
                    mud.send_message(
                        id,
                        "Welcome to the game, {}. ".format(gs.players[id]["name"])
                        + "Type 'help' for a list of commands. Have fun!\n",
                    )

                    # send the new player the description of their current room
                    rm = gs.rooms[gs.players[id]["room"]]
                    mud.send_message(id, get_room_display_str(rm, gs.players[id], gs))

                elif command in commands_lookup:
                    c = commands_lookup[command]

                    # execute yields strings to pass on to the client
                    for msg in c.execute(cmd_player, params, command):
                        mud.send_message(id, msg)
                # 'help' command
                elif command == "help":

                    # send the player back the list of possible commands
                    mud.send_message(id, "Commands:")
                    mud.send_message(
                        id,
                        "  say <message>  - Says something out loud, "
                        + "e.g. 'say Hello'",
                    )
                    mud.send_message(
                        id,
                        "  look           - Examines the "
                        + "surroundings, e.g. 'look'",
                    )
                    mud.send_message(
                        id,
                        "  go <exit>      - Moves through the exit "
                        + "specified, e.g. 'go outside'",
                    )
                    mud.send_message(
                        id, "  quit      - Quit and log out of the PoffMUD"
                    )
                elif command == "quit":

                    mud.send_message(id, f"Goodbye {cmd_player['name']}...")
                    mud.disconnect_client(id)

                # some other, unrecognised command
                else:
                    # send back an 'unknown command' message
                    mud.send_message(id, "Unknown command '{}'".format(command))

            except Exception as e:
                print(e)
                raise e
