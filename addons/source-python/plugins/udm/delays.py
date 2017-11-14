# ../udm/delays.py

"""Provides delay management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import AutoUnload
#   Listeners
from listeners import OnLevelEnd
from listeners.tick import Delay


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

    def __call__(self, key, delay_time, callback, args=()):
        """Append a Delay instance for `key`."""
        self[key].append(Delay(delay_time, callback, args))

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
@OnLevelEnd
def on_level_end():
    """Cancel all pending delays."""
    delay_manager.cancel_all()
