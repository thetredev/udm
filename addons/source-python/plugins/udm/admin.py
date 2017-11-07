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
# >> ADMIN MENU
# =============================================================================
class _AdminMenu(CloseButtonPagedMenu):
    """Class used to provide a base menu with the following submenus:

        * Spawn Point Manager
    """

    def __init__(self):
        """Object initialization."""
        super().__init__(
            close_callback=self._close_callback,
            select_callback=lambda menu, player_index, option: option.value.send(player_index),
            data=[
                PagedRadioOption('SpawnPoint Manager', SpawnPointManagerMenu(self)),
            ]
        )

    def _close_callback(self, player_index):
        """Enable default gameplay for the admin player who just closed this menu."""
        # Get a PlayerEntity instance for the player
        player = PlayerEntity(player_index)

        # Equip the player with their inventory selection
        player.equip_inventory(inventory_index=player.inventory_selection)

        # Disable damage protection
        player.disable_damage_protection()

        # Give knife
        player.give_named_item('weapon_knife')


# Store a global instance of `_AdminMenu`
admin_menu = _AdminMenu()
