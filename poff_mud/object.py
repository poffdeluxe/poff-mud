from enum import Enum
from poff_mud.enum_contains import EnumContains
from poff_mud.file_helpers import (
    read_number,
    read_string,
    read_flagset,
    read_until_tilde,
    read_letter,
    peek_next_line,
)
from poff_mud.copyable import Copyable

from poff_mud.airv import IRVFlag, AffectFlag, AffectWhere, AffectLocation, Affect


class ObjectExtraFlag(Enum, metaclass=EnumContains):
    GLOWING = "A"
    HUMMING = "B"
    DARK = "C"
    EVIL = "E"
    INVIS = "F"
    MAGIC = "G"
    NODROP = "H"
    BLESS = "I"
    ANTIGOOD = "J"
    ANTIEVIL = "K"
    ANTINEUTRAL = "L"
    NOREMOVE = "M"
    INVENTORY = "N"
    NOPURGE = "O"
    ROTDEATH = "P"
    VISDEATH = "Q"
    NOSAC = "R"
    NOLOCATE = "T"
    MELTDROP = "U"
    SELLEXTRACT = "W"
    BURNPROOF = "Y"


class ObjectWearFlag(Enum, metaclass=EnumContains):
    TAKE = "A"
    FINGER = "B"
    NECK = "C"
    BODY = "D"
    HEAD = "E"
    LEGS = "F"
    FEET = "G"
    HANDS = "H"
    ARMS = "I"
    SHIELD = "J"
    ABOUTBODY = "K"
    WAIST = "L"
    WRIST = "M"
    WIELD = "N"
    HOLD = "O"
    FLOAT = "Q"


class ObjectWeaponFlag(Enum, metaclass=EnumContains):
    FLAMING = "A"
    FROST = "B"
    VAMPIRIC = "C"
    SHARP = "D"
    VORPAL = "E"
    TWOHANDED = "F"
    SHOCKING = "G"
    POISONED = "H"


class ObjectType(Enum, metaclass=EnumContains):
    WEAPON = "weapon"  # special values
    ARMOR = "armor"  # special values
    CONTAINER = "container"  # special values
    LIGHT = "light"  # special values
    FOOD = "food"  # special values
    DRINK = "drink"  # special values
    MONEY = "money"  # special values
    WAND = "wand"  # special values
    STAFF = "staff"  # special values
    POTION = "potion"  # special values
    SCROLL = "scroll"  # special values
    PILL = "pill"  # special values
    FURNITURE = "furniture"  # special values
    PORTAL = "portal"  # special values
    INNKEY = "innkey"
    CLOTHING = "clothing"
    FOUNTAIN = "fountain"  # special values
    KEY = "key"
    BOAT = "boat"
    MAP = "map"
    WARPSTONE = "warpstone"
    TREASURE = "treasure"
    JEWELRY = "jewelry"
    GEM = "gem"
    TRASH = "trash"
    JUKEBOX = "jukebox"  # Not documented..


code_to_condition = {"P": 100, "G": 90, "A": 75, "W": 50, "D": 25, "B": 10, "R": 0}


class Object(Copyable):
    def __init__(self):
        self.vnum = "###"
        self.keywords = []

        self.short_desc = ""
        self.long_desc = ""

        self.material = ""

        self.item_type = ObjectType.TRASH
        self.special_values = [0, 0, 0, 0, 0]  # Depend on item_type

        # Extra Flags
        self.extra_flags = []

        # Wear Flags
        self.wear_flags = []

        self.level = -1
        self.weight = -1
        self.cost = -1

        # Pristine, good, adequate, worn, damaged, broken, ruined
        self.condition = 100

        # Extra descriptions for given keyword
        # {keyword: description}
        self.extra_description = {}

        self.affects = []

        # If item is container, it can hold stuff
        self.contains = []

    def __repr__(self):
        return f"OBJ #{self.vnum}: {self.short_desc} ({self.item_type} - Level {self.level})"

    @classmethod
    def load_from_file(cls, fp):
        obj = cls()

        vnum = fp.readline()
        vnum = vnum.strip()
        vnum = vnum[1:]  # Remove leading #-sign
        obj.vnum = vnum

        keyword_str = read_until_tilde(fp)
        keyword_str = keyword_str.strip()
        obj.keywords = keyword_str.split(" ")

        obj.short_desc = read_until_tilde(fp)
        obj.long_desc = read_until_tilde(fp)

        obj.material = read_until_tilde(fp)

        obj.item_type = ObjectType(read_string(fp))

        raw_extra_flags = read_flagset(fp)
        for f in raw_extra_flags:
            obj.extra_flags.append(ObjectExtraFlag(f))

        raw_wear_flags = read_flagset(fp)
        for f in raw_wear_flags:
            obj.wear_flags.append(ObjectWearFlag(f))

        for i in [0, 1, 2, 3, 4]:
            raw_value = read_string(fp)
            if raw_value.isnumeric() and raw_value != "0":
                raw_value = int(raw_value)

            # Weapon special case (last value is weapon flags)
            if obj.item_type == "weapon" and i == 4:
                raw_weapon_tags = raw_value.split()
                weapon_flags = [ObjectWeaponFlag[f] for f in raw_wear_flags]

                obj.special_values[i] = weapon_flags
                continue

            obj.special_values[i] = raw_value

        obj.level = read_number(fp)
        obj.weight = read_number(fp)
        obj.cost = read_number(fp)

        cond_code = read_string(fp)
        obj.condition = code_to_condition[cond_code]

        # There's no delimter for each object and there can be
        # infinite E, F, or A entries so we need to consume
        # until we don't have an E, F, A entry
        next_line = peek_next_line(fp)
        next_line = next_line.strip()
        while next_line in ["E", "F", "A"]:
            # Advance the file pointer
            fp.readline()

            if next_line == "E":
                keyword_str = read_until_tilde(fp)
                keyword_str = keyword_str.strip()

                extra_desc = read_until_tilde(fp)

                for k in keyword_str.split(" "):
                    obj.extra_description[k] = extra_desc
            elif next_line == "F":
                aff = Affect()

                aff_type = read_string(fp)
                if aff_type == "A":
                    aff.where = AffectWhere.TO_AFFECTS
                elif aff_type == "I":
                    aff.where = AffectWhere.TO_IMMUNE
                elif aff_type == "R":
                    aff.where == AffectWhere.TO_RESIST
                elif aff_type == "V":
                    aff.where == AffectWhere.TO_VULN

                aff.level = obj.level

                location = read_number(fp)
                aff.location = (
                    AffectLocation(location) if location != 6 else AffectLocation.NONE
                )
                aff.modifier = read_number(fp)

                raw_flags = read_flagset(fp)
                if aff.where == AffectWhere.TO_AFFECTS:
                    aff.flags = [AffectFlag(f) for f in raw_flags]
                else:
                    aff.flags = [IRVFlag(f) for f in raw_flags]

                obj.affects.append(aff)
            elif next_line == "A":
                aff = Affect()
                aff.where = AffectWhere.TO_OBJECT
                aff.level = obj.level

                location = read_number(fp)
                aff.location = (
                    AffectLocation(location) if location != 6 else AffectLocation.NONE
                )

                aff.modifier = read_number(fp)

                obj.affects.append(aff)

            next_line = peek_next_line(fp)
            next_line = next_line.strip()

        return obj
