# ../udm/weapons/menus.py

"""Provides a convenience class to create weapon menus in an easy way."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioOption

# Script Imports
#   Menus
from udm.menus import CloseButtonPagedMenu
#   Players
from udm.players import PlayerEntity
#   Weapons
from udm.weapons import weapons


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _WeaponMenu(CloseButtonPagedMenu):
    """Convenience class used to create weapon menus dynamically on-the-fly."""

    def __init__(self, tag, title, next_menu):
        """Initialize this menu using the given tag."""
        # Call the super class constructor using the list of weapons mapped to the tag
        # and this menu's select callback
        super().__init__(
            close_callback=self._close_callback,
            data=[PagedRadioOption(weapon.display_name, weapon.name) for weapon in weapons.by_tag(tag)],
            select_callback=self.select_callback,
            title=title
        )

        # Store the next menu
        self._next_menu = next_menu

    def _close_callback(self, player_index):
        """Send the next menu if the player closes this one."""
        if self._next_menu is not None:
            self._next_menu.send(player_index)

    def select_callback(self, menu, player_index, option):
        """Handle the chosen menu item."""
        # Give the player the weapon they chose
        player = PlayerEntity(player_index)
        player.inventories[player.inventory_selection].add_weapon(option.value)

        # Send the next menu to the player if it is a valid menu instance
        if self._next_menu is not None:
            self._next_menu.send(player_index)


# =============================================================================
# >> PUBLIC GLOBAL VARAIBLES
# =============================================================================
# Create the Secondary Weapons menu using no <next_menu>
secondary_menu = _WeaponMenu('secondary', 'Secondary Weapons', None)

# Create the Primary Weapons menu using the Secondary Weapons menu as the <next_menu> parameter
primary_menu = _WeaponMenu('primary', 'Primary Weapons', secondary_menu)
