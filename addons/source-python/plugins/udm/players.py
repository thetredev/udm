# ../udm/players.py

"""Provides convenience classes for player entities and a player inventory class."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Random
import random

# Source.Python Imports
#   Players
from players.entity import Player as Player

# Script Imports
#   Weapons
from udm.weapons import weapons
from udm.weapons import Weapons


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _Inventory(list):
    """Convenience class used to provide safe ways to equip and remove weapons from a player and act as an inventory."""

    def __init__(self, player_index):
        """Initialize this list with the player's index."""
        # Call the super class constructor
        super().__init__()

        # Store the player's index
        self._player_index = player_index

    def append(self, classname):
        """Override list.append() to equip the player with the given weapon in a safe way."""
        # Correct the classname given in case it is only the weapon's basename
        classname = Weapons.format_classname(classname)

        # Get a PlayerEntity instance for the player's index
        player = PlayerEntity(self._player_index)

        # Safely remove any weapon of the given tag the player is currently owning
        self._safe_remove(player, weapons[classname].tag)

        # Add the classname to this inventory
        super().append(classname)

        # Return the weapon entity given to the player
        return player.give_named_item(classname)

    def sorted_by_tags(self):
        return sorted(self, key=lambda classname: weapons[classname].tag, reverse=True)

    def _safe_remove(self, player, tag):
        """Safely remove a player's weapon entity and its index from this inventory."""
        # Loop through all the weapons the player is currently owning for the parameters provided
        for weapon in player.weapons(None, is_filters=tag):

            # Remove the weapon entity from the server
            weapon.remove()

            if weapon.classname in self:
                self.remove(weapon.classname)


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a global map of players and their inventories
_inventories = dict()

# Store the weapon tags for random weapons
_random_weapon_tags = ('secondary', 'primary')


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class PlayerEntity(Player):
    """Convenience class used for the following things:

        - Wrap players.entity.Player.give_named_item() to return an actual weapons.entity.Weapon instance
        - Provide a safe and easy way to access the player's inventory"""

    def prepare(self):
        """Prepare the player for battle."""
        # Remove all the player's weapons except for 'knife'
        for weapon in self.weapons(not_filters='knife'):
            weapon.remove()

        # Equip the player with an assault suit
        super().give_named_item('item_assaultsuit')

        # Equip the player with a High Explosive grenade
        self.give_named_item('hegrenade')

        # Equip the player with all the weapons stored in their inventory
        if self.inventory:
            for classname in self.inventory.sorted_by_tags():
                self.give_named_item(classname)

        # Or give random weapons, if the inventory is empty
        else:
            for tag in _random_weapon_tags:
                self.give_named_item(random.choice(weapons.by_tag(tag)).basename)

    def give_named_item(self, classname):
        """Make sure to correct the classname before passing it to the base give_named_item() method."""
        super().give_named_item(Weapons.format_classname(classname))

    def spawn(self):
        """Safely respawn the player."""
        if self.is_connected():
            super().spawn(True)

    @property
    def inventory(self):
        """Provide access to the player's inventory in a safe and easy way."""
        # If the player is connected, create an _Inventory instance if no inventory exists for the player yet
        if self.is_connected():
            if self.index not in _inventories:
                _inventories[self.index] = _Inventory(self.index)

            # Return the player's inventory
            return _inventories[self.index]

        # If the player is disconnected, remove the player's inventory
        if self.index in _inventories:
            del _inventories[self.index]
