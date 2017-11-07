# ../udm/menus.py

"""Provides a convenience class to add a 'close callback' to the PagedRadioMenu."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import BUTTON_CLOSE
from menus.radio import PagedRadioMenu


# =============================================================================
# >> PUBLIC CLASSES
# =============================================================================
class CloseButtonPagedMenu(PagedRadioMenu):
    """Menu class used to react to the 'close' button."""

    def __init__(self, close_callback, **kwargs):
        """Object initialization."""
        super().__init__(**kwargs)

        # Store the close callback
        self._close_callback = close_callback

    def _select(self, player_index, choice_index):
        """Override _select() to be able to react to the 'close' button within this menu."""
        # Call the close callback if the 'close' button has been selected
        if choice_index == BUTTON_CLOSE:
            self._close_callback(player_index)

        # Continue the base class routine
        return super()._select(player_index, choice_index)
