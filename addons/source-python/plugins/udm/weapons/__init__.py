# ../udm/weapons/__init__.py

"""Provides convenience classes and global variables for weapon entities."""

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
from weapons.manager import weapon_manager

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store the path to the weapons data file
_weapons_ini = PLUGIN_DATA_PATH.joinpath(info.name, 'weapons', f'{GAME_NAME}.ini')


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _WeaponIter(WeaponIter):
    """Class used to extend filters.weapons.WeaponIter with a method to remove all idle weapons."""

    def remove_idle(self):
        """Remove all idle weapon entities on the server."""
        for weapon in self:
            if weapon.owner is None:
                weapon.remove()


class _Weapon(object):
    """Class used to store information about a weapon."""

    def __init__(self, weapon_class, display_name, tag):
        """Object initialization."""
        # Store the weapon's basename
        self._basename = weapon_class.basename

        # Store the weapon's
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
# >> PUBLIC CLASSES
# =============================================================================
class _Weapons(dict):
    """Class used to map each weapon specified in the weapons data file to a _Weapon object."""

    def __init__(self, data):
        """Object initialization."""
        super().__init__()

        # Update this dictionary with the entries to map
        for tag, weapon_names in data.items():
            self.update({
                weapon_class.name: _Weapon(weapon_class, weapon_names[weapon_class.basename], tag)
                for weapon_class in [weapon_manager[f'{weapon_manager.prefix}{key}'] for key in weapon_names]
            })

        # Store the tags provided
        self._tags = list(data.keys())

    def by_tag(self, tag):
        """Return all _Weapon instances categorized by <tag>."""
        for weapon in self.values():
            if weapon.tag == tag:
                yield weapon

    @property
    def tags(self):
        """Return the tags provided."""
        return self._tags


# =============================================================================
# >> PUBLIC FUNCTIONS
# =============================================================================
def refill_ammo(weapon):
    """Refill the weapon's ammo."""
    if weapon.owner is not None:
        weapon.ammo = weapons[weapon.classname].maxammo


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a global map of weapon classnames and _Weapon objects using the weapon data file
weapons = _Weapons(ConfigObj(_weapons_ini))

# Store an instance of WeaponIter to be able to remove idle weapons
weapon_iter = _WeaponIter()
