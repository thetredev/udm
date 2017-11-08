# ../udm/players/inventories.py

"""Provides player inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory import make_object
#   Players
from players.entity import Player
from players.helpers import index_from_steamid
#   Weapons
from weapons.entity import Weapon

# Script Imports
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> INVENTORY ITEM
# =============================================================================
class _InventoryItem(object):
    """Class used to provide an inventory item."""

    def __init__(self):
        """Store the item's basename."""
        self.basename = None

    def equip(self, player):
        """Equip the player with this inventory item."""
        # Get a list of weapons owned by the player of the same weapon tag as this inventory item
        entity = self.equipped_entity(player)

        # Remove the weapon the player currently owns before equipping this one
        if entity is not None:

            # Only equip if this item is not the same the player currently owns
            if entity.classname != self.data.name:
                entity.remove()
                weapon = make_object(Weapon, player.give_named_item(self.data.name))
            else:
                weapon = entity

        # Equip the item straight away, if the player doesn't own any weapon of this inventory item's weapon tag
        else:
            weapon = make_object(Weapon, player.give_named_item(self.data.name))

        # Set silencer on for weapons which are supposed to be silenced
        if weapon_manager.silencer_allowed(self.basename):
            weapon.set_property_bool('m_bSilencerOn', self.data.silenced)

    def equipped_entity(self, player):
        """Return the currently equipped entity for this inventory item."""
        equipped = list(player.weapons(is_filters=self.data.tag))

        if equipped:
            return equipped[0]

        # Return None if the player currently doesn't carry the weapon
        return None

    @property
    def data(self):
        """Return the weapon's data."""
        return weapon_manager[self.basename]


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

    def add_weapon(self, basename):
        """Add an inventory item for `basename` and equip the player with it."""
        # Get the weapon's data
        weapon_data = weapon_manager[basename]

        # Create a new inventory item if the player doesn't own any weapon of the weapon's tag
        if weapon_data.tag not in self.keys():
            self[weapon_data.tag] = _InventoryItem()

        # Get the inventory item
        item = self[weapon_data.tag]

        # Set the inventory item's basename
        item.basename = basename

        # Equip the player with it
        player = Player(index_from_steamid(self._player_steamid))
        item.equip(player)

    def remove_weapon(self, tag):
        """Remove an inventory item for weapon tag `tag`."""
        # Get a Player instance for the player this inventory belongs to
        player = Player(index_from_steamid(self._player_steamid))

        # Get the currently equipped weapon entity for the weapon tag
        entities = list(player.weapons(is_filters=tag))

        # Remove it if it was found
        if entities is not None:
            entities[0].remove()

        # Remove the weapon tag from this inventory
        if tag in self.keys():
            del self[tag]

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
