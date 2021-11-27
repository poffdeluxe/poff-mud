# Poff MUD

This is a derivative project that makes use of [MUD PI](https://github.com/Frimkron/mud-pi) (for the python telnet connection), [QuickMUD/Merc/Diku (for content/game engine)](https://github.com/avinson/rom24-quickmud/), and my own ideas for the rest :)

## License
Very important -- license info is in the `license/` directory. This directory contains licenses for the aforementioned software.

I did not create the areas or a lot of the content/ruleset stuff! Please checkout the [Rom2.4 QuickMUD repo](https://github.com/avinson/rom24-quickmud/) for more info.

## Getting Started
Python 3.9 is required

1. Run `python3 -m venv venv` to create the environment
2. Run `source venv/bin/activate`
3. Install dependencies with `pip install -r requirements.txt`

Now, with the environment activated, you can run `python simplemud.py` to boot the MUD server. You can access the server by running `telnet localhost 1234` (Server by default runs on port 1234)

Or you can run `python area_load_test.py` to a simple debug script that loads the midgaard and school areas and prints their rooms, objects, mobiles, and resets.

## TODO
Lots.

Players that log in to the server are not saved (I think I'd like to store players and some other game state in postgres)

I'm currently loading most of the data contained in the area file (currently missing shops and specials)

Next goal is to add RPG game mechanics like MOB actions and combat.