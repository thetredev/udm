# ../udm/maps.py

"""Provides map function handling."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Core
from core import AutoUnload
#   Filters
from filters.entities import EntityIter


# =============================================================================
# >> MAP FUNCTIONS
# =============================================================================
class _MapFunctions(list, AutoUnload):
    """Class used to enable and disable map function entities."""

    def __call__(self, *args, **kwargs):
        """Call the `value` input from `args` for all entities in each entity iterator in this list, if provided."""
        if len(args) > 0:
            value = args[0]

            for iterator in self:
                for entity in iterator:
                    entity.call_input(value)

    def disable(self):
        """Call the `Disable` input for all entity iterators in this list."""
        self('Disable')

    def enable(self):
        """Call the `Enable` input for all entity iterators in this list."""
        self('Enable')

    def _unload_instance(self):
        """Enable map functions on unload."""
        self.enable()


# Store a global instance of `_MapFunctions`
map_functions = _MapFunctions([
    EntityIter('func_buyzone'),
    EntityIter('func_bomb_target'),
    EntityIter('func_hostage_rescue')
])
