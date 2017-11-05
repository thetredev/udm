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
            lambda player_index: PlayerEntity(player_index).equip(admin=True),
            data=[
                PagedRadioOption('SpawnPoint Manager', SpawnPointManagerMenu(self)),
            ],
            select_callback=lambda menu, player_index, option: option.value.send(player_index)
        )


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Create the Admin menu
admin_menu = _AdminMenu()
