# ../udm/menus.py

"""Provides a convenience class to create weapon menus in an easy way."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioMenu
from menus.radio import PagedRadioOption

# Script Imports
#   Players
from udm.players import PlayerEntity
#   Weapons
from udm.weapons import weapons


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store a map of weapon tag and their udm.weapons._Weapon instances
_weapons_by_tag = {
    tag: weapons.by_tag(tag) for tag in ('secondary', 'primary', 'grenade')
}


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _WeaponMenu(PagedRadioMenu):
    """Convenience class used to create weapon menus dynamically on-the-fly."""

    def __init__(self, tag, title, next_menu):
        """Initialize this menu using the given tag."""
        # Call the super class constructor using the list of weapons mapped to the tag
        # and this menu's select callback
        super().__init__(
            [PagedRadioOption(weapon.display_name, weapon.basename) for weapon in _weapons_by_tag[tag]],
            select_callback=self.select_callback, title=title
        )

        # Store the next menu
        self._next_menu = next_menu

    def select_callback(self, menu, player_index, option):
        """Handle the chosen menu item."""
        # Give the player the weapon they chose
        PlayerEntity(player_index).inventory.append(option.value)

        # Send the next menu to the player if it is a valid menu instance
        if self._next_menu is not None:
            self._next_menu.send(player_index)


# =============================================================================
# >> PUBLIC GLOBAL VARAIBLES
# =============================================================================
# Create the Grenade menu without any <next_menu>
grenade_menu = _WeaponMenu('grenade', 'Grenade', None)

# Create the Primary Weapons menu using the Grenade menu as the <next_menu> parameter
primary_menu = _WeaponMenu('primary', 'Primary Weapons', grenade_menu)

# Create the Secondary Weapons menu using the Primary Weapons menu as the <next_menu> parameter
secondary_menu = _WeaponMenu('secondary', 'Secondary Weapons', primary_menu)
