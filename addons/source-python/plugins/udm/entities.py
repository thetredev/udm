# ../udm/entities.py

"""Provides classes for entity management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Filters
from filters.entities import EntityIter


# =============================================================================
# >> CLASSES
# =============================================================================
class EntityRemover(object):
    """Class used to remove entities from the server."""

    @staticmethod
    def perform_action(entities):
        """Remove all entities specified from the server."""
        for forbidden_entity_classname in entities:
            for entity in EntityIter(forbidden_entity_classname):
                entity.remove()


class EntityInputDispatcher(object):
    """Class used to dispatch an input on entities."""

    @staticmethod
    def perform_action(entities, input_name):
        """Dispatch the specified input on all entities."""
        for forbidden_entity_classname in entities:
            for entity in EntityIter(forbidden_entity_classname):
                entity.call_input(input_name)
