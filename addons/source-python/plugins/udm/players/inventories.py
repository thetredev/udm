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
from udm.weapons import Weapons
from udm.weapons import weapons


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a global map of players and their inventories
player_inventories = dict()


# =============================================================================
# >> PLAYER INVENTORY
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
        # Correct the classname given in case it is only the weapon's basename
        classname = Weapons.format_classname(classname)

        # Get a PlayerEntity instance for the player's index
        player = Player(index_from_steamid(self._player_steamid))

        # Safely remove any weapon of the given tag the player is currently owning
        self._safe_remove(player, weapons[classname].tag)

        # Add the classname to this inventory
        super().append(classname)

        # Give the player the weapon
        player.give_named_item(classname)

    def sorted_by_tags(self):
        """Return this inventory's classnames sorted by their weapon tags."""
        return sorted(self, key=lambda classname: weapons[classname].tag, reverse=True)

    def _safe_remove(self, player, tag):
        """Safely remove a player's weapon entity and its index from this inventory."""
        # Loop through all the weapons the player is currently owning for the parameters provided
        for weapon in player.weapons(is_filters=tag):

            # Remove the weapon entity from the server
            weapon.remove()

            # Remove the classname from this inventory
            if weapon.classname in self:
                self.remove(weapon.classname)
