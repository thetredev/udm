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
# >> PUBLIC CLASSES
# =============================================================================
class PlayerInventory(list):
    """Convenience class used to provide safe ways to equip and remove weapons from a player and act as an inventory."""

    def __init__(self, player_steamid):
        """Initialize this list with the player's SteamID."""
        # Call the super class constructor
        super().__init__()

        # Store the player's index
        self._player_steamid = player_steamid

    def append(self, classname):
        """Override list.append() to equip the player with the given weapon in a safe way."""
        # Get a PlayerEntity instance for the player's index
        player = Player(index_from_steamid(self._player_steamid))

        # Store a variable to decide whether to equip the weapon
        equip = True

        # Loop through all the player's weapons by tag
        for weapon in player.weapons(is_filters=weapons[classname].tag, not_filters=('melee', 'grenade')):

            # Remove the weapon if it's not the desired one
            if weapon.classname != classname:
                weapon.remove()

                # Remove the weapon's classname from this inventory as well
                if weapon.classname in self:
                    self.remove(weapon.classname)

            # If the player already has the weapon, don't equip it again
            else:
                equip = False

        # Add the classname to this inventory
        if classname not in self.copy():
            super().append(classname)

        # Give the player the weapon if it is allowed
        if equip:
            player.give_named_item(classname)

    def sorted_by_tags(self):
        """Return this inventory's classnames sorted by their weapon tags."""
        return sorted(self, key=lambda classname: weapons[classname].tag, reverse=True)


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
