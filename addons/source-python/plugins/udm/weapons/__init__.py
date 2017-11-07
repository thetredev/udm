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
from weapons.manager import weapon_manager

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def refill_ammo(weapon):
    """Refill the weapon's ammo."""
    if weapon.owner is not None:
        weapon.ammo = weapons[weapon.classname].maxammo


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
class _Weapon(object):
    """Class used to store weapon data."""

    def __init__(self, weapon_class, display_name, tag):
        """Object initialization."""
        # Store the weapon's display name
        self._display_name = display_name

        # Store the weapon's name
        self._name = weapon_class.name

        # Store the weapon's maxammo value
        self._maxammo = weapon_class.maxammo

        # Store the weapon's primary tag
        self._tag = tag

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
class _Weapons(dict):
    """Class used to manage weapons listed in the weapons data file."""

    def __init__(self, data):
        """Object initialization."""
        # Call dict's constructor
        super().__init__()

        # Update this dictionary with the weapon data file entries
        for tag, weapon_names in data.items():
            self.update({
                weapon_class.name: _Weapon(weapon_class, weapon_names[weapon_class.basename], tag)
                for weapon_class in [weapon_manager[f'{weapon_manager.prefix}{key}'] for key in weapon_names]
            })

        # Store the tags provided by the weapon data file
        self._tags = list(data.keys())

    def by_tag(self, tag):
        """Return all _Weapon instances categorized by `tag`."""
        for weapon in self.values():
            if weapon.tag == tag:
                yield weapon

    @property
    def tags(self):
        """Return the tags provided by the weapon data file."""
        return self._tags


# Store a global instance of `_Weapons`
weapons = _Weapons(ConfigObj(_weapons_ini))
