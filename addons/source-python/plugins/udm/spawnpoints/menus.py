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
#   Players
from players.entity import Player

# Script Imports
#   Config
from udm.config import cvar_spawn_point_distance
#   Menus
from udm.menus import CloseButtonPagedMenu
#   Spawn Points
from udm.spawnpoints import spawnpoints
from udm.spawnpoints import SpawnPoint


# =============================================================================
# >> SPAWN POINT LIST MENU
# =============================================================================
class _SpawnPointManagerListMenu(CloseButtonPagedMenu):
    """Class used to provide the following functionality:

        * list all spawn points in a selectable, enumerated format, e.g. #1 for the first spawn point, etc
        * spawn the player to any selected spawn point
        * reload the menu with all available spawn points before it is sent to a player
        * send the parent menu to the player if they choose to close this one
    """

    def __init__(self, parent_menu):
        """Object initialization."""
        super().__init__(
            close_callback=parent_menu.send,
            build_callback=self._build_callback,
            select_callback=self._select_callback
        )

        # Store the parent menu
        self._parent_menu = parent_menu

    def _build_callback(self, menu, player_index):
        """Reload the menu with all available spawn points."""
        menu.clear()
        menu.extend(
            [PagedRadioOption(f'#{index + 1}', spawnpoint) for index, spawnpoint in enumerate(spawnpoints)]
        )

    def _select_callback(self, menu, player_index, option):
        """Spawn the player at the selected location."""
        # Get a Player instance for the player
        player = Player(player_index)

        # Spawn the player at the selected location
        player.origin = option.value
        player.view_angle = option.value.angle

        # Send the parent menu
        self._parent_menu.send(player_index)


# =============================================================================
# >> SPAWN POINT MANAGER MENU
# =============================================================================
class _SpawnPointManagerMenuOptions(IntEnum):
    """Class used to enumerate options for the Spawn Point Manager menu."""

    ADD = 0,
    REMOVE = 1
    LIST = 2
    SAVE = 3


class SpawnPointManagerMenu(CloseButtonPagedMenu):
    """Class used to manage spawn points."""

    def __init__(self, parent_menu):
        """Object initialization."""
        # Add `Add`, `Remove`, `List` and `Save` options
        super().__init__(
            close_callback=parent_menu.send,
            data=[
                PagedRadioOption('Add', _SpawnPointManagerMenuOptions.ADD),
                PagedRadioOption('Remove', _SpawnPointManagerMenuOptions.REMOVE),
                ' ',
                PagedRadioOption('List', _SpawnPointManagerListMenu(self)),
                ' ',
                PagedRadioOption('Save', _SpawnPointManagerMenuOptions.SAVE)
            ], select_callback=self._select_callback, title='Spawn Point Manager'
        )

    def _select_callback(self, menu, player_index, option):
        """Handle the selected option."""
        # Get a Player instance for the player
        player = Player(player_index)

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
                ).send(player_index)

            # Send this menu back to the player
            menu.send(player_index)

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
                    ).send(player_index)

                    # Break the loop
                    break

            # Send this menu back to the player
            menu.send(player_index)

        # Handle the option `Save`
        elif option.value == _SpawnPointManagerMenuOptions.SAVE:

            # Save the spawn points list to file
            spawnpoints.save()

            # Tell the player about it
            SayText2(f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Points have been saved.').send(player_index)

            # Send this menu back to the player
            menu.send(player_index)

        # For `List`: Send the _SpawnPointManagerListMenu to the player
        else:
            option.value.send(player_index)
