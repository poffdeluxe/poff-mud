import copy
from enum import Enum
from poff_mud.copyable import Copyable


class SpawnPoolType(Enum):
    MOB = "mob"
    OBJ = "obj"


class SpawnPoolDuplicateExistsError(Exception):
    pass


class SpawnPoolNotCopyableError(Exception):
    pass


class SpawnPoolDoesNotExistError(Exception):
    pass


class SpawnPoolItemDoesNotExistError(Exception):
    pass


class SpawnPool:
    """
    This class is just a helper to create generic pools from which to create
    fresh, new instances of objects/mobs/whatever for the MUD.

    The thought process here is that we can load in the representative object/mob/whatever
    via area files (or wherever else) and then when we need to create/spawn a new
    item, we can simply spawn it by deepcopying the requested item.

    This makes it easier to share items across areas and enforces the copyable
    requirement.
    """

    def __init__(self):
        # Come on in the water's fine
        self._pool = {}

    def add(self, pool_key, item_key, item):
        # Create pool_key entry if it doesn't exist
        if pool_key not in self._pool:
            self._pool[pool_key] = {}

        if not issubclass(type(item), Copyable):
            raise SpawnPoolNotCopyableError(
                f"Item {item_key} for pool {pool_key} is not copyable"
            )

        if item_key in self._pool[pool_key]:
            raise SpawnPoolNotCopyableError(
                f"Item {item_key} for pool {pool_key} already exists in pool"
            )

        self._pool[pool_key][item_key] = item

    def contains(self, pool_key, item_key):
        if pool_key not in self._pool:
            raise SpawnPoolDoesNotExistError(f"Pool {pool_key} does not exist")

        return item_key in self._pool[pool_key]

    def spawn(self, pool_key, item_key):
        if pool_key not in self._pool:
            raise SpawnPoolDoesNotExistError(f"Pool {pool_key} does not exist")

        if item_key not in self._pool[pool_key]:
            raise SpawnPoolItemDoesNotExistError(
                f"{item_key} does not exist in pool {pool_key}"
            )

        return copy.deepcopy(self._pool[pool_key][item_key])
