# ../udm/config/menus.py

"""Provides cvars for plugin configuration."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioOption

# Script Imports
#   Config
from udm.config import config
#   Menus
from udm.menus import CloseButtonPagedMenu
from udm.menus.decorators import SelectCallback


# =============================================================================
# >> CONFIG MANAGER MENU
# =============================================================================
# Store a global instance of the Config Manager menu
config_manager_menu = CloseButtonPagedMenu(
    data=[PagedRadioOption(key, value) for key, value in config.cvars],
    title='Config Manager'
)


# =============================================================================
# >> CONFIG MANAGER MENU CALLBACKS
# =============================================================================
@SelectCallback(config_manager_menu)
def on_select_config_option(player, option):
    """Send the Config Manager menu back to the player."""
    # Testing purposes...
    config_manager_menu.send(player.index)
