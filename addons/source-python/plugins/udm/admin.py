# ../udm/admin.py

"""Provides admin functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioMenu
from menus.radio import PagedRadioOption

# Script Imports
#   Spawn Points
from udm.spawnpoints.menus import spawnpoint_manager_menu


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Create the admin menu; on select: send the specified menu to the player
admin_menu = PagedRadioMenu(
    [
        PagedRadioOption('SpawnPoint Manager', spawnpoint_manager_menu)
    ],
    select_callback=lambda menu, player_index, option: option.value.send(player_index)
)
