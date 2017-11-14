# ../udm/weapons/menus.py

"""Provides Secondary and Primary Weapons menus."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioOption

# Script Imports
#   Menus
from udm.menus import CloseButtonPagedMenu
from udm.menus.decorators import CloseCallback
from udm.menus.decorators import SelectCallback
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def options_for_tag(tag):
    """Yield each weapon as a `PagedRadioOption` for `tag`."""
    for weapon_data in weapon_manager.by_tag(tag):
        yield PagedRadioOption(weapon_data.display_name, weapon_data.basename)


# =============================================================================
# >> WEAPON MENUS
# =============================================================================
# Create the Secondary Weapons menu using no `next_menu`
secondary_menu = CloseButtonPagedMenu(data=list(options_for_tag('secondary')), title='Secondary Weapons')

# Create the Primary Weapons menu using the Secondary Weapons menu as `next_menu`
primary_menu = CloseButtonPagedMenu(data=list(options_for_tag('primary')), title='Primary Weapons')


# =============================================================================
# >> SECONDARY MENU CALLBACKS
# =============================================================================
@CloseCallback(secondary_menu)
def on_close_secondary_menu(player):
    """Remove the secondary weapon from the player's inventory."""
    player.inventory.remove_weapon(player, 'secondary')


@SelectCallback(secondary_menu)
def on_select_secondary_weapon(player, option):
    """Add the secondary weapon to the player's inventory."""
    player.inventory.add_inventory_item(player, option.value)


# =============================================================================
# >> PRIMARY MENU CALLBACKS
# =============================================================================
@CloseCallback(primary_menu)
def on_close_primary_menu(player):
    """Remove the primary weapon from the player's inventory."""
    player.inventory.remove_weapon(player, 'primary')

    # Send the secondary menu to the player
    secondary_menu.send(player.index)


@SelectCallback(primary_menu)
def on_select_primary_weapon(player, option):
    """Add the primary weapon to the player's inventory."""
    player.inventory.add_inventory_item(player, option.value)

    # Send the secondary menu to the player
    secondary_menu.send(player.index)
