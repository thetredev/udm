# ../udm/cvars.py

"""Provides dynamic ConVar manipulation."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Core
from core import AutoUnload
#   Cvars
from cvars import cvar

# Script Imports
#   Config
from udm.config import cvar_enable_noblock


# =============================================================================
# >> MANIPULATED INTEGER CONVARS
# =============================================================================
class _ManipulatedIntConVar(AutoUnload):
    """Class used to manipulate an integer convar on load & reset the default value on unload."""

    def __init__(self, name, manipulated_value):
        """Object initialization."""
        # Store the convar
        self._convar = cvar.find_var(name)

        # Get its default value if the convar exists
        self._default = None if self._convar is None else self._convar.get_int()

        # Store the manipulated value
        self._manipulated_value = manipulated_value

    def manipulate_value(self):
        """Set the manipulated value."""
        if self._convar is not None:
            self._convar.set_int(self._manipulated_value)

    def set_default_value(self):
        """Set the default value."""
        if self._convar is not None:
            self._convar.set_int(self._default)

    def _unload_instance(self):
        """Set the default value on unload."""
        self.set_default_value()


class _ManipulatedIntConVars(list):
    """Class used to set desired values for each specified `ManipulatedIntConVar` instance."""

    def manipulate_values(self):
        """Set manipulated values."""
        for convar in self:
            convar.manipulate_value()


# Store a global instance of `ManipulatedIntConVars`
manipulated_int_convars = _ManipulatedIntConVars([
    _ManipulatedIntConVar('mp_buytime', 60 * 60),
    _ManipulatedIntConVar('mp_startmoney', 10_000),
    _ManipulatedIntConVar('mp_buy_anywhere', 1),
    _ManipulatedIntConVar('mp_solid_teammates', int(cvar_enable_noblock.get_int() == 0))
])
