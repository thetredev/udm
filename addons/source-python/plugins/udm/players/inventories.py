# ../udm/players/inventories.py

"""Provides player inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import defaultdict

# Source.Python Imports
#   Memory
from memory import make_object
#   Weapons
from weapons.entity import Weapon

# Script Imports
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> PLAYER INVENTORIES
# =============================================================================
class _InventoryItem(object):
    """Class used to provide an inventory item."""

    def __init__(self):
        """Object initialization."""
        # Make it possible to store the weapon's basename in the future
        self.basename = None

    @property
    def data(self):
        """Return the weapon's data."""
        return weapon_manager[self.basename]


class PlayerInventory(defaultdict):
    """Class used to provide a weapon inventory for players."""

    def __init__(self):
        """Make `_InventoryItem` the default value type."""
        super().__init__(_InventoryItem)

    def equip(self, player, tag=None):
        """Equip the player with the weapon(s) of weapon tag in `tag`."""
        # Make `tag` all keys of this dictionary if none was provided
        if tag is None:
            tag = self.keys()

        # Make `tag` an iterable
        if isinstance(tag, str):
            tag = (tag, )

        # Give each inventory item for the keys in `tag`
        for key in sorted(tag, reverse=True):

            # Get the weapon's data
            weapon_data = self[key].data

            # Get the weapon of tag in `key` the player is carrying
            weapon = player.get_weapon(is_filters=key)

            # Remove it if it's not the weapon the player has chosen as their inventory item of the respective tag
            if weapon is not None and weapon.weapon_name != weapon_data.name:
                weapon.remove()

                # Give their inventory item
                weapon = make_object(Weapon, player.give_named_item(weapon_data.name))

            # Give their inventory item if the player doesn't carry that weapon
            elif weapon is None:
                weapon = make_object(Weapon, player.give_named_item(weapon_data.name))

            # Fix silencer issues for *_silenced weapons
            if '_silencer' in weapon.weapon_name:
                weapon.set_property_bool('m_bSilencerOn', '_silencer' in weapon_data.name)

            # Set silencer on for weapons which are supposed to be silenced
            if weapon_manager.silencer_allowed(weapon_data.basename):
                weapon.set_property_bool('m_bSilencerOn', weapon_data.silenced)

    def add_inventory_item(self, player, basename):
        """Add an inventory item for `basename` and equip the player with it."""
        # Get the weapon's data
        weapon_data = weapon_manager[basename]

        # Set the inventory item's basename
        self[weapon_data.tag].basename = basename

        # Equip the player with the inventory item
        self.equip(player, weapon_data.tag)

    def remove_inventory_item(self, player, tag):
        """Remove an inventory item for weapon tag `tag`."""
        # Get the currently equipped weapon entity for the weapon tag
        weapon = player.get_weapon(is_filters=tag)

        if weapon is not None:
            weapon.remove()

        # Remove the weapon tag from this inventory
        if tag in self.keys():
            del self[tag]

    def inventory_items(self):
        """Return all inventory items reverse-sorted by their weapon tag."""
        for key in sorted(self.keys(), reverse=True):
            yield self[key]


class _PlayerInventoryMap(defaultdict):
    """Class used to map inventory selection indexes to `PlayerInventory` items."""

    def __init__(self):
        """Object initialization."""
        # Make `PlayerInventory` the default value type
        super().__init__(PlayerInventory)


class _PlayerInventories(defaultdict):
    """Class used to provide multiple inventories and weapon selections for players."""

    # Store weapon selections
    selections = defaultdict(int)

    # Store random weapon selections, defaults to True for every new player
    selections_random = defaultdict(lambda: True)

    def __init__(self):
        """Object initialization."""
        # Make `_PlayerInventoryMap` the default value type
        super().__init__(_PlayerInventoryMap)


# Store a global instance of `_PlayerInventories`
player_inventories = _PlayerInventories()
