# ../udm/weapons/menus.py

"""Provides Secondary and Primary Weapons menus."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus import PagedMenu
from menus import PagedOption

# Script Imports
#   Players
from udm.players import PlayerEntity
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def options_for_tag(tag):
    """Yield each weapon as a `PagedRadioOption` for `tag`."""
    for weapon_data in weapon_manager.by_tag(tag):
        yield PagedOption(weapon_data.display_name, weapon_data.basename)


# =============================================================================
# >> SECONDARY WEAPONS MENU
# =============================================================================
# Create the Secondary Weapons menu
secondary_menu = PagedMenu(data=list(options_for_tag('secondary')), title='Secondary Weapons')


@secondary_menu.register_close_callback
def on_close_secondary_menu(menu, player_index):
    """Remove the secondary weapon from the player's inventory."""
    player = PlayerEntity(player_index)
    player.inventory.remove_inventory_item(player, 'secondary')

    # Equip random weapons if the player's inventory is empty
    if not player.inventory:
        player.equip_random_weapons()


@secondary_menu.register_select_callback
def on_select_secondary_weapon(menu, player_index, option):
    """Add the secondary weapon to the player's inventory."""
    player = PlayerEntity(player_index)
    player.inventory.add_inventory_item(player, option.value)


# =============================================================================
# >> PRIMARY WEAPONS MENU
# =============================================================================
# Create the Primary Weapons menu
primary_menu = PagedMenu(data=list(options_for_tag('primary')), title='Primary Weapons')


@primary_menu.register_close_callback
def on_close_primary_menu(menu, player_index):
    """Remove the primary weapon from the player's inventory."""
    player = PlayerEntity(player_index)
    player.inventory.remove_inventory_item(player, 'primary')

    # Send the secondary menu to the player
    secondary_menu.send(player.index)


@primary_menu.register_select_callback
def on_select_primary_weapon(menu, player_index, option):
    """Add the primary weapon to the player's inventory."""
    player = PlayerEntity(player_index)
    player.inventory.add_inventory_item(player, option.value)

    # Send the secondary menu to the player
    secondary_menu.send(player.index)
