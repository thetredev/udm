# ../udm/players.py

"""Provides convenience classes for player entities and a player inventory class."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Memory
from memory import make_object
#   Players
from players.entity import Player as Player
#   Weapons
from weapons.entity import Weapon

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
        self._safe_remove(player, is_filters=weapons[classname].tag)

        # Give the player the weapon
        weapon = player.give_named_item(classname)

        # Add the weapon's index to this inventory
        super().append(weapon.index)

        # Return the weapon entity given to the player
        return weapon

    def remove(self, classname):
        """Override list.remove() to remove a weapon from the player's inventory in a safe way."""
        # Correct the classname given in case it is only the weapon's basename
        classname = Weapons.format_classname(classname)

        # Get a PlayerEntity instance for the player's index
        player = PlayerEntity(self._player_index)

        # Safely remove the weapon entity if the player is currently owning it
        self._safe_remove(player, classname)

    def _safe_remove(self, player, classname=None, **kwargs):
        """Safely remove a player's weapon entity and its index from this inventory."""
        # Loop through all the weapons the player is currently owning for the parameters provided
        for weapon in player.weapons(classname, **kwargs):

            # Remove the weapon entity from the server
            weapon.remove()

            # Remove the weapon's index from this inventory if it has been added
            if weapon.index in self:
                super().remove(weapon.index)


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a global map of players and their inventories
_inventories = dict()


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class PlayerEntity(Player):
    """Convenience class used for the following things:

        - Wrap players.entity.Player.give_named_item() to return an actual weapons.entity.Weapon instance
        - Provide a safe and easy way to access the player's inventory"""

    def give_named_item(self, classname):
        """Make self.give_named_item() return an actual weapons.entity.Weapon instance."""
        return make_object(Weapon, super().give_named_item(classname))

    @property
    def inventory(self):
        """Provide access to the player's inventory in a safe and easy way."""
        # Create an _Inventory instance if no inventory exists for the player yet
        if self.index not in _inventories:
            _inventories[self.index] = _Inventory(self.index)

        # Return the player's inventory
        return _inventories[self.index]
