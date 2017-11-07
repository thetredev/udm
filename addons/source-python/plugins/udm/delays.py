# ../udm/delays.py

"""Provides delay management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib

# Source.Python Imports
#   Listeners
from listeners import OnClientDisconnect
from listeners import OnLevelEnd
#   Players
from players.helpers import userid_from_index


# =============================================================================
# >> DELAY MANAGER
# =============================================================================
class _DelayManager(dict):
    """Class used to group delays and cancel any such group if needed."""

    def __missing__(self, key):
        """Set and return an empty list as the key's value."""
        value = self[key] = list()
        return value

    def cancel_all(self):
        """Cancel all pending delays."""
        for key in self.copy():
            self.cancel_delays(key)

    def cancel_delays(self, key):
        """Cancel all delays for `key`."""
        # Get the delay list for `key`
        delay_list = self[key]

        # Cancel all delays in the delay list
        for delay in delay_list:
            if delay.running:
                delay.cancel()

        # Clear the delay list
        delay_list.clear()


# Store a global instance of `_DelayManager`
delay_manager = _DelayManager()


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnClientDisconnect
def on_client_disconnect(index):
    """Cancel all pending delays of the client."""
    # Note: This is done, because the event 'player_disconnect' somehow does not get fired...
    with contextlib.suppress(ValueError):

        # Get the userid of the client
        userid = userid_from_index(index)

        # Cancel the client's pending delays
        delay_manager.cancel_delays(f"respawn_{userid}")
        delay_manager.cancel_delays(f"protect_{userid}")


@OnLevelEnd
def on_level_end():
    """Cancel all pending delays."""
    delay_manager.cancel_all()
