# ../udm/spawnpoints/__init__.py

"""Provides convenience classes for player entities and a player inventory class."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Pyhton Imports
#   JSON
import json
#   Random
import random

# Source.Python Imports
#   Engines
from engines.server import global_vars
#   Filters
from filters.players import PlayerIter
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Paths
from paths import PLUGIN_DATA_PATH

# Script Imports
#   Config
from udm.config import cvar_spawn_point_distance


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a PlayerIter instance for alive players
_playeriter_alive = PlayerIter('alive')

# Store the path to the plugin's spawn points data
_spawnpoints_path = PLUGIN_DATA_PATH.joinpath('udm', 'spawnpoints')

# Create the spawn points data path if it does not exist
if not _spawnpoints_path.exists():
    _spawnpoints_path.makedirs()


# =============================================================================
# >> PUBLIC CLASSES
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


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
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
        # Get a shuffled copy of this list
        shuffled = self.copy()
        random.shuffle(shuffled)

        # Get origins for alive players
        player_origins = [player.origin for player in _playeriter_alive]

        # Store possible vectors to spawn on
        possible = list()

        # Loop through the shuffled spawn points list
        for spawnpoint in shuffled:

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


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store an instance of _SpawnPoints globally & load all vectors for the current map
spawnpoints = _SpawnPoints()
spawnpoints.load()
