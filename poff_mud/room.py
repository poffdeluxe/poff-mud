from enum import Enum
from poff_mud.enum_contains import EnumContains
from poff_mud.file_helpers import (
    read_number,
    read_string,
    read_flagset,
    read_until_tilde,
    read_letter,
)


class RoomFlag(Enum, metaclass=EnumContains):
    DARK = "A"  # (A)  A light source must be carried to see in this room
    NO_MOB = "C"  # (C)  Monsters cannot enter this room
    INDOORS = "D"  # (D)  Room is inside (i.e. not affected by weather)
    PRIVATE = "J"  # (J)  Room is limited to two characters (i.e. chat rooms)
    SAFE = "K"  # (K)  Safe from pkilling and aggressive mobs
    SOLITARY = "L"  # (L)  One character only can enter this room
    PET_SHOP = "M"  # (M)  see addendum about pet shops
    NO_RECALL = "N"  # (N)  players cannot use the 'recall' command to leave this room

    # These are flags not described in Rom2.4 Doc... :weary:
    IMP_ONLY = "O"
    GODS_ONLY = "P"
    NEWBIES_ONLY = "R"
    LAW = "S"
    NOWHERE = "T"


class RoomSectorType(Enum, metaclass=EnumContains):
    INSIDE = "0"
    CITY = "1"
    FIELD = "2"
    FOREST = "3"
    HILLS = "4"
    MOUNTAIN = "5"
    WATER = "6"
    DEEP = "7"
    AIR = "9"
    DESERT = "10"


code_to_direction = [
    "north",  # 0
    "east",  # 1
    "south",  # 2
    "west",  # 3
    "up",  # 4
    "down",  # 5
]

exit_shorthand_to_dir = {"n": "north", "s": "south", "w": "west", "e": "east"}


class DoorState(Enum, metaclass=EnumContains):
    OPEN = 0
    CLOSED = 1
    CLOSED_AND_LOCKED = 2


class Room:
    def __init__(self):
        self.vnum = 0

        self.header = "Room"
        self.desc = "Starring Brie Larson"

        self.flags = []
        self.sector_type = "INSIDE"

        self.exits = {}

        self.extra = {}

        self.mana_recovery_adjust = 0
        self.health_recovery_adjust = 0

        self.clan = None
        self.owner = None

        # More state-y stuff
        self.players = []
        self.objects = []
        self.mobs = []

    def __repr__(self):
        return f"ROOM #{self.vnum}: {self.header} ({self.sector_type} - EXITS: {', '.join(self.exits.keys())})"

    @staticmethod
    def load_exit(fp, room):
        dir_num = read_number(fp)
        direction = code_to_direction[dir_num]

        desc = read_until_tilde(fp)
        raw_keywords = read_until_tilde(fp)

        door_state = read_number(fp)
        key_vnum = read_number(fp)
        exit_vnum = str(read_number(fp))

        room.exits[direction] = {
            "look_description": desc,
            "door_keywords": raw_keywords.split(" ") if raw_keywords != "" else None,
            "door_state": DoorState(door_state),
            "key_vnum": str(key_vnum)
            if key_vnum > 0
            else None,  # 0 denotes not a door and -1 means there's no key
            "exit_vnum": exit_vnum,
        }

    @classmethod
    def load_from_file(cls, fp):
        room = cls()

        vnum = fp.readline()
        vnum = vnum.strip()
        vnum = vnum[1:]  # Remove leading #-sign
        room.vnum = vnum

        room.header = read_until_tilde(fp)
        room.desc = read_until_tilde(fp)

        # First set of flags are old and can be ignored
        read_flagset(fp)

        raw_room_flags = read_flagset(fp)
        for flag in raw_room_flags:
            if flag not in RoomFlag:
                continue

            room.flags.append(RoomFlag(flag))

        raw_sector_type = read_string(fp)
        room.sector_type = RoomSectorType(raw_sector_type)

        last_char = read_letter(fp)
        while last_char != "S":
            if last_char == "D":
                # Handle exit direction
                Room.load_exit(fp, room)
            elif last_char == "E":
                fp.read(1)

                # Handle extra description
                keyword_str = read_until_tilde(fp)
                keyword_str = keyword_str.strip()
                extra_keywords = keyword_str.split(" ")

                extra_desc = read_until_tilde(fp)

                for k in extra_keywords:
                    room.extra[k] = extra_desc

                # Combined case
                room.extra[keyword_str] = extra_desc
            elif last_char == "M":
                fp.read(1)

                # handle mana adjustment
                room.mana_recovery_adjust = read_number(fp)
            elif last_char == "H":
                fp.read(1)

                # handle HP adjustment
                room.hp_recovery_adjust = read_number(fp)
            elif last_char == "O":
                fp.read(1)

                # owner string
                room.owner = read_until_tilde(fp)
            elif last_char == "C":
                fp.read(1)

                # handle clan
                room.clan = read_until_tilde(fp)

            last_char = read_letter(fp)

        # If it's an S, we need to skip past the newline character
        fp.read(1)

        return room
