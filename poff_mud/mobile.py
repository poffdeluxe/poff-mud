from enum import Enum
from copy import deepcopy

from poff_mud.file_helpers import (
    read_number,
    read_string,
    read_flagset,
    read_until_tilde,
)
from poff_mud.character import Character
from poff_mud.copyable import Copyable
from poff_mud.airv import IRVFlag

specific_to_general_damage = {
    "bite": "pierce",
    "chomp": "pierce",
    "peck": "pierce",
    "pierce": "pierce",
    "scratch": "pierce",
    "stab": "pierce",
    "sting": "pierce",
    "thrust": "pierce",
    "beating": "bash",
    "blast": "bash",
    "pound": "bash",
    "charge": "bash",
    "crush": "bash",
    "peckb": "bash",
    "punch": "bash",
    "slap": "bash",
    "smash": "bash",
    "suction": "bash",
    "thwack": "bash",
    "claw": "slash",
    "cleave": "slash",
    "grep": "slash",
    "slash": "slash",
    "slice": "slash",
    "whip": "slash",
    "acbite": "magic",  # Acid
    "digestion": "magic",  # Acid
    "slime": "magic",  # Acid
    "frbite": "magic",  # Cold
    "chill": "magic",  # Cold
    "magic": "magic",  # Energy
    "wratch": "magic",  # Energy
    "flame": "magic",
    "flbite": "magic",
    "divine": "magic",
    "shock": "magic",
    "shbite": "magic",
    "drain": "magic",
}

code_to_act_flag = {
    "A": "NPC",  # Mobile is an NPC (set automatically by the game)
    "B": "sentinel",  # Mobile doesn't wander
    "C": "scavenger",  # Mobile picks up items on the floor
    "F": "aggressive",  # Mobile attacks any character in the same room (see the section dealing with aggression)
    "G": "stay area",  # Mobile will not, leave a zone (this should be set)
    "H": "wimpy",  # Mobile will fly when badly hurt
    "I": "pet",  # Mobile is a pet (and hence safe from attack)
    "J": "train",  # Mobile can train statistics
    "K": "practice",  # Mobile can practice statistics
    "O": "undead",  # Mobile has special undead powers (i.e. life draining)
    "Q": "cleric",  # Mobile has cleric casting powers
    "R": "mage",  # Mobile has mage casting powers
    "S": "thief",  # Mobile has thief combat skills (backstab, etc.)
    "T": "warrior",  # Mobile has warrior combat skills (disarm, parry, etc.)
    "U": "noalign",  # Mobile is unaligned (unintelligent animals, golems, etc.)
    "V": "nopurge",  # Mobile isn't removed by the purge command
    "W": "outdoors",  # Mobile will not wander outside a building
    "Y": "indoors",  # Mobile will not wander into a building
    "a": "healer",  # Mobile can heal characters (i.e. the heal command)
    "b": "gain",  # Mobile can grant new skills (i.e. the gain command)
    "c": "update",  # Mobile is always updated, even in idle zones (rarely needed)
    "d": "changer",  # Mobile can change coins (i.e. Otho the Money Changer)
}

code_to_affect_flag = {
    "B": "invisible",  # Mobile is invisible
    "C": "detect evil",  # Mobile can sense evil
    "D": "detect invis",  # Mobile can see invisible. **
    "E": "detect magic",  # Mobile can see magic
    "F": "detect hide",  # Mobile can see hidden (sneaking/hiding) characters
    "G": "detect good",  # Mobile can sense good
    "H": "sanctuary",  # Mobile is protected by a sanctuary spell. **
    "I": "faerie fire",  # Mobile is surrounded by faerie fire (a hindrance)
    "J": "infravision",  # Mobile can see heat sources in the dark
    "N": "protect evil",  # Mobile takes less damage from evil characters
    "O": "protect good",  # Mobile takes less damage from good characters
    "P": "sneaking",  # Mobile is sneaking (hard to detect while moving)
    "Q": "hiding",  # Mobile is hiding (cannot be seen without detect hidden)
    "T": "flying",  # Mobile is flying
    "U": "pass door",  # Mobile can walk through closed doors
    "V": "haste",  # Mobile is affected by a haste spell
    "Z": "dark vision",  # Mobile can see in the dark without a light source
    "b": "swimming",  # Mobile is swimming (or capable of swimming)
    "c": "regeneration",  # Mobile recovers hit points and mana faster than usual
}

code_to_offensive_flag = {
    "A": "area attack",  # Mobile hits all characters fighting against it. Very powerful.
    "B": "backstab",  # Mobile can backstab to start a combat
    "C": "bash",  # Mobile can bash characters off their feet
    "D": "berserk",  # Mobile may go berserk in a fight
    "E": "disarm",  # Mobile can disarm _without_ a weapon wielded**
    "F": "dodge",  # Mobile dodges blows
    "G": "fade",  # Mobile can fade "out of phase" to avoid blows
    "H": "fast",  # Mobile is faster than most others, so has extra attacks
    "I": "kick",  # Mobile can kick in combat for extra damage
    "J": "kick dirt",  # Mobile kicks dirt, blinding opponents
    "K": "parry",  # Mobile can parry _without_ a weapon wielded**
    "L": "rescue",  # Mobile may rescue allies in a fight
    "M": "tail",  # Mobile can legsweep with its tail or tentacles
    "N": "trip",  # Mobile trips in combat
    "O": "crush",  # Mobile can crush opponents in its arms
    "P": "all",  # Mobile helps all other mobiles in combat
    "Q": "align",  # Mobile assists mobiles of like alignment
    "R": "race",  # Mobile will assist other mobiles of the same race
    "S": "players",  # Mobile will assist players (by race/alignment)
    "T": "guard",  # Mobile assists as a cityguard
    "U": "vnum",  # Mobile assists mobiles of the same number only
}

code_to_form_flag = {
    # Corpse flags
    "A": "edible",  # Mobile can be eaten
    "B": "poison",  # Mobile is poisonous when eaten (should also be edible)
    "C": "magical",  # Mobile's magic nature causes strange effects when eaten
    "D": "vanishes",  # Mobile vanishes after death (i.e. a wraith)
    "E": "other",  # Mobile is not flesh and blood (defined by material type)
    # Form flags
    "G": "animal",  # Mobile is a "dumb" animal
    "H": "sentient",  # Mobile is capable of higher reasoning
    "I": "undead",  # Mobile is an undead, and not truly alive at all
    "J": "construct",  # Mobile is a magical construct, such as a golem
    "K": "mist",  # Mobile is a partially material mist
    "L": "intangible",  # Mobile is immaterial (like a ghost)
    "M": "biped",  # Mobile is bipedal (like a human)
    "N": "centaur",  # Mobile has a humanoid torso, but a beast's lower body
    "O": "insect",  # Mobile is an insect
    "P": "spider",  # Mobile is an arachnid
    "Q": "crustacean",  # Mobile is a crustacean (i.e. a crab or lobster)
    "R": "worm",  # Mobile is a worm, that is a tube-shaped invertebrate
    "S": "blob",  # Mobile is a formless blob (when used with mist, a cloud)
    "V": "mammal",  # Mobile is a mammal
    "W": "bird",  # Mobile is a bird
    "X": "reptile",  # Mobile is a reptile (and should be cold-blooded)
    "Y": "snake",  # Mobile is a snake (and should be a reptile)
    "Z": "dragon",  # Mobile is a dragon
    "a": "amphibian",  # Mobile is an amphibian (and should be able to swim)
    "b": "fish",  # Mobile is a fish (and should be able to swim)
    "c": "cold blood",  # Mobile is cold-blooded, cannot be seen with infravis.
}

code_to_parts_flag = {
    "A": "head",  # Mobile has a head
    "B": "arms",  # Mobile has arm(s) (usually assumed to be 2)
    "C": "legs",  # Mobile has leg(s)
    "D": "heart",  # Mobile has a heart
    "E": "brains",  # Mobile has brains (not all mobs with heads have brains)
    "F": "guts",  # Mobile has intestines
    "G": "hands",  # Mobile has hands capable of manipulating objects
    "H": "feet",  # Mobile has feet
    "I": "fingers",  # Mobile has fingers capable of wearing rings
    "J": "ear",  # Mobile has ear(s)
    "K": "eye",  # Mobile has eye(s)
    "L": "tongue",  # Mobile has a _long_ tongue (like a lizard)
    "M": "eyestalks",  # Mobile has eyestalks (it should also have eyes)
    "N": "tentacles",  # Mobile has one or more tentacles
    "O": "fins",  # Mobile has fins
    "P": "wings",  # Mobile has wings
    "Q": "tail",  # Mobile has a usable tail (no stubs)
    "U": "claws",  # Mobile has combat-capable claws
    "V": "fangs",  # Mobile has combat-capable teeth
    "W": "horns",  # Mobile has horns, not necessarily dangerous ones
    "X": "scales",  # Mobile is covered with scales
    "Y": "tusks",  # Mobile has some teeth elongated into tusks
}

# ZX01 - VNUM
# Sample~ - Name list
# Sample~ - short description
# A sample mobile is here, waiting for a face. - longer
# ~
# It looks bland and boring, and like it belongs nowhere near an area
# file, but is a good example of a mobile.
# ~ look
# human~ race
# ABTV <-act CDFJVZ <-effect  1000 <-alignment 3000 <-mob group
# 45 <level- 30 <+ ot hit> 1d1+3999<hit dice> 1d1+499 <mana< 5d4+40 <damage> crush <damage type>
# -25 <pierce ac> -25 <bash ac> -25 <splash ac> -15 <magic ac>
# ACDEFHIKLNOT <offsnive flags> ABP <immunities> CD <resistance> 0 <vuln>
# stand <start pos > stand <default pos>  either <sex> 0 <treasure>
# 0 <form flags> 0 <part flags> medium <size> 0 <material>


class Mobile(Copyable, Character):
    def __init__(self):
        Character.__init__(self)

        self.vnum = ""
        # self.id = uuid

        self.keywords = []
        self.short_desc = ""
        self.long_desc = ""
        self.look_desc = ""

        self.race = "human"

        self.act_flags = []
        self.affect_flags = []
        self.alignment = 0  # -1000 (satan) to 1000 (saintly)

        self.mob_group = None  # New
        self.area_mob_group = None  # Old -- match up with area

        self.level = 1
        self.bonus_to_hit = 0

        self.hit_dice = "1d1+1"
        self.mana_dice = "1d1+1"
        self.dmg_dice = "1d1+1"

        self.damage_type = "crush"

        self.ac = {"pierce": -25, "bash": -25, "slash": -15, "magic": -15}

        self.offensive_flags = []
        self.immunity_flags = []
        self.resistance_flags = []
        self.vulnerability_flags = []

        self.start_pos = "stand"
        self.default_pos = "stand"

        self.current_pos = self.start_pos

        self.treasure = 0  # In silver pieces

        self.form_flags = []
        self.parts_flags = []

        self.size = "medium"

        self.material = None

    def __repr__(self):
        return f"MOB #{self.vnum}: {self.short_desc} (Level {self.level})"

    def has_act_flag(self, act_flag):
        return act_flag in self.act_flags

    @classmethod
    def load_from_file(cls, fp):
        mob = cls()

        vnum = fp.readline()
        vnum = vnum.strip()
        vnum = vnum[1:]  # Remove leading #-sign
        mob.vnum = vnum

        keyword_str = read_until_tilde(fp)
        keyword_str = keyword_str.strip()
        mob.keywords = keyword_str.split(" ")

        mob.short_desc = read_until_tilde(fp)
        mob.long_desc = read_until_tilde(fp)
        mob.look_desc = read_until_tilde(fp)

        mob.race = read_until_tilde(fp)

        # TODO: act and affect (and maybe other flags) are affected by
        # race
        raw_act_flags = read_flagset(fp)
        for flag_code in raw_act_flags:
            mob.act_flags.append(code_to_act_flag[flag_code])

        raw_affect_flags = read_flagset(fp)
        for flag_code in raw_affect_flags:
            mob.affect_flags.append(code_to_affect_flag[flag_code])

        mob.alignment = read_number(fp)
        mob.area_mob_group = read_number(fp)

        mob.level = read_number(fp)
        mob.bonus_to_hit = read_number(fp)

        mob.hit_dice = read_string(fp)
        mob.mana_dice = read_string(fp)
        mob.dmg_dice = read_string(fp)
        mob.damage_type = read_string(fp)

        mob.ac["pierce"] = read_number(fp)
        mob.ac["bash"] = read_number(fp)
        mob.ac["slash"] = read_number(fp)
        mob.ac["magic"] = read_number(fp)

        raw_off_flags = read_flagset(fp)
        for flag_code in raw_off_flags:
            mob.offensive_flags.append(code_to_offensive_flag[flag_code])

        raw_imm_flags = read_flagset(fp)
        for flag_code in raw_imm_flags:
            mob.immunity_flags.append(IRVFlag(flag_code))

        raw_res_flags = read_flagset(fp)
        for flag_code in raw_res_flags:
            mob.resistance_flags.append(IRVFlag(flag_code))

        raw_vul_flags = read_flagset(fp)
        for flag_code in raw_vul_flags:
            mob.vulnerability_flags.append(IRVFlag(flag_code))

        mob.start_pos = read_string(fp)
        mob.default_pos = read_string(fp)

        mob.current_pos = mob.start_pos

        read_string(fp)

        mob.treasure = read_number(fp)

        raw_form_flags = read_flagset(fp)
        for flag_code in raw_form_flags:
            mob.form_flags.append(code_to_form_flag[flag_code])

        raw_part_flags = read_flagset(fp)
        for flag_code in raw_part_flags:
            mob.parts_flags.append(code_to_parts_flag[flag_code])

        mob.size = read_string(fp)
        raw_material = read_string(fp)
        if raw_material != "0":
            mob.material = raw_material

        return mob
