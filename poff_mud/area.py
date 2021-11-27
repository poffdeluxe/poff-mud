import copy
from enum import Enum

from poff_mud.enum_contains import EnumContains
from poff_mud.spawn_pool import SpawnPoolType
from poff_mud.mobile import Mobile
from poff_mud.character import EquipmentSlot
from poff_mud.room import Room, code_to_direction, DoorState
from poff_mud.object import Object

from poff_mud.file_helpers import (
    peek_next_line,
    read_until_tilde,
    read_letter,
    read_number,
    read_until_delimiter,
)


class ResetAction(Enum, metaclass=EnumContains):
    MOB_SPAWN = "M"
    OBJ_SPAWN = "O"
    OBJ_IN_OBJ = "P"
    GIVE_OBJ = "G"
    EQUIP_OBJ = "E"
    SET_DOOR = "D"


class Area:
    '''
    For an overview of the .are files, checkout:
    https://github.com/avinson/rom24-quickmud/blob/master/doc/Rom2.4.doc

    There are some missing details from this doc so I've done my best
    to fill in details from the quickmud source code
    '''
    def __init__(self):
        self.filename = ""
        self.name = "Area"
        self.description = ""
        self.level_min = 1
        self.level_max = 5

        self.vnum_min = 1
        self.vnum_max = 1

        self.resets = []

        self.rooms = {}

        # Pools to copy/spawn mobs and objects from
        self.mobs = {}
        self.objects = {}

    def __repr__(self):
        desc_split = self.description.split(" ", 1)
        author = desc_split[0]
        desc = desc_split[1]
        return f"AREA #{self.filename}: {self.name} By: {author} (Lvl {self.level_min} to {self.level_max})"

    def reset(self, gsp):
        # Count all the spawned mobs and objects by vnum
        all_spawned_mob_vnums = {}
        all_spawned_obj_vnums = {}

        for vnum in self.rooms:
            rm = self.rooms[vnum]

            for mob in rm.mobs:
                all_spawned_mob_vnums[mob.vnum] = (
                    all_spawned_mob_vnums.get(mob.vnum, 0) + 1
                )

            for obj in rm.objects:
                all_spawned_obj_vnums[obj.vnum] = (
                    all_spawned_obj_vnums.get(obj.vnum, 0) + 1
                )

        # Note: reset doesn't necessarily imply
        # resetting a zone from the ground up.
        # New things are basically spawned in if
        # needed or conditions are met.

        # Apply resets
        last = None
        last_reset = None
        for reset in self.resets:
            print(f"Attempting reset: {reset['action']} with values {reset['values']}")

            values = reset["values"]
            if reset["action"] == ResetAction.MOB_SPAWN:
                mob_vnum = values[1]
                room_vnum = values[3]

                rm = self.rooms[room_vnum]
                matching_mobs = [m for m in rm.mobs if m.vnum == mob_vnum]

                local_count = len(matching_mobs)
                global_count = all_spawned_mob_vnums.get(mob_vnum, 0)

                if local_count >= int(values[4]) or global_count >= int(values[2]):
                    last = None
                    continue

                if gsp.contains(SpawnPoolType.MOB, mob_vnum):
                    # We're good to spawn the mob
                    mob = gsp.spawn(SpawnPoolType.MOB, mob_vnum)
                    rm.mobs.append(mob)
                    last = mob
                else:
                    print(f"WARNING: Mob {mob_vnum} not in global spawn pool")
            elif reset["action"] == ResetAction.OBJ_SPAWN:
                obj_vnum = values[1]
                room_vnum = values[3]

                if room_vnum not in self.rooms:
                    # TODO: midgaard.are tries to do this. Idk why.
                    print(
                        "WARNING: Trying to spawn an object in a room not in the area"
                    )
                    continue

                # Don't spawn object if there's an object there already
                rm = self.rooms[room_vnum]

                matching_objs = [o for o in rm.objects if o.vnum == obj_vnum]
                if len(matching_objs) > 0:
                    last = None
                    continue

                # TODO: spec says to not spawn object if players
                # are present but I kinda disagree.. not sure
                # the reasoning but there probably is one
                if len(rm.players) > 0:
                    last = None
                    continue

                if gsp.contains(SpawnPoolType.OBJ, obj_vnum):
                    obj = gsp.spawn(SpawnPoolType.OBJ, obj_vnum)
                    rm.objects.append(obj)
                    last = obj
                else:
                    print(f"WARNING: Obj {obj_vnum} not in global spawn pool")
            elif reset["action"] == ResetAction.OBJ_IN_OBJ:
                obj_vnum = values[1]
                global_limit = int(values[2])
                obj_to_vnum = values[3]
                local_limit = int(values[4])

                # Global limit is arg 2
                # WARNING: Possible Bug! This doesn't count stuff in containers!
                # We might need to have a global way to find and count spawned objects
                # that even might be within containers..
                if all_spawned_obj_vnums.get(obj_vnum, 0) >= global_limit:
                    continue

                # I'm not entirely sure this is the correct behavior
                # but the problem is that VNUM doesn't necessarily
                # correspond to an instanced version so we have to rely
                # on last pointer to figure out where to put the item

                # But there's a new problem... sometimes an object might
                # not get spawned in because it already exists. Fuck!

                # Ok... Here's what I'm gonna do:
                # If the last.vnum matches the expected vnum, give that
                # object the target object. If it doesn't, try
                # to look up the expected object in the room
                if type(last).__name__ == "Object" and obj_to_vnum == last.vnum:
                    # Local limit in container is 4
                    local_count = len([o for o in last.contains if o.vnum == obj_vnum])
                    if local_count >= local_limit:
                        continue

                    if gsp.contains(SpawnPoolType.OBJ, obj_vnum):
                        # We can give the object to this last object
                        obj = gsp.spawn(SpawnPoolType.OBJ, obj_vnum)
                        last.contains.append(obj)
                    else:
                        print(f"WARNING: Obj {obj_vnum} not in global spawn pool")
                else:
                    # Look up object
                    target_object = None

                    if not last_reset:
                        continue
                    last_values = last_reset["values"]
                    last_obj_vnum = values[1]
                    last_room_vnum = values[3]

                    target_object = next(
                        o for o in self.rooms[last_room_vnum] if o.vnum == last_obj_vnum
                    )

                    # Couldn't find the object.. give up
                    if target_object is None:
                        continue

                    # Local limit in container is 4
                    local_count = [
                        o for o in target_object.contains if o.vnum == obj_vnum
                    ]
                    if local_count >= local_limit:
                        continue

                    if gsp.contains(SpawnPoolType.OBJ, obj_vnum):
                        obj = gsp.spawn(SpawnPoolType.OBJ, obj_vnum)
                        target_object.contains.append(obj)
                    else:
                        print(f"WARNING: Obj {obj_vnum} not in global spawn pool")
            elif reset["action"] == ResetAction.GIVE_OBJ:
                obj_vnum = values[1]

                if last and type(last).__name__ == "Mobile":
                    if gsp.contains(SpawnPoolType.OBJ, obj_vnum):
                        obj = gsp.spawn(SpawnPoolType.OBJ, obj_vnum)
                        last.inventory.append(obj)
                    else:
                        print(f"WARNING: Obj {obj_vnum} not in global spawn pool")
                else:
                    # TODO: There's a case here where the mob already existed
                    # so it didn't get reset and therefore won't get an item
                    # reset to it (since it wasn't newly created). I have to figure
                    # out if this is the intended behavior or if I should look up
                    # the mob in the area and give it the item if it doesn't exist
                    print("Skipping as the last thing loaded wasn't a mob..")

                    last = None

            elif reset["action"] == ResetAction.EQUIP_OBJ:
                obj_vnum = values[1]
                wear_slot = EquipmentSlot(int(values[3]))

                if last and type(last).__name__ == "Mobile":
                    if gsp.contains(SpawnPoolType.OBJ, obj_vnum):
                        obj = gsp.spawn(SpawnPoolType.OBJ, obj_vnum)
                        last.equip(obj, wear_slot)
                    else:
                        print(f"WARNING: Obj {obj_vnum} not in global spawn pool")
                else:
                    # TODO: There's a case here where the mob already existed
                    # so it didn't get reset and therefore won't get an item
                    # reset to it (since it wasn't newly created). I have to figure
                    # out if this is the intended behavior or if I should look up
                    # the mob in the area and give it the item if it doesn't exist
                    print("Skipping as the last thing loaded wasn't a mob..")

                    last = None
            elif reset["action"] == ResetAction.SET_DOOR:
                room_vnum = values[1]
                rm = self.rooms[room_vnum]
                rm.exits[code_to_direction[int(values[2])]] = DoorState(int(values[3]))

            last_reset = reset

    @staticmethod
    def load_area_block(fp, area):
        area.filename = read_until_tilde(fp)
        area.name = read_until_tilde(fp)

        read_letter(fp)  # {

        raw_level_str = read_until_delimiter(fp, "}")
        if "All" in raw_level_str:
            area.level_min = 1
            area.level_max = 999
        else:
            area.level_min, area.level_max = raw_level_str.split()

        area.description = read_until_tilde(fp).strip()

        area.vnum_min = read_number(fp)
        area.vnum_max = read_number(fp)

        fp.readline()

    @classmethod
    def load_from_file(cls, fp, gsp=None):
        area = cls()

        while True:
            line_header = fp.readline()
            if "#AREA" in line_header:
                Area.load_area_block(fp, area)
            elif "#MOBILES" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "#0":
                    mob = Mobile.load_from_file(fp)
                    area.mobs[mob.vnum] = mob

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()
            elif "#ROOMS" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "#0":
                    room = Room.load_from_file(fp)
                    area.rooms[room.vnum] = room

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()
            elif "#OBJECTS" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "#0":
                    obj = Object.load_from_file(fp)
                    area.objects[obj.vnum] = obj

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()
            elif "#RESETS" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "S":
                    reset_line = fp.readline()

                    if "\t" in reset_line:
                        reset_line = reset_line.split("\t", 1)[0]

                    reset_line_parts = reset_line.split()
                    reset_info = {
                        "action": ResetAction(reset_line_parts[0]),
                        "values": reset_line_parts[1:],
                    }
                    area.resets.append(reset_info)

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()
            elif line_header == "\n":
                continue
            elif line_header == "":
                break
            else:
                continue

        # If we're passing in a spawn pool, add relevant items to their pools
        if gsp:
            for obj_vnum in area.objects:
                gsp.add(SpawnPoolType.OBJ, obj_vnum, area.objects[obj_vnum])

            for mob_vnum in area.mobs:
                gsp.add(SpawnPoolType.MOB, mob_vnum, area.mobs[mob_vnum])

        return area
