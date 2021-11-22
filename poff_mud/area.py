import copy

from poff_mud.mobile import Mobile
from poff_mud.room import Room


def peek_next_line(fp):
    pos = fp.tell()
    line = fp.readline()
    fp.seek(pos)

    return line


class Area:
    def __init__(self):
        self.filename = ""
        self.name = "Area"
        self.description = ""
        self.level_min = 1
        self.level_max = 5

        self.vnum_min = 1
        self.vnum_max = 1

    @staticmethod
    def load_area_block(fp, area):
        pass

    @classmethod
    def load_from_file(cls, fp):
        area = cls()
        mobs = []
        rooms = []

        while True:
            line_header = fp.readline()

            if "#AREA" in line_header:
                Area.load_area_block(fp, area)
            elif "#MOBILES" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "#0":
                    mobs.append(Mobile.load_from_file(fp))

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()
            elif "#ROOMS" in line_header:
                next_line = peek_next_line(fp)
                next_line = next_line.strip()

                while next_line != "#0":
                    rooms.append(Room.load_from_file(fp))

                    next_line = peek_next_line(fp)
                    next_line = next_line.strip()

                # Advance past #0
                fp.readline()

                breakpoint()
            elif line_header == "\n":
                continue
            elif line_header == "":
                return
            else:
                continue
