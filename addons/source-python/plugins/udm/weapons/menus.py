# ../udm/weapons/menus.py

"""Provides Secondary Weapons and Primary Weapons menus."""

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
from udm.weapons import weapon_manager


# =============================================================================
# >> WEAPON MENU
# =============================================================================
class _WeaponMenu(CloseButtonPagedMenu):
    """Class used to create a weapon menu for any given weapon tag using the weapons data file."""

    def __init__(self, tag, title, next_menu):
        """Create a menu with weapons of the tag in `tag`."""
        super().__init__(
            close_callback=self._close_callback,
            data=[PagedRadioOption(weapon_data.display_name, weapon_data.name) for weapon_data in weapon_manager.by_tag(tag)],
            select_callback=self._select_callback,
            title=title
        )

        # Store the next menu
        self._next_menu = next_menu

    def _close_callback(self, player_index):
        """Send the next menu if the player closes this one."""
        if self._next_menu is not None:
            self._next_menu.send(player_index)

    def _select_callback(self, menu, player_index, option):
        """Equip the player with the selected weapon."""
        player = PlayerEntity(player_index)
        player.inventories[player.inventory_selection].add_weapon(option.value)

        # Send the next menu to the player if it is a valid menu instance
        if self._next_menu is not None:
            self._next_menu.send(player_index)


# Create the Secondary Weapons menu using no `next_menu`
secondary_menu = _WeaponMenu('secondary', 'Secondary Weapons', None)

# Create the Primary Weapons menu using the Secondary Weapons menu as `next_menu`
primary_menu = _WeaponMenu('primary', 'Primary Weapons', secondary_menu)
