# ../udm/players/inventories.py

"""Provides convenience classes for player inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Players
from players.entity import Player
from players.helpers import index_from_steamid

# Script Imports
#   Weapons
from udm.weapons import weapons


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _InventoryItem(object):
    """Class used to provide an inventory item."""

    def __init__(self, classname):
        """Object initialization."""
        # Store the item's classname
        self.classname = classname

    def equip(self, player):
        """Equip the player with this inventory item."""
        # Get a list of weapons of the same tag as this item owned by the player
        equipped = list(player.weapons(is_filters=self.tag))

        # Remove the weapon the player currently owns before equipping this one
        if equipped:
            entity = equipped[0]

            # Don't equip if this item already is the weapon owned by the player
            if entity.classname != self.classname:
                entity.remove()
                player.give_named_item(self.classname)

        # Equip the item straight away, if the player doesn't own any weapon of its tag
        else:
            player.give_named_item(self.classname)

    @property
    def tag(self):
        """Return this item's weapon tag."""
        return weapons[self.classname].tag


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class PlayerInventory(dict):
    """Class used to provide a weapon inventory for players."""

    def __init__(self, player_steamid):
        """Initialize this list with the player's SteamID."""
        # Call the super class constructor
        super().__init__()

        # Store the player's index
        self._player_steamid = player_steamid

    def add_weapon(self, classname):
        """Add the weapon to the inventory and equip the player with it."""
        # Get the weapon's class
        weapon_class = weapons[classname]

        # Create a new inventory item if the player doesn't own any weapon of the same tag
        if weapon_class.tag not in self.keys():
            self[weapon_class.tag] = _InventoryItem(classname)

        # Get the inventory item object
        item = self[weapon_class.tag]

        # Set the item's classname
        item.classname = classname

        # Equip the player with the item
        player = Player(index_from_steamid(self._player_steamid))
        item.equip(player)

    def values(self):
        for key in sorted(self.keys(), reverse=True):
            yield self[key]


class _PlayerInventories(dict):
    """Class used to store player inventories and their weapon selections."""

    # Store each player's weapon selections
    selections = dict()

    def __missing__(self, key):
        """Set and return an empty dictionary object as the value for `key`."""
        value = self[key] = dict()
        return value


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Create a global instance of _PlayerInventories
player_inventories = _PlayerInventories()
