# ../udm/spawnpoints/menus.py

"""Provides convenience classes to create an admin menu for spawn point management."""

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
# >> PRIVATE CLASSES
# =============================================================================
class _SpawnPointManagerListMenu(CloseButtonPagedMenu):
    """Menu class used to

        - Enumerate all available spawn points and make them selectable
        - Spawn the player to a selected spawn point
        - Refill the menu with all available spawn points before it is sent to a player
        - React to the 'close' button
    """

    def __init__(self, parent_menu):
        """Initialize this menu using the internal build and select callbacks."""
        super().__init__(
            parent_menu.send,
            build_callback=self._build_callback, select_callback=self._select_callback
        )

        # Store the parent menu
        self._parent_menu = parent_menu

    def _build_callback(self, menu, player_index):
        """Refill the menu with all available spawn points."""
        menu.clear()
        menu.extend(
            [PagedRadioOption(f'#{index + 1}', spawnpoint) for index, spawnpoint in enumerate(spawnpoints)]
        )

    def _select_callback(self, menu, player_index, option):
        """Spawn the player at the selected location."""
        # Get a players.entity.Player instance for the player
        player = Player(player_index)

        # Spawn the player at the selected location
        player.origin = option.value
        player.view_angle = option.value.angle

        # Send them the Spawn Point Manager menu
        self._parent_menu.send(player_index)


class _SpawnPointManagerMenuOptions(IntEnum):
    """Enum class used to enumerate options for the Spawn Point Manager menu."""

    ADD = 0,
    REMOVE = 1
    LIST = 2


class SpawnPointManagerMenu(CloseButtonPagedMenu):
    """Menu class used to manage spawn points."""

    def __init__(self, parent_menu):
        """Initialize this menu using the 'Add', 'Remove', and 'List' options and the internal select callback."""
        super().__init__(
            lambda player_index: parent_menu.send(player_index),
            data=[
                PagedRadioOption('Add', _SpawnPointManagerMenuOptions.ADD),
                PagedRadioOption('Remove', _SpawnPointManagerMenuOptions.REMOVE),
                ' ',
                PagedRadioOption('List', _SpawnPointManagerListMenu(self))
            ], select_callback=self._select_callback, title='Spawn Point Manager'
        )

    def _select_callback(self, menu, player_index, option):
        """Handle the selected option."""
        # Get a players.entity.Player instance for the player
        player = Player(player_index)

        # Handle the option 'Add'
        if option.value == _SpawnPointManagerMenuOptions.ADD:

            # Get a list of the distance of all spawn points to the player's current location
            distances = [spawnpoint.get_distance(player.origin) for spawnpoint in spawnpoints]

            # Evaluate the results...
            if not distances or min(distances) >= cvar_spawn_point_distance.get_float():

                # Add the spawn point to the spawn points list
                spawnpoints.append(SpawnPoint(player.origin.x, player.origin.y, player.origin.z, player.view_angle))

                # Tell the player about the addition
                SayText2(
                    f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Point {WHITE}#{len(spawnpoints)}{ORANGE}'
                    ' has been added.'
                ).send(player_index)

            # Send the menu back to the player
            menu.send(player_index)

        # Handle the option 'Remove'
        elif option.value == _SpawnPointManagerMenuOptions.REMOVE:

            # Find the spawn point closest to the player's current location
            for spawnpoint in spawnpoints.copy():
                if spawnpoint in spawnpoints and spawnpoint.get_distance(player.origin) < 5:

                    # If found, remove it from the spawn points list
                    position = spawnpoints.index(spawnpoint) + 1
                    spawnpoints.remove(spawnpoint)

                    # Tell the player about the removal
                    SayText2(
                        f'{ORANGE}[{WHITE}Admin Menu{ORANGE}] Spawn Point {WHITE}#{position} {ORANGE}'
                        'has been removed.'
                    ).send(player_index)

                    # Break the loop
                    break

            # Send the menu back to the player
            menu.send(player_index)

        # Handle the option 'List': Send the _SpawnPointManagerListMenu to the player
        else:
            option.value.send(player_index)
