# ../udm/admin.py

"""Provides the Admin menu."""

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
#   Spawn Points
from udm.spawnpoints.menus import SpawnPointManagerMenu


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _AdminMenu(CloseButtonPagedMenu):
    """Class used to provide a base menu for each of the following submenus:

        - Spawn Point Manager
    """

    def __init__(self):
        """Object initialization"""
        super().__init__(
            close_callback=self._close_callback,
            select_callback=lambda menu, player_index, option: option.value.send(player_index),
            data=[
                PagedRadioOption('SpawnPoint Manager', SpawnPointManagerMenu(self)),
            ]
        )

    def _close_callback(self, player_index):
        """Enable default gameplay for the admin player who just closed this menu."""
        player = PlayerEntity(player_index)

        player.equip(inventory_index=player.inventory_selection)
        player.unprotect()
        player.give_named_item('weapon_knife')


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Create the Admin menu
admin_menu = _AdminMenu()
