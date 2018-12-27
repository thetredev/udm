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
# >> CLASSES
# =============================================================================
class DefaultConVar(object):
    """Class used to store and reset the default value of a convar."""

    def __init__(self, name, value):
        """Object initialization."""
        # Store the convar
        self.convar = cvar.find_var(name)

        # Get its default value
        if isinstance(value, int):
            value = self.convar.get_int()

        elif isinstance(value, str):
            value = self.convar.get_string()

        elif isinstance(value, bool):
            value = self.convar.get_bool()

        else:
            raise NotImplementedError(f'Type {type(value)} is not supported for this class.')

        # Store its default value
        self.default = value

        # Store its runtime value
        self.value = value

    def manipulate_value(self):
        """Set the manipulated value."""
        if self.convar is not None:
            self.convar.set_int(self.value)

    def set_default_value(self):
        """Set the default value."""
        if self.convar is not None:
            self.convar.set_int(self.default)


class DefaultConVars(AutoUnload, list):
    """Class used as a list of default convars."""

    def manipulate_values(self):
        """Set manipulated values."""
        for convar in self:
            convar.manipulate_value()

    def set_default_values(self):
        """Set default values."""
        for convar in self:
            convar.set_default_value()

    def _unload_instance(self):
        """Set the default value on unload."""
        self.set_default_values()
        self.clear()


# Store a global instance of `DefaultConVars`
default_convars = DefaultConVars([
    DefaultConVar('mp_buytime', 60 * 60),
    DefaultConVar('mp_startmoney', 10_000),
    DefaultConVar('mp_buy_anywhere', 1),
    DefaultConVar('mp_solid_teammates', int(cvar_enable_noblock.get_int() == 0))
])

# Store the convar `mp_restartgame`
mp_restartgame = cvar.find_var('mp_restartgame')
