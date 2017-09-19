# ../udm/weapons.py

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
# Load the weapon names configuration in ../addons/source-python/data/plugins/udm/weapons/<GAME_NAME>.ini
# If no file has been found, this will be an empty dictionary and the server won't crash
_weapon_names = ConfigObj(PLUGIN_DATA_PATH / info.name / 'weapons' / GAME_NAME + '.ini')


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _Weapon(object):
    """Convenience class used to provide a weapon's display name and tag properties."""

    def __init__(self, weapon_class):
        """Initialize this object with a weapons.instance.WeaponClass instance."""
        # Store the weapon's basename
        self._basename = weapon_class.basename

        # Store the weapon's primary tag
        self._tag = [tag for tag in weapon_class.tags if tag != 'all'][0]

    @property
    def basename(self):
        """Return the weapon's basename."""
        return self._basename

    @property
    def display_name(self):
        """Return the weapon's display name."""
        # Return the name found in _weapon_names
        if self._basename in _weapon_names:
            return _weapon_names[self._basename]

        # Otherwise simply return the weapon's basename
        return self._basename

    @property
    def tag(self):
        """Return the weapon's primary tag."""
        return self._tag


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class Weapons(dict):
    """Convenience class used to mimic weapons.manager.weapon_manager and add a method to return all items by tag."""

    # Store relevant weapon tags in a list
    tags = [tag for tag in weapon_manager.tags if tag != 'all']

    def by_tag(self, tag):
        """Yield all _Weapon instances categorized by <tag>."""
        return [weapon for weapon in self.values() if weapon.tag == tag]

    @staticmethod
    def format_classname(classname):
        """Convenience method to format a classname with the game's weapon prefix."""
        # Add the weapon prefix to the classname if the classname doesn't start with it
        if not classname.startswith(weapon_manager.prefix):
            classname = f'{weapon_manager.prefix}{classname}'

        # Return the (formatted) classname
        return classname


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a map of weapon classname and _Weapon instance for all weapons found in weapons.manager.weapon_manager
weapons = Weapons({
    classname: _Weapon(weapon_class) for classname, weapon_class in weapon_manager.items()
})
