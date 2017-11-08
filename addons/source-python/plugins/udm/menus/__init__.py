# ../udm/menus/__init__.py

"""Provides the `CloseButtonPagedMenu` which calls a callback when a player decides to close the menu."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import AutoUnload
#   Filters
from filters.players import PlayerIter
#   Menus
from menus.radio import BUTTON_CLOSE
from menus.radio import PagedRadioMenu


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store an instance of `PlayerIter` for all players
_playeriter_all = PlayerIter()


# =============================================================================
# >> CLOSE BUTTON PAGED MENU
# =============================================================================
class CloseButtonPagedMenu(PagedRadioMenu, AutoUnload):
    """Class used to call a callback when a player decides to close the menu."""

    def __init__(self, **kwargs):
        """Object initialization."""
        super().__init__(**kwargs)

        # Store the close callback
        self.close_callback = None

    def _select(self, player_index, choice_index):
        """Call the close callback if the close button has been selected."""
        if choice_index == BUTTON_CLOSE:
            self.close_callback(player_index)

        # Continue the base class routine
        return super()._select(player_index, choice_index)

    def _unload_instance(self):
        """ Close the menu for all players on unload."""
        self.close([player.index for player in _playeriter_all])
