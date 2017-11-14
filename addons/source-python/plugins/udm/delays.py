# ../udm/delays.py

"""Provides delay management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib

# Source.Python Imports
#   Core
from core import AutoUnload
#   Listeners
from listeners import OnClientDisconnect
from listeners import OnLevelEnd
#   Players
from players.helpers import userid_from_index


# =============================================================================
# >> DELAY MANAGER
# =============================================================================
class _DelayList(list):
    """Class used to append delays only when delays are enabled."""

    def append(self, delay):
        """Append the delay only when delays are enabled."""
        if delay_manager.delays_enabled:
            super().append(delay)

        # Otherwise, cancel the delay if it is running
        elif delay.running:
            delay.cancel()

    def cancel_all(self):
        """Cancel all delays in this delay list."""
        for delay in self.copy():
            if delay.running:
                delay.cancel()

        self.clear()


class _DelayManager(dict, AutoUnload):
    """Class used to group delays and cancel any such group if needed."""

    # Remember whether delays are enabled
    delays_enabled = True

    def __missing__(self, key):
        """Set and return an instance of `_DelayList()` as the key's value."""
        value = self[key] = _DelayList()
        return value

    def cancel(self, key):
        """Cancel all delays for `key`."""
        # Get the delay list for `key`
        self[key].cancel_all()

    def cancel_all(self):
        """Cancel all pending delays."""
        self.delays_enabled = False

        for delay_list in self.values():
            delay_list.cancel_all()

        self.clear()

    def _unload_instance(self):
        """Cancel all pending delays on unload."""
        self.cancel_all()


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
        delay_manager.cancel(f"respawn_{userid}")
        delay_manager.cancel(f"protect_{userid}")


@OnLevelEnd
def on_level_end():
    """Cancel all pending delays."""
    delay_manager.cancel_all()
