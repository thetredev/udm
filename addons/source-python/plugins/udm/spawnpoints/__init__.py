# ../udm/spawnpoints/__init__.py

"""Provides spawn point management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   JSON
import json
#   Random
import random

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Engines
from engines.server import global_vars
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import OnLevelInit
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
# Store an instance of PlayerIter for alive players
_playeriter_alive = PlayerIter('alive')

# Store the path to the plugin's spawn points data
# ../addons/source-python/data/plugins/udm/spawnpoints
_spawnpoints_path = PLUGIN_DATA_PATH.joinpath('udm', 'spawnpoints', GAME_NAME)

# Create the spawn points data path if it does not exist
if not _spawnpoints_path.exists():
    _spawnpoints_path.makedirs()


# =============================================================================
# >> SPAWN POINTS
# =============================================================================
class SpawnPoint(Vector):
    """Class used to attach a QAngle to a Vector and provide a JSON representation for the respective locations."""

    def __init__(self, x, y, z, angle):
        """Object initialization."""
        # Call Vector's constructor using the given xyz-coordinates
        super().__init__(x, y, z)

        # Store the QAngle object
        self._angle = angle

    @property
    def angle(self):
        """Return the QAngle object."""
        return self._angle

    @property
    def json(self):
        """Return a JSON representation of the `self` and `self.angle`."""
        return {
            'vector': [self.x, self.y, self.z],
            'angle': [self.angle.x, self.angle.y, self.angle.z]
        }


class _SpawnPoints(list):
    """Class used to provide spawn point managing functionality:

        * load spawn points from a JSON file
        * save spawn points to a JSON file
        * get a random spawn point
    """

    def get_random(self):
        """Calculate distances between all alive player locations and spawn points and return a random possible one."""
        # Get a shuffled copy of this spawn point list
        shuffled = self.copy()
        random.shuffle(shuffled)

        # Get current origins for alive players
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

        # Return a random spawn point
        if possible:
            return random.choice(possible)

        # Or return None if `possible` is empty
        return None

    def load(self):
        """Load spawn points from the spawn points data file for the current map."""
        # Skip if the file doesn't exist
        if not self.json_file.exists():
            return

        # Read the spawn points data file into memory
        with self.json_file.open() as f:
            contents = json.load(f)

        # Append each entry as a `SpawnPoint` object
        for data in contents:
            self.append(SpawnPoint(*data['vector'], QAngle(*data['angle'])))

    def save(self):
        """Save spawn points to the spawn points data file for the current map."""
        # Skip if we have nothing to save
        if not self:
            return

        # Dump the contents of this list to file
        with self.json_file.open('w') as f:
            json.dump([spawnpoint.json for spawnpoint in self], f, indent=4)

    @property
    def json_file(self):
        """Return the path to the JSON file for the current map."""
        return _spawnpoints_path.joinpath(global_vars.map_name + '.json')


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a global instance of `_SpawnPoints`
spawnpoints = _SpawnPoints()

# Load all spawn points for the current map
spawnpoints.load()


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    """Reload spawn points."""
    spawnpoints.clear()
    spawnpoints.load()
