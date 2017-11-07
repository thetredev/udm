# ../udm/maps.py

"""Provides map function handling."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
#   Filters
from filters.entities import EntityIter


# =============================================================================
# >> MAP FUNCTIONS
# =============================================================================
class _MapFunctions(list):
    """Class used to enable and disable map function entities."""

    def disable(self):
        """Call the `Disable` input for all entity iterators in this list."""
        self._call_input('Disable')

    def enable(self):
        """Call the `Enable` input for all entity iterators in this list."""
        self._call_input('Enable')

    def _call_input(self, value):
        """Call the `value` input for all entities in each entity iterator in this list."""
        for it in self:
            for entity in it:
                entity.call_input(value)


# Store a global instance of `_MapFunctions`
map_functions = _MapFunctions([
    EntityIter('func_buyzone'),
    EntityIter('func_bomb_target'),
    EntityIter('func_hostage_rescue')
])
