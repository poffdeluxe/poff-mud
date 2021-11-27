from enum import Enum


class AffectFlag(Enum):
    BLIND = "A"  # *
    INVIS = "B"

    DETECTEVIL = "C"
    DETECTINVIS = "D"
    DETECTMAGIC = "E"
    DETECTHIDDEN = "F"
    DETECTGOOD = "G"

    SANCTUARY = "H"
    FAERIEFIRE = "I"  # *
    INFRARED = "J"
    CURSE = "K"
    FLAMING = "L"
    POISONED = "M"  # *)

    PROTEVIL = "N"
    PROTGOOD = "O"

    SNEAK = "P"
    HIDE = "Q"

    SLEEP = "R"  # *
    CHARM = "S"  # *

    FLYING = "T"
    PASSDOOR = "U"
    HASTE = "V"

    CALM = "W"  # *
    PLAGUE = "X"  # *
    WEAKEN = "Y"  # *
    DARKVIS = "Z"
    BESERK = "a"  # *
    SWIM = "b"
    REGEN = "c"
    SLOW = "d"
    # * items will be detrimental to the character, possibly for cursed items.


# Immune, Resist, Vulnerability Flags
# Describes types of damage that a character
# might be more or less resistant to
class IRVFlag(Enum):
    SUMMON = "A"  # Summoning and gating magic
    CHARM = "B"  # Charm spells (the beguiling spell group)
    MAGIC = "C"  # All magic (be very careful using this flag)

    WEAPONS = "D"  # All physical attacks (be very careful using this flag)
    BASH = "E"  # Blunt weapons
    PIERCE = "F"  # Piercing weapons
    SLASH = "G"  # Slashing weapons

    FIRE = "H"  # Flame and heat attacks and spells
    COLD = "I"  # Cold and ice attacks and spells
    LIGHTNING = "J"  # Electrical attacks and spells
    ACID = "K"  # Corrosive attacks and spells
    POISON = "L"  # Venoms and toxic vapors
    NEGATIVE = "M"  # Life draining attacks and spells, or unholy energies
    HOLY = "N"  # Holy or blessed attacks
    ENERGY = "O"  # Generic magical force (i.e. magic missile)
    MENTAL = "P"  # Mental attacks (such as a mind flayer's mind blasts)
    DISEASE = "Q"  # Disease, from the common cold to the black death
    DROWNING = "R"  # Watery attacks and suffocation

    LIGHT = "S"  # Light-based attacks, whether blinding or cutting
    SOUND = "T"  # Sonic attacks and weapons, or deafening noises
    WOOD = "X"  # Wooden weapons and creatures
    SILVER = "Y"  # Silver or mithril weapons and creatures
    IRON = "Z"  # Iron and steel weapons and creatures


class AffectWhere(Enum):
    TO_OBJECT = 0
    TO_AFFECTS = 1
    TO_IMMUNE = 2
    TO_RESIST = 3
    TO_VULN = 4


class AffectLocation(Enum):
    NONE = 0
    STRENGTH = 1
    DEXTERITY = 2
    INTELLIGENCE = 3
    WISDOM = 4
    CONSTITUTION = 5
    # SEX = 6 # ??? I'm gonna drop this I think - Poff
    CHARISMA = 7
    MANA = 12
    HITPOINTS = 13
    MOVEMENT = 14
    AC = 17
    HITROLL = 18
    DAMROLL = 19
    SPELL = 20


class Affect:
    def __init__(self):
        self.where = AffectWhere.TO_AFFECTS

        self.type = -1  # Unknown what this does yet

        self.level = 1

        self.duration = -1
        self.timer = None

        self.location = AffectLocation.NONE
        self.modifier = 0

        self.flags = []  # Could be IRV flags or Affect flags
