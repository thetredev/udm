# ../udm/delays.py

"""Provides delay management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import AutoUnload
#   Listeners
from listeners.tick import Delay

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> DELAY MANAGER
# =============================================================================
class _DelayManager(dict, AutoUnload):
    """Class used to manage delays."""

    # Remember whether delays are enabled
    delays_enabled = True

    def __init__(self, prefix):
        """Object initialization."""
        # Call dict's constructor
        super().__init__()

        # Store the key prefix
        self._prefix = prefix

        # Store a mapping of delay callbacks which should be called on cancel
        self._call_on_cancel = dict()

    def __call__(self, key, delay, callback, args=(), call_on_cancel=False):
        """Add the delay object and reference it by `key`."""
        # Format the delay key
        key = self._format_key(key)

        # Cancel the delay for the key, if it is running
        self.cancel(key)

        # Store whether the callback should be called on cancel
        self._call_on_cancel[key] = call_on_cancel

        # Add the delay if delays are enabled
        if self.delays_enabled:
            self[key] = Delay(delay, callback, args)

    def cancel(self, key):
        """Cancel the delay if it is running."""
        # Format the delay key
        key = self._format_key(key)

        if key in self:

            # Get the delay object referenced `key`
            delay = self[key]

            # Cancel it if it is running
            if delay.running:
                if self._call_on_cancel[key]:
                    delay()
                else:
                    delay.cancel()

            # Remove `key` from this dict
            del self[key]
            del self._call_on_cancel[key]

    def clear(self):
        """Cancel all pending delays."""
        for key in self.copy():
            self.cancel(key)

        # Disable delays
        self.delays_enabled = False

    @property
    def prefix(self):
        """Return the key prefix."""
        return self._prefix

    def _format_key(self, key):
        """Prepend `key` with the key prefix."""
        if not key.startswith(self.prefix):
            return f'{self.prefix}_{key}'

        # Return the key if it is already prepended with the key prefix
        return key

    def _unload_instance(self):
        """Cancel all pending delays on unload."""
        self.clear()


# Store a global instance of `_DelayManager`
delay_manager = _DelayManager(info.name)
