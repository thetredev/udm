# ../udm/spawnpoints/menus.py

"""Provides a submenu for the Admin menu to manage spawn points in-game."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from enum import IntEnum

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
#   Config
from udm.config import cvar_spawn_point_distance
#   Players
from udm.players import PlayerEntity
#   Spawn Points
from udm.spawnpoints import spawnpoints
from udm.spawnpoints import SpawnPoint


# =============================================================================
# >> SPAWN POINTS MENUS
# =============================================================================
class _SpawnPointsManagerMenuOptions(IntEnum):
    """Class used to enumerate options for the Spawn Points Manager menu."""

    ADD = 0,
    REMOVE = 1
    LIST = 3
    SAVE = 5

    @staticmethod
    def as_menu_options():
        """Return a list of `PagedRadioMenuOption`s for the members of _SpawnPointsManagerMenuOptions."""
        # Get a list of the members of _SpawnPointsManagerMenuOptions
        members = [e for e in _SpawnPointsManagerMenuOptions]

        # Generate a list of menu options from the members
        menu_options = list()
        for index, member in enumerate(members):

            # New lines only apply from the second index onwards
            if index > 0:

                # Get the difference between the member's value and its index in the enum
                diff = member.value - members[index - 1].value

                # Extend the options with empty lines if the difference is higher than 0 (`zero`)
                if diff > 1:
                    menu_options.extend([' ' for i in range(diff - 1)])

            # Append the actual menu option
            menu_options.append(PagedOption(member.name.capitalize(), member))

        # Return the list of menu options
        return menu_options


# Create the Spawn Points Manager menu
spawnpoints_manager_menu = PagedMenu(
    data=_SpawnPointsManagerMenuOptions.as_menu_options(),
    title='Spawn Points Manager'
)


# Create the Spawn Points List menu
_spawnpoints_list_menu = PagedMenu(title='Spawn Points List')


# =============================================================================
# >> SPAWN POINTS LIST MENU CALLBACKS
# =============================================================================
@_spawnpoints_list_menu.register_build_callback
def on_build_spawnpoints_list_menu(menu, player_index):
    """Reload the menu with all available spawn points."""
    menu.clear()
    menu.extend(
        [PagedOption(f'#{index + 1}', spawnpoint) for index, spawnpoint in enumerate(spawnpoints)]
    )


@_spawnpoints_list_menu.register_close_callback
def on_close_spawnpoints_list_menu(menu, player_index):
    """Send the Spawn Points Manager menu to the player."""
    spawnpoints_manager_menu.send(player_index)


@_spawnpoints_list_menu.register_select_callback
def on_select_spawnpoint(menu, player_index, option):
    """Spawn the player at the selected location."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Set their origin and view angle
    player.origin = option.value
    player.view_angle = option.value.angle

    # Send the Spawn Points Manager menu to the player
    spawnpoints_manager_menu.send(player.index)


# =============================================================================
# >> SPAWN POINTS MANAGER MENU CALLBACKS
# =============================================================================
@spawnpoints_manager_menu.register_close_callback
def on_close_spawnpoints_manager_menu(menu, player_index):
    """Send the Admin Menu when the player closes the Spawn Points Manager menu."""
    admin_menu.send(player_index)


@spawnpoints_manager_menu.register_select_callback
def on_select_spawnpoints_manager_option(menu, player_index, option):
    """Handle the selected option."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(player_index)

    # Handle the option `Add`
    if option.value is _SpawnPointsManagerMenuOptions.ADD:

        # Get a list of the distance of all spawn points to the player's current location
        distances = [spawnpoint.get_distance(player.origin) for spawnpoint in spawnpoints]

        # Add the player's current location, if it is far enough away from all other spawn points
        if not distances or min(distances) >= cvar_spawn_point_distance.get_float():
            spawnpoints.append(SpawnPoint(player.origin.x, player.origin.y, player.origin.z, player.view_angle))

            # Tell the player about the addition
            player.tell(
                spawnpoints_manager_menu.title,
                f'Spawn Point {MESSAGE_COLOR_WHITE}#{len(spawnpoints)} {MESSAGE_COLOR_ORANGE}has been added.'
            )

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # Handle the option `Remove`
    elif option.value is _SpawnPointsManagerMenuOptions.REMOVE:

        # Find the spawn point closest to the player's current location
        for spawnpoint in spawnpoints.copy():
            if spawnpoint in spawnpoints and spawnpoint.get_distance(player.origin) < 20:
                # Store its position
                position = spawnpoints.index(spawnpoint) + 1

                # Remove it from the spawn points list
                spawnpoints.remove(spawnpoint)

                # Tell the player about the removal
                player.tell(
                    spawnpoints_manager_menu.title,
                    f'Spawn Point {MESSAGE_COLOR_WHITE}#{position} {MESSAGE_COLOR_ORANGE}has been removed.'
                )

                # Break the loop
                break

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # Handle the option `Save`
    elif option.value is _SpawnPointsManagerMenuOptions.SAVE:

        # Save the spawn points list to file
        spawnpoints.save()

        # Tell the player about it
        player.tell(
            spawnpoints_manager_menu.title, 'Spawn Points have been saved.'
        )

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # For `List`: Send the _SpawnPointManagerListMenu to the player
    elif option.value is _SpawnPointsManagerMenuOptions.LIST:
        _spawnpoints_list_menu.send(player.index)
