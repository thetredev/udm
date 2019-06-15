# ../udm/spawn_locations/menus.py

"""Provides a submenu for the Admin menu to manage spawn points in-game."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus import PagedMenu
from menus import PagedOption
#   Messages
from messages.colors.saytext2 import ORANGE as MESSAGE_COLOR_ORANGE
from messages.colors.saytext2 import WHITE as MESSAGE_COLOR_WHITE

# Script Imports
#   Admin
from udm.admin import admin_menu
#   Players
from udm.players import PlayerEntity
#   Spawn Locations
from udm.spawn_locations import SAFE_SPAWN_DISTANCE
from udm.spawn_locations import spawn_location_manager
from udm.spawn_locations import SpawnLocation


# =============================================================================
# >> CONSTANTS
# =============================================================================
# Player location distance tolerance to a spawn location (in units)
SPAWN_LOCATION_TOLERANCE_UNITS = 20.0


# =============================================================================
# >> SPAWN LOCATION MANAGER MENU
# =============================================================================
def add_spawn_location_at_player_location(player):
    """Add a the player's current location as a spawn location."""
    # Get a list of the distance of all spawn locations to the player's current location
    distances = [spawn_location.get_distance(player.origin) for spawn_location in spawn_location_manager]

    # Add the player's current location, if it is far enough away from all other spawn locations
    if not distances or min(distances) >= SAFE_SPAWN_DISTANCE:
        spawn_location = SpawnLocation.from_player_location(player)
        spawn_location_manager.append(spawn_location)

        # Tell the player about the addition
        player.tell(
            spawn_location_manager_menu.title,
            f'Spawn Location {MESSAGE_COLOR_WHITE}#{len(spawn_location_manager)} {MESSAGE_COLOR_ORANGE}has been added.'
        )

    # Send the spawn locations manager menu back to the player
    spawn_location_manager_menu.send(player.index)


def remove_spawn_location_at_player_location(player):
    """Remove the spawn location at the player's current location."""
    # Find near spawn locations
    spawn_location_distances = [
        (spawn_location, spawn_location.get_distance(player.origin))
        for spawn_location in spawn_location_manager
    ]

    near_spawn_locations = [
        (spawn_location, distance) for spawn_location, distance in spawn_location_distances
        if distance < SPAWN_LOCATION_TOLERANCE_UNITS
    ]

    # Remove the nearest spawn location from the list
    if near_spawn_locations:
        spawn_location = min(near_spawn_locations, key=lambda x: x[1])

        # Store its position
        position = spawn_location_manager.index(spawn_location) + 1

        # Remove it from the spawn location list
        spawn_location_manager.remove(spawn_location)

        # Tell the player about the removal
        player.tell(
            spawn_location_manager_menu.title,
            f'Spawn Location {MESSAGE_COLOR_WHITE}#{position} {MESSAGE_COLOR_ORANGE}has been removed.'
        )

    # Send the spawn location manager menu back to the player
    spawn_location_manager_menu.send(player.index)


def send_spawn_location_list_to_player(player):
    """Send the spawn location list menu to the player."""
    spawn_location_list_menu.send(player.index)


def save_spawn_locations(player):
    """Save current spawn locations to file."""
    spawn_location_manager.save()

    # Tell the player about it
    player.tell(spawn_location_manager_menu.title, 'Spawn Locations have been saved.')

    # Send the spawn location manager menu back to the player
    spawn_location_manager_menu.send(player.index)


# Create the Spawn Location Manager menu
spawn_location_manager_menu = PagedMenu(
    [
        PagedOption('Add', add_spawn_location_at_player_location),
        PagedOption('Remove', remove_spawn_location_at_player_location),
        ' ',
        PagedOption('List', send_spawn_location_list_to_player),
        ' ',
        PagedOption('Save', save_spawn_locations)
    ], title='Spawn Location Manager'
)


# =============================================================================
# >> SPAWN LOCATION LIST MENU
# =============================================================================
# Create the Spawn Location List menu
spawn_location_list_menu = PagedMenu(title='Spawn Location List')


# =============================================================================
# >> SPAWN LOCATION LIST MENU CALLBACKS
# =============================================================================
@spawn_location_list_menu.register_build_callback
def on_spawn_location_list_menu_build(menu, player_index):
    """Reload the menu with all available spawn locations."""
    menu.clear()
    menu.extend([
        PagedOption(f'#{index + 1}', spawn_location) for index, spawn_location in enumerate(spawn_location_manager)
    ])


@spawn_location_list_menu.register_select_callback
def on_spawn_location_list_menu_select(menu, player_index, option):
    """Spawn the player at the selected location."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Move player to the chosen spawn location
    option.value.move_player(player)

    # Send the Spawn Location Manager menu to the player
    spawn_location_manager_menu.send(player.index)


@spawn_location_list_menu.register_close_callback
def on_spawn_location_list_menu_close(menu, player_index):
    """Send the Spawn Location Manager menu to the player."""
    spawn_location_manager_menu.send(player_index)


# =============================================================================
# >> SPAWN LOCATION MANAGER MENU CALLBACKS
# =============================================================================
@spawn_location_manager_menu.register_select_callback
def on_spawn_location_manager_menu_select(menu, player_index, option):
    """Handle the selected option."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Call the callback function from `option` on `player`
    option.value(player)


@spawn_location_manager_menu.register_close_callback
def on_spawn_location_manager_menu_close(menu, player_index):
    """Send the Admin Menu when the player closes the Spawn Location Manager menu."""
    admin_menu.send(player_index)
