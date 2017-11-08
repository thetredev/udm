# ../udm/menus/callbacks.py

"""Provides callback decorators for build, close, and select menu callbacks."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Script Imports
#   Players
from udm.players import PlayerEntity


# =============================================================================
# >> BASE CALLBACK DECORATOR
# =============================================================================
class _CloseMenuCallback(object):
    """Class used to provide a base for later callback decorators."""

    def __init__(self, menu):
        """Store the menu."""
        self._menu = menu


# =============================================================================
# >> BUILD CALLBACK DECORATOR
# =============================================================================
class BuildCallback(_CloseMenuCallback):
    """Class used to store the decorated callback as the `build_callback` for the registered menu."""

    def __call__(self, callback):
        """Store a redirect call to the decorated callback for `build_callback`."""
        self._menu.build_callback = lambda menu, player_index: \
            callback(PlayerEntity(player_index), menu)


# =============================================================================
# >> CLOSE CALLBACK DECORATOR
# =============================================================================
class CloseCallback(_CloseMenuCallback):
    """Class used to store the decorated callback as the `close_callback` for the registered menu."""

    def __call__(self, callback):
        """Store a redirect call to the decorated callback for `close_callback`."""
        self._menu.close_callback = lambda player_index: \
            callback(PlayerEntity(player_index))


# =============================================================================
# >> SELECT CALLBACK DECORATOR
# =============================================================================
class SelectCallback(_CloseMenuCallback):
    """Class used to store the decorated callback as the `select_callback` for the registered menu."""

    def __call__(self, callback):
        """Store a redirect call to the decorated callback for `select_callback`."""
        self._menu.select_callback = lambda menu, player_index, option:\
            callback(PlayerEntity(player_index), option)
