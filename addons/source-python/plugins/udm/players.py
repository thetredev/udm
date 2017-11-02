# ../udm/players.py

"""Provides convenience classes for player entities and a player inventory class."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   JSON
import json
#   Random
import random

# Source.Python Imports
#   Colors
from colors import Color
from colors import WHITE
#   Engines
from engines.server import global_vars
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners.tick import Delay
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Paths
from paths import PLUGIN_DATA_PATH
#   Players
from players.entity import Player

# Script Imports
#   Config
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_spawn_point_distance
from udm.config import cvar_spawn_protection_delay
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

# Store a PlayerIter instance for alive players
_playeriter_alive = PlayerIter('alive')

# Store the path to the plugin's spawn points data
_spawnpoints_path = PLUGIN_DATA_PATH.joinpath('udm', 'spawnpoints')

# Create the spawn points data path if it does not exist
if not _spawnpoints_path.exists():
    _spawnpoints_path.makedirs()


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
# >> SPAWN POINTS
# =============================================================================
class SpawnPoint(Vector):
    """Class used to attach a QAngle to a Vector and provide a JSON representation for the respective locations."""

    def __init__(self, x, y, z, angle):
        """Object initialization."""
        # Call Vector's constructor using the given parameters
        super().__init__(x, y, z)

        # Store the QAngle object
        self._angle = angle

    @property
    def angle(self):
        """Return the QAngle object."""
        return self._angle

    @property
    def json(self):
        """Return a JSON representation of this spawn point location."""
        return {
            'vector': [self.x, self.y, self.z],
            'angle': [self.angle.x, self.angle.y, self.angle.z]
        }


class _SpawnPoints(list):
    """Class used to provide spawn point managing functionality:

        - Load spawn points from a JSON file
        - Save spawn points to a JSON file
        - Get a random spawn point safely
    """

    def load(self):
        """Load spawn points from the spawn points data file for the current map."""
        # Skip if the file doesn't exist
        if not self.json_file.exists():
            return

        # Remove all spawn points from this list
        self.clear()

        # Read the spawn points data file into memory
        with self.json_file.open() as f:
            contents = json.load(f)

        # Append each entry as a _SpawnPoint object
        for data in contents:
            self.append(SpawnPoint(*data['vector'], QAngle(*data['angle'])))

    def save(self):
        """Save spawn points to the spawn points data file for the current map."""
        # Skip if we have nothing to save
        if not self:
            return

        # Dump the contents of this list to file
        with self.json_file.open('w') as f:
            json.dump([spawnpoint.json for spawnpoint in self], f)

    def get_random(self):
        """Return a random spawn point safely."""
        # Get origins for alive players
        player_origins = [player.origin for player in _playeriter_alive]

        # Store possible vectors to spawn on
        possible = list()

        # Loop through all spawn points in this list
        for spawnpoint in self:

            # Calculate the distances between this spawn point and player origins
            distances = [origin.get_distance(spawnpoint) for origin in player_origins]

            # Append the spawn point to the possible list, if it is safe to spawn on
            if min(distances) >= cvar_spawn_point_distance.get_float():
                possible.append(spawnpoint)

        # Return a random spawn point if we found any possible ones
        if possible:
            return random.choice(possible)

        # Return None if we haven't found any possible spawn point
        return None

    @property
    def json_file(self):
        """Return the path to the JSON file for the current map."""
        return _spawnpoints_path.joinpath(global_vars.map_name + '.json')


# Store an instance of _SpawnPoints globally & load all vectors for the current map
spawnpoints = _SpawnPoints()
spawnpoints.load()


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class PlayerEntity(Player):
    """Convenience class used for the following things:

        - Wrap players.entity.Player.give_named_item() to return an actual weapons.entity.Weapon instance
        - Provide a safe and easy way to access the player's inventory"""

    def give_named_item(self, classname):
        """Make sure to correct the classname before passing it to the base give_named_item() method."""
        super().give_named_item(Weapons.format_classname(classname))

    def _protect(self):
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
        Delay(cvar_spawn_protection_delay.get_int(), self._unprotect)

    def prepare(self):
        """Prepare the player for battle."""
        # Protect the player from any damage
        self._protect()

        # Choose a random spawn point
        spawnpoint = spawnpoints.get_random()

        # Spawn the player on the location found
        if spawnpoint is not None:
            self.origin = spawnpoint
            self.view_angle = spawnpoint.angle

        # Remove all the player's weapons except for 'knife'
        for weapon in self.weapons(not_filters='knife'):
            weapon.remove()

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

    def refill_ammo(self):
        """Refill the player's ammo on reload after the reload animation has finished."""
        if self.active_weapon is not None and 'meele' not in weapons[self.active_weapon.classname].tag:

            # Get the 'next attack' property for the current weapon, plus a tolerance value of one second
            next_attack = self.active_weapon.get_property_float('m_flNextPrimaryAttack') + 1

            # Calculate the amount of time it would take for the reload animation to finish (tolerance included)
            duration = next_attack - global_vars.current_time

            # Refill the weapon's ammo after the reload animation has finished
            Delay(duration, self._refill_ammo)

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

    def _refill_ammo(self):
        """Refill the player's ammo."""
        if self.is_connected() and self.active_weapon is not None\
                and 'meele' not in weapons[self.active_weapon.classname].tag:
            self.active_weapon.ammo = weapons[self.active_weapon.classname].maxammo

    def _unprotect(self):
        """Enable default gameplay, if they're still online."""
        if self.is_connected():

            # Disable god mode
            self.godmode = False

            # Reset the player's color
            self.color = WHITE
