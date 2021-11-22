class Object:
    def __init___(self):
        self.uuid = "uuid"
        self.vnum = "###"
        self.name = "item"
        self.keywords = []

        self.short_desc = ""
        self.long_desc = ""
        self.desc = ""

        self.material = ""

        self.item_type = ""

        # Extra Flags

        # Wear F;ags

        self.level = -1
        self.weight = -1
        self.cost = -1

        self.special_values = [0, 0, 0, 0, 0]

        # Pristine, good, adequate, worn, damaged, broken, ruined
        self.condition = 100

        # Extra descriptions for given keyword
        # {keyword: description}
        self.extra_description = {}
