from enum import Enum
from poff_mud.file_helpers import (
    read_number,
    read_string,
    read_flagset,
    read_until_tilde,
    read_letter,
)

code_to_room_flag = {
    "A": "DARK",  # (A)  A light source must be carried to see in this room
    "C": "NO_MOB",  # (C)  Monsters cannot enter this room
    "D": "INDOORS",  # (D)  Room is inside (i.e. not affected by weather)
    "J": "PRIVATE",  # (J)  Room is limited to two characters (i.e. chat rooms)
    "K": "SAFE",  # (K)  Safe from pkilling and aggressive mobs
    "L": "SOLITARY",  # (L)  One character only can enter this room
    "M": "PET_SHOP",  # (M)  see addendum about pet shops
    "N": "NO_RECALL",  # (N)  players cannot use the 'recall' command to leave this room
    # These are flags not described in Rom2.4 Doc... :weary:
    "O": "IMP_ONLY",
    "P": "GODS_ONLY",
    "R": "NEWBIES_ONLY",
    "S": "LAW",
    "T": "NOWHERE",
}

code_to_sector_type = {
    "0": "INSIDE",
    "1": "CITY",
    "2": "FIELD",
    "3": "FOREST",
    "4": "HILLS",
    "5": "MOUNTAIN",
    "6": "WATER",
    "7": "DEEP WATER",
    "9": "AIR",
    "10": "DESERT",
}

code_to_direction = [
    "north",  # 0
    "east",  # 1
    "south",  # 2
    "west",  # 3
    "up",  # 4
    "down",  # 5
]


class DoorState(Enum):
    OPEN = 0
    CLOSED = 1
    CLOSED_AND_LOCKED = 2


class Room:
    def __init__(self):
        self.vnum = 0

        self.header = "The Room"
        self.desc = "Starring Brie Larson"

        self.flags = []
        self.sector_type = "INSIDE"

        self.exits = {}

        self.extra = {}

        self.mana_recovery_adjust = 0
        self.health_recovery_adjust = 0

        self.clan = None
        self.owner = None

    @staticmethod
    def load_exit(fp, room):
        dir_num = read_number(fp)
        direction = code_to_direction[dir_num]

        desc = read_until_tilde(fp)
        raw_keywords = read_until_tilde(fp)

        door_state = read_number(fp)
        key_vnum = read_number(fp)
        exit_vnum = read_number(fp)

        room.exits[direction] = {
            "look_description": desc,
            "door_keywords": raw_keywords.split(" ") if raw_keywords != "" else None,
            "door_state": DoorState(door_state),
            "key_vnum": key_vnum
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
            room.flags = code_to_room_flag[flag]

        raw_sector_types = read_flagset(fp)
        # TODO: come on fix this. It's ugly as hell!
        room.sector_type = code_to_sector_type.get(
            raw_sector_types[0] if len(raw_sector_types) else 0, "INSIDE"
        )

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
