# ../udm/spawnpoints/menus.py

"""Provides a submenu for the Admin menu to manage spawn points in-game."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus import PagedMenu
from menus import PagedOption

# Script Imports
#   Admin
from udm.admin import admin_menu
#   Colors
from udm.colors import MESSAGE_COLOR_ORANGE
from udm.colors import MESSAGE_COLOR_WHITE
#   Players
from udm.players import PlayerEntity
#   Spawn Points
from udm.spawnpoints import SAFE_SPAWN_DISTANCE
from udm.spawnpoints import spawnpoint_manager
from udm.spawnpoints import SpawnPoint


# =============================================================================
# >> CONSTANTS
# =============================================================================
# Player location distance tolerance to a spawn point (in units)
SPAWN_POINT_TOLERANCE_UNITS = 20.0


# =============================================================================
# >> SPAWN POINTS MANAGER MENU
# =============================================================================
def add_spawnpoint_at_player_location(player):
    """Add a the player's current location as a spawn point."""
    # Get a list of the distance of all spawn points to the player's current location
    distances = [spawnpoint.get_distance(player.origin) for spawnpoint in spawnpoint_manager]

    # Add the player's current location, if it is far enough away from all other spawn points
    if not distances or min(distances) >= SAFE_SPAWN_DISTANCE:
        spawnpoint_manager.append(SpawnPoint(player.origin.x, player.origin.y, player.origin.z, player.view_angle))

        # Tell the player about the addition
        player.tell(
            spawnpoints_manager_menu.title,
            f'Spawn Point {MESSAGE_COLOR_WHITE}#{len(spawnpoint_manager)} {MESSAGE_COLOR_ORANGE}has been added.'
        )

    # Send the spawn points manager menu back to the player
    spawnpoints_manager_menu.send(player.index)


def remove_spawnpoint_at_player_location(player):
    """Remove the spawn point at the player's current location."""
    # Find the spawn point closest to the player's current location
    for spawnpoint in spawnpoint_manager.copy():
        if spawnpoint in spawnpoint_manager and spawnpoint.get_distance(player.origin) < SPAWN_POINT_TOLERANCE_UNITS:

            # Store its position
            position = spawnpoint_manager.index(spawnpoint) + 1

            # Remove it from the spawn points list
            spawnpoint_manager.remove(spawnpoint)

            # Tell the player about the removal
            player.tell(
                spawnpoints_manager_menu.title,
                f'Spawn Point {MESSAGE_COLOR_WHITE}#{position} {MESSAGE_COLOR_ORANGE}has been removed.'
            )

            # Break the loop
            break

    # Send the spawn points manager menu back to the player
    spawnpoints_manager_menu.send(player.index)


def send_spawnpoints_list_to_player(player):
    """Send the spawn points list menu to the player."""
    _spawnpoints_list_menu.send(player.index)


def save_spawnpoints(player):
    """Save current spawn points to file."""
    spawnpoint_manager.save()

    # Tell the player about it
    player.tell(spawnpoints_manager_menu.title, 'Spawn Points have been saved.')

    # Send the spawn points manager menu back to the player
    spawnpoints_manager_menu.send(player.index)


# Create the Spawn Points Manager menu
spawnpoints_manager_menu = PagedMenu(
    [
        PagedOption('Add', add_spawnpoint_at_player_location),
        PagedOption('Remove', remove_spawnpoint_at_player_location),
        ' ',
        PagedOption('List', send_spawnpoints_list_to_player),
        ' ',
        PagedOption('Save', save_spawnpoints)
    ], title='Spawn Points Manager'
)


# =============================================================================
# >> SPAWN POINTS LIST MENU
# =============================================================================
# Create the Spawn Points List menu
_spawnpoints_list_menu = PagedMenu(title='Spawn Points List')


# =============================================================================
# >> SPAWN POINTS LIST MENU CALLBACKS
# =============================================================================
@_spawnpoints_list_menu.register_build_callback
def on_spawnpoints_list_menu_build(menu, player_index):
    """Reload the menu with all available spawn points."""
    menu.clear()
    menu.extend([PagedOption(f'#{index + 1}', spawnpoint) for index, spawnpoint in enumerate(spawnpoint_manager)])


@_spawnpoints_list_menu.register_select_callback
def on_spawnpoints_list_menu_select(menu, player_index, option):
    """Spawn the player at the selected location."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Set their origin and view angle
    player.origin = option.value
    player.view_angle = option.value.angle

    # Send the Spawn Points Manager menu to the player
    spawnpoints_manager_menu.send(player.index)


@_spawnpoints_list_menu.register_close_callback
def on_spawnpoints_list_menu_close(menu, player_index):
    """Send the Spawn Points Manager menu to the player."""
    spawnpoints_manager_menu.send(player_index)


# =============================================================================
# >> SPAWN POINTS MANAGER MENU CALLBACKS
# =============================================================================
@spawnpoints_manager_menu.register_select_callback
def on_spawnpoints_manager_menu_select(menu, player_index, option):
    """Handle the selected option."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Call the callback function from `option` on `player`
    option.value(player)


@spawnpoints_manager_menu.register_close_callback
def on_spawn_points_manager_menu_close(menu, player_index):
    """Send the Admin Menu when the player closes the Spawn Points Manager menu."""
    admin_menu.send(player_index)
