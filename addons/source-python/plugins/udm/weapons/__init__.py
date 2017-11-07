# ../udm/weapons/__init__.py

"""Provides helper functions and an interface between the weapon data file and the plugin."""

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
from filters.weapons import WeaponIter as WeaponIter
#   Paths
from paths import PLUGIN_DATA_PATH
#   Weapons
from weapons.manager import weapon_manager as sp_weapon_manager

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def refill_ammo(weapon):
    """Refill the weapon's ammo."""
    if weapon.owner is not None:
        weapon.ammo = weapon_manager.by_name(weapon.classname).maxammo


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store the path to the weapons data file
_weapons_ini = PLUGIN_DATA_PATH.joinpath(info.name, 'weapons', f'{GAME_NAME}.ini')


# =============================================================================
# >> WEAPON ITERATOR
# =============================================================================
class _WeaponIter(WeaponIter):
    """Class used to provide a method to remove all idle weapon entities from the server."""

    def remove_idle(self):
        """Remove all idle weapon entities on the server."""
        for weapon in self:
            if weapon.owner is None:
                weapon.remove()


# Store a global instance of `_WeaponIter`
weapon_iter = _WeaponIter()


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

        # Store whether the weapon should be silenced
        self._silenced = basename.endswith('_silenced')

    @property
    def basename(self):
        """Return the weapon's basename."""
        return self._basename

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
    def silenced(self):
        """Return whether the weapon should be silenced."""
        return self._silenced

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
                weapon_class = sp_weapon_manager[f"{sp_weapon_manager.prefix}{basename.replace('_silenced', '')}"]

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
        return self[f"{name.replace(sp_weapon_manager.prefix, '')}"]

    def silencer_allowed(self, basename):
        """Return whether the weapon of classname `name` is allowed to be silenced."""
        return basename in self.keys() and basename.replace('_silenced', '') in self.keys()

    @property
    def tags(self):
        """Return the tags provided by the weapon data file."""
        return self._tags


# Store a global instance of `_WeaponManager`
weapon_manager = _WeaponManager(ConfigObj(_weapons_ini))

# Store a global list of melee weapons for the game
melee_weapons = [weapon.name for weapon in sp_weapon_manager.values() if 'melee' in weapon.tags]
