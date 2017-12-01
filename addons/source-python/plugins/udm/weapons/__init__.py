# ../udm/weapons/__init__.py

"""Provides helper functions and access to the weapon data file."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   ConfigObj
from configobj import ConfigObj

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnEntityDeleted
#   Paths
from paths import PLUGIN_DATA_PATH
#   Weapons
from weapons.manager import weapon_manager as sp_weapon_manager

# Script Imports
#   Delays
from udm.delays import delay_manager
#   Info
from udm.info import info


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def refill_ammo(weapon):
    """Refill the weapon's ammo."""
    if weapon.owner is not None:
        weapon.ammo = weapon_manager.by_name(weapon.weapon_name).maxammo


def remove_weapon(weapon):
    """Safely remove a weapon entity."""
    if weapon.owner is None:
        weapon.remove()


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store the path to the weapons data file
_weapons_ini = PLUGIN_DATA_PATH.joinpath(info.name, 'weapons', f'{GAME_NAME}.ini')


# =============================================================================
# >> WEAPON DATA
# =============================================================================
class _WeaponData(object):
    """Class used to store weapon data."""

    def __init__(self, basename, weapon_class, display_name, tag):
        """Object initialization."""
        # Store the weapon's basename
        self._basename = basename

        # Store the weapon's clip
        self._clip = weapon_class.clip

        # Store the weapon's display name
        self._display_name = display_name

        # Store the weapon's name
        self._name = weapon_class.name

        # Store the weapon's maxammo value
        self._maxammo = weapon_class.maxammo

        # Store the weapon's primary tag
        self._tag = tag

    @property
    def basename(self):
        """Return the weapon's basename."""
        return self._basename

    @property
    def can_silence(self):
        """Return whether the weapon can be silenced."""
        if 'usp' in self.basename:
            return True

        if self.basename == 'm4a1_silencer':
            return True

        if GAME_NAME == 'cstrike' and self.basename == 'm4a1':
            return True

        return False

    @property
    def clip(self):
        """Return the weapon's clip."""
        return self._clip

    @property
    def display_name(self):
        """Return the weapon's display name."""
        return self._display_name

    @property
    def maxammo(self):
        """Return the weapon's maxammo property."""
        return self._maxammo

    @property
    def name(self):
        """Return the weapon's full name."""
        return self._name

    @property
    def tag(self):
        """Return the weapon's primary tag."""
        return self._tag


# =============================================================================
# >> WEAPON MANAGER
# =============================================================================
class _WeaponManager(dict):
    """Class used to manage weapons listed in the weapons data file."""

    def __init__(self, data_file):
        """Object initialization."""
        # Call dict's constructor
        super().__init__()

        # Update this dictionary with the weapon data file entries
        for tag, weapon_names in data_file.items():
            for basename, displayname in weapon_names.items():

                # Get the weapon class from Source.Python's `weapon_manager`
                weapon_class = sp_weapon_manager[basename.replace('_silenced', '')]

                # Store the `_WeaponData` object at `basename`
                self[basename] = _WeaponData(basename, weapon_class, displayname, tag)

        # Store the tags provided by the weapon data file
        self._tags = list(data_file.keys())

    def by_tag(self, tag):
        """Return all _Weapon instances categorized by `tag`."""
        for weapon in self.values():
            if weapon.tag == tag:
                yield weapon

    def by_name(self, name):
        """Return the `_WeaponData` object for the weapon no matter the weapon prefix."""
        basename = name.replace(sp_weapon_manager.prefix, '')

        if basename in self.keys():
            return self[basename]

        return None

    @property
    def tags(self):
        """Return the tags provided by the weapon data file."""
        return self._tags


# Store a global instance of `_WeaponManager`
weapon_manager = _WeaponManager(ConfigObj(_weapons_ini))


# =============================================================================
# >> MELEE WEAPON
# =============================================================================
# Store the melee weapon for the game
melee_weapon = list(WeaponClassIter(is_filters='melee'))[0].name


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def on_entity_deleted(base_entity):
    """Cancel the refill & drop delays for the deleted entity."""
    if base_entity.classname.startswith(sp_weapon_manager.prefix):
        delay_manager.cancel(f'refill_{base_entity.index}')
        delay_manager.cancel(f'drop_{base_entity.index}')
