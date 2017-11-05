# ../udm/players.py

"""Provides convenience classes for player entities and a player inventory class."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib
#   Random
import random

# Source.Python Imports
#   Colors
from colors import Color
from colors import WHITE
#   Engines
from engines.server import global_vars
#   Listeners
from listeners import OnEntityDeleted
from listeners.tick import Delay
#   Players
from players.entity import Player
from players.helpers import index_from_userid

# Script Imports
#   Config
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_spawn_protection_delay
#   Delays
from udm.delays import delay_manager
#   Spawn Points
from udm.spawnpoints import spawnpoints
#   Weapons
from udm.weapons import weapons
from udm.weapons import Weapons


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a global map of players and their inventories
_inventories = dict()

# Store the weapon tags for random weapons
_random_weapon_tags = ('secondary', 'primary')


# =============================================================================
# >> INVENTORY
# =============================================================================
class _Inventory(list):
    """Convenience class used to provide safe ways to equip and remove weapons from a player and act as an inventory."""

    def __init__(self, player_userid):
        """Initialize this list with the player's index."""
        # Call the super class constructor
        super().__init__()

        # Store the player's index
        self._player_userid = player_userid

    def append(self, classname):
        """Override list.append() to equip the player with the given weapon in a safe way."""
        # Correct the classname given in case it is only the weapon's basename
        classname = Weapons.format_classname(classname)

        # Get a PlayerEntity instance for the player's index
        player = PlayerEntity(index_from_userid(self._player_userid))

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
        for weapon in player.weapons(None, is_filters=tag):

            # Remove the weapon entity from the server
            weapon.remove()

            # Remove the classname from this inventory
            if weapon.classname in self:
                self.remove(weapon.classname)


# =============================================================================
# >> PLAYER ENTITY
# =============================================================================
class PlayerEntity(Player):
    """Convenience class used for the following things:

        - Wrap players.entity.Player.give_named_item() to return an actual weapons.entity.Weapon instance
        - Provide a safe and easy way to access the player's inventory"""

    def equip(self, admin=False):
        """Equip the player with their inventory or random weapons."""
        # Equip the player with an assault suit
        super().give_named_item('item_assaultsuit')

        # Equip the player with a High Explosive grenade if configured that way
        if cvar_equip_hegrenade.get_int() > 0:
            self.give_named_item('hegrenade')

        # Equip the player with all the weapons stored in their inventory
        if self.inventory:
            for classname in self.inventory.sorted_by_tags():
                self.give_named_item(classname)

        # Or give random weapons, if the inventory is empty
        else:
            for tag in _random_weapon_tags:
                self.give_named_item(random.choice(weapons.by_tag(tag)).basename)

        # Unprotect and re-equip the knife when the player closes the admin menu
        if admin:
            self.unprotect()
            self.give_named_item('knife')

    def give_named_item(self, classname):
        """Make sure to correct the classname before passing it to the base give_named_item() method."""
        super().give_named_item(Weapons.format_classname(classname))

    def prepare(self):
        """Prepare the player for battle."""
        # Protect the player from any damage
        self.protect(cvar_spawn_protection_delay.get_int())

        # Choose a random spawn point
        spawnpoint = spawnpoints.get_random()

        # Spawn the player on the location found
        if spawnpoint is not None:
            self.origin = spawnpoint
            self.view_angle = spawnpoint.angle

        # Strip the player off their weapons, but keep the knife
        self.strip('knife')

        # Equip the player
        self.equip()

    def protect(self, time_delay=None):
        """Protect the player for the configured spawn protection duration."""
        # Enable god mode
        self.godmode = True

        # Set the player's color
        self.color = Color(
            210 if self.team == 2 else 0,
            0,
            210 if self.team == 3 else 0
        )

        # Call _unprotect() after the configured spawn protection duration
        if time_delay is not None:
            delay_manager[f'protect_{self.userid}'].append(Delay(time_delay, self.unprotect))

    def refill_ammo(self):
        """Refill the player's ammo on reload after the reload animation has finished."""
        with contextlib.suppress(ValueError):
            if weapons[self.active_weapon.classname].tag != 'meele':

                # Get the 'next attack' property for the current weapon, plus a tolerance value of one second
                next_attack = self.active_weapon.get_property_float('m_flNextPrimaryAttack') + 1

                # Calculate the amount of time it would take for the reload animation to finish (tolerance included)
                duration = next_attack - global_vars.current_time

                # Refill the weapon's ammo after the reload animation has finished
                delay_manager[f'refill_{self.active_weapon.index}'].append(
                    Delay(duration, self._refill_ammo, (self.active_weapon, ))
                )

    def spawn(self):
        """Safely respawn the player."""
        if self.is_connected():
            super().spawn(True)

    def strip(self, keep=None):
        """Remove all the player's weapons except for 'knife'."""
        for weapon in self.weapons(not_filters=keep):
            weapon.remove()

    def unprotect(self):
        """Enable default gameplay, if they're still online."""
        if self.is_connected():

            # Disable god mode
            self.godmode = False

            # Reset the player's color
            self.color = WHITE

    @property
    def inventory(self):
        """Provide access to the player's inventory in a safe and easy way."""
        # If the player is connected, create an _Inventory instance if no inventory exists for the player yet
        if self.is_connected():
            if self.userid not in _inventories:
                _inventories[self.userid] = _Inventory(self.userid)

            # Return the player's inventory
            return _inventories[self.userid]

        # If the player is disconnected, remove the player's inventory
        if self.userid in _inventories:
            del _inventories[self.userid]

    def _refill_ammo(self, weapon):
        """Refill the player's ammo."""
        if weapon.owner is not None:
            weapon.ammo = weapons[weapon.classname].maxammo


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def on_entity_deleted(entity):
    """Cancel the refill delay for the deleted entity."""
    with contextlib.suppress(ValueError):
        delay_manager.cancel_delays(f'refill_{entity.index}')
