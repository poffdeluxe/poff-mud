from enum import Enum

# Left finger  1		Right finger 2
# Neck (1)	 3		Neck (2)	 4
# On Torso	 5		Head		 6
# Legs		 7		Feet		 8
# Hands		 9		Arms		10
# Shield 	11		About body	12
# Waist		13		Left Wrist	14
# Right Wrist	15		Wield		16
# Held		17		Floating	18


class EquipmentSlot(Enum):
    LIGHT = 0

    L_FINGER = 1
    R_FINGER = 2
    NECK_1 = 3
    NECK_2 = 4

    TORSO = 5
    HEAD = 6
    LEGS = 7
    FEET = 8
    HANDS = 9
    ARMS = 10
    SHIELD = 11
    ABOUTBODY = 12
    WAIST = 13

    L_WRIST = 14
    R_WRIST = 15

    WIELD = 16
    HELD = 17
    FLOATING = 18


class Character:
    def __init__(self):
        self.level = 1

        self.hp = 1
        self.max_hp = 1

        self.mana = 1
        self.max_mana = 1

        self.move = 1
        self.max_move = 1

        self.inventory = []

        self.equipment = {
            EquipmentSlot.LIGHT: None,
            EquipmentSlot.L_FINGER: None,
            EquipmentSlot.R_FINGER: None,
            EquipmentSlot.NECK_1: None,
            EquipmentSlot.NECK_2: None,
            EquipmentSlot.TORSO: None,
            EquipmentSlot.HEAD: None,
            EquipmentSlot.LEGS: None,
            EquipmentSlot.FEET: None,
            EquipmentSlot.HANDS: None,
            EquipmentSlot.ARMS: None,
            EquipmentSlot.SHIELD: None,
            EquipmentSlot.ABOUTBODY: None,
            EquipmentSlot.WAIST: None,
            EquipmentSlot.L_WRIST: None,
            EquipmentSlot.R_WRIST: None,
            EquipmentSlot.WIELD: None,
            EquipmentSlot.HELD: None,
            EquipmentSlot.HELD: None,
            EquipmentSlot.FLOATING: None,
        }

    def equip(self, obj, slot):
        # If something is already equipped,
        # remove it from equipment slot and place
        # it in the inventory
        if self.equipment[slot]:
            already_eqd_obj = self.equipment[slot]
            self.inventory.push(already_eqd_obj)

        # Equip the item
        self.equipment[slot] = obj

        # If the item is coming from the inventory,
        # remove it from the inventory
        if obj in self.inventory:
            self.inventory.remove(obj)
