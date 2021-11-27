#!/usr/bin/env python3
from poff_mud.spawn_pool import SpawnPool
from poff_mud.area import Area


def load_and_print_area(filename, gsp):
    with open(filename) as fp:
        new_area = Area.load_from_file(fp, gsp=gsp)

    print(new_area)

    print("MOBS:")
    for mob_vnum in new_area.mobs:
        print(f"\t{new_area.mobs[mob_vnum]}")

    print("ROOMS:")
    for room_vnum in new_area.rooms:
        print(f"\t{new_area.rooms[room_vnum]}")

    print("OBJECTS:")
    for obj_vnum in new_area.objects:
        print(f"\t{new_area.objects[obj_vnum]}")

    return new_area


if __name__ == "__main__":
    areas = []
    gsp = SpawnPool()

    school = load_and_print_area("areas/school.are", gsp)
    areas.append(school)

    midgaard = load_and_print_area("areas/midgaard.are", gsp)
    areas.append(midgaard)

    for a in areas:
        a.reset(gsp)
