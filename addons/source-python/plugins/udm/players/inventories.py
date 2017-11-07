# ../udm/players/inventories.py

"""Provides player inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Players
from players.entity import Player
from players.helpers import index_from_steamid

# Script Imports
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> INVENTORY ITEM
# =============================================================================
class _InventoryItem(object):
    """Class used to provide an inventory item."""

    def __init__(self, classname):
        """Store the item's classname."""
        self.classname = classname

    def equip(self, player):
        """Equip the player with this inventory item."""
        # Get a list of weapons owned by the player of the same weapon tag as this inventory item
        equipped = list(player.weapons(is_filters=self.tag))

        # Remove the weapon the player currently owns before equipping this one
        if equipped:
            entity = equipped[0]

            # Only equip if this item is not the same the player currently owns
            if entity.classname != self.classname:
                entity.remove()
                player.give_named_item(self.classname)

        # Equip the item straight away, if the player doesn't own any weapon of this inventory item's weapon tag
        else:
            player.give_named_item(self.classname)

    @property
    def tag(self):
        """Return this inventory item's weapon tag."""
        return weapon_manager[self.classname].tag


# =============================================================================
# >> PLAYER INVENTORIES
# =============================================================================
class PlayerInventory(dict):
    """Class used to provide a weapon inventory for players."""

    def __init__(self, player_steamid):
        """Initialize this list with the player's SteamID."""
        # Call the super class constructor
        super().__init__()

        # Store the player's SteamID
        self._player_steamid = player_steamid

    def add_weapon(self, classname):
        """Add an inventory item for `classname` and equip the player with it."""
        # Get the weapon's data
        weapon_data = weapon_manager[classname]

        # Create a new inventory item if the player doesn't own any weapon of the weapon's tag
        if weapon_data.tag not in self.keys():
            self[weapon_data.tag] = _InventoryItem(classname)

        # Get the inventory item
        item = self[weapon_data.tag]

        # Set the inventory item's classname
        item.classname = classname

        # Equip the player with it
        player = Player(index_from_steamid(self._player_steamid))
        item.equip(player)

    def values(self):
        """Return all inventory items reverse-sorted by their weapon tag."""
        for key in sorted(self.keys(), reverse=True):
            yield self[key]


class _PlayerInventories(dict):
    """Class used to provide multiple inventories and weapon selections for players."""

    # Store player weapon selections
    selections = dict()

    def __missing__(self, key):
        """Set and return an empty dictionary as the value for `key`."""
        value = self[key] = dict()
        return value


# Store a global instance of `_PlayerInventories`
player_inventories = _PlayerInventories()
