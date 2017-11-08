# ../udm/spawnpoints/menus.py

"""Provides a submenu for the Admin menu to manage spawn points in-game."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
from enum import IntEnum

# Source.Python Imports
#   Colors
from colors import WHITE
from colors import ORANGE
#   Menus
from menus.radio import PagedRadioOption
#   Messages
from messages import SayText2

# Script Imports
#   Config
from udm.config import cvar_spawn_point_distance
#   Menus
from udm.menus import CloseButtonPagedMenu
from udm.menus.decorators import BuildCallback
from udm.menus.decorators import CloseCallback
from udm.menus.decorators import SelectCallback
#   Spawn Points
from udm.spawnpoints import spawnpoints
from udm.spawnpoints import SpawnPoint


# =============================================================================
# >> SPAWN POINTS MENUS
# =============================================================================
class _SpawnPointManagerMenuOptions(IntEnum):
    """Class used to enumerate options for the Spawn Point Manager menu."""

    ADD = 0,
    REMOVE = 1
    LIST = 3
    SAVE = 5

    @staticmethod
    def as_menu_options():
        """Return a list of `PagedRadioMenuOption`s for the members of _SpawnPointManagerMenuOptions."""
        # Get a list of the members of _SpawnPointManagerMenuOptions
        members = [e for e in _SpawnPointManagerMenuOptions]

        # Generate a list of menu options from the members
        menu_options = list()
        for index, member in enumerate(members):

            # Get the difference between the member's value and its index in the enum
            diff = member.value - index

            # Extend the options with empty lines if the difference is higher than 0 (`zero`)
            if diff > 0:
                menu_options.extend([' ' for i in range(diff)])

            # Append the actual menu option
            menu_options.append(PagedRadioOption(member.name.capitalize(), member))

        # Return the list of menu options
        return menu_options


# Create the Spawn Points Manager menu
spawnpoints_manager_menu = CloseButtonPagedMenu(
    data=_SpawnPointManagerMenuOptions.as_menu_options(),
    title='Spawn Points Manager'
)


# Create the Spawn Points List menu
_spawnpoints_list_menu = CloseButtonPagedMenu(title='Spawn Points List')


# =============================================================================
# >> SPAWN POINTS LIST MENU CALLBACKS
# =============================================================================
@BuildCallback(_spawnpoints_list_menu)
def on_build_spawnpoints_list_menu(player, menu):
    """Reload the menu with all available spawn points."""
    menu.clear()
    menu.extend(
        [PagedRadioOption(f'#{index + 1}', spawnpoint) for index, spawnpoint in enumerate(spawnpoints)]
    )


@CloseCallback(_spawnpoints_list_menu)
def on_close_spawnpoints_list_menu(player):
    spawnpoints_manager_menu.send(player.index)


@SelectCallback(_spawnpoints_list_menu)
def on_select_spawnpoint(player, option):
    """Spawn the player at the selected location."""
    player.origin = option.value
    player.view_angle = option.value.angle

    # Send the Spawn Points Manager menu
    spawnpoints_manager_menu.send(player.index)


# =============================================================================
# >> SPAWN POINTS MANAGER MENU CALLBACKS
# =============================================================================
@SelectCallback(spawnpoints_manager_menu)
def on_select_spawnpoints_manager_option(player, option):
    """Handle the selected option."""
    # Handle the option `Add`
    if option.value == _SpawnPointManagerMenuOptions.ADD:

        # Get a list of the distance of all spawn points to the player's current location
        distances = [spawnpoint.get_distance(player.origin) for spawnpoint in spawnpoints]

        # Add the player's current location, if it is far enough away from all other spawn points
        if not distances or min(distances) >= cvar_spawn_point_distance.get_float():
            spawnpoints.append(SpawnPoint(player.origin.x, player.origin.y, player.origin.z, player.view_angle))

            # Tell the player about the addition
            SayText2(
                f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Point {WHITE}#{len(spawnpoints)}{ORANGE}'
                ' has been added.'
            ).send(player.index)

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # Handle the option `Remove`
    elif option.value == _SpawnPointManagerMenuOptions.REMOVE:

        # Find the spawn point closest to the player's current location
        for spawnpoint in spawnpoints.copy():
            if spawnpoint in spawnpoints and spawnpoint.get_distance(player.origin) < 20:
                # Store its position
                position = spawnpoints.index(spawnpoint) + 1

                # Remove it from the spawn points list
                spawnpoints.remove(spawnpoint)

                # Tell the player about the removal
                SayText2(
                    f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Point {WHITE}#{position} {ORANGE}'
                    'has been removed.'
                ).send(player.index)

                # Break the loop
                break

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # Handle the option `Save`
    elif option.value == _SpawnPointManagerMenuOptions.SAVE:

        # Save the spawn points list to file
        spawnpoints.save()

        # Tell the player about it
        SayText2(f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Points have been saved.').send(player.index)

        # Send this menu back to the player
        spawnpoints_manager_menu.send(player.index)

    # For `List`: Send the _SpawnPointManagerListMenu to the player
    elif option.value == _SpawnPointManagerMenuOptions.LIST:
        _spawnpoints_list_menu.send(player.index)
