# ../udm/delays.py

"""Provides convenience classes for delay management."""


# =============================================================================
# >> PRIVATE CLASSES
# =============================================================================
class _DelayManager(dict):
    """Class used to store all delays so they can be cancelled when needed."""

    def __missing__(self, key):
        """Set and return an empty list as the key's value."""
        value = self[key] = list()
        return value

    def cancel_delays(self, key):
        """Cancel all delays for the given key."""
        # Get the delay list for the given key
        delay_list = self[key]

        # Cancel all delays in the delay list
        for delay in delay_list:
            if delay.running:
                delay.cancel()

        # Clear the delay list
        delay_list.clear()


# Store a global instance of _DelayManager
delay_manager = _DelayManager()
