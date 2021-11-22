#!/usr/bin/env python3
from poff_mud.area import Area

if __name__ == "__main__":
    with open("areas/school.are") as fp:
        Area.load_from_file(fp)
