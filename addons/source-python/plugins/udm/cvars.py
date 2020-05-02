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
from udm.config import cvar_enable_infinite_ammo
from udm.config import cvar_spawn_protection_delay


# =============================================================================
# >> CLASSES
# =============================================================================
class DefaultConVar(object):
    """Class used to store and reset the default value of a convar."""

    def __init__(self, name, value):
        """Object initialization."""
        # Store the convar
        self.convar = cvar.find_var(name)

        # Store its runtime value
        self.value = value

        # Store its default value, if it exists
        if self.convar is not None:
            self.default = self.convar.get_int()
        else:
            self.default = None

    def manipulate_value(self):
        """Set the manipulated value."""
        if self.convar is not None:
            self.convar.set_int(self.value)

    def set_default_value(self):
        """Set the default value."""
        if self.convar is not None and self.default is not None:
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
    DefaultConVar('mp_solid_teammates', int(cvar_enable_noblock.get_int() == 0)),
    DefaultConVar('mp_respawn_on_death_t', 0),
    DefaultConVar('mp_respawn_on_death_ct', 0),
    DefaultConVar('mp_randomspawn', 0),
    DefaultConVar('mp_randomspawn_los', 0),
    DefaultConVar('mp_buy_during_immunity', 0),
    DefaultConVar('mp_respawn_immunitytime', 0 if cvar_spawn_protection_delay.get_int() > 0 else 2),
    DefaultConVar('sv_infinite_ammo', 0 if cvar_enable_infinite_ammo.get_bool() else 2),
    DefaultConVar('mp_friendlyfire', 0),
    DefaultConVar('mp_freezetime', 0),
    DefaultConVar('mp_dm_bonus_length_max', 0),
    DefaultConVar('mp_dm_bonus_length_min', 0),
    DefaultConVar('mp_dm_time_between_bonus_max', 9999),
    DefaultConVar('mp_dm_time_between_bonus_min', 9999),
    DefaultConVar('mp_do_warmup_period', 0)
])

# Store the convar `mp_restartgame`
mp_restartgame = cvar.find_var('mp_restartgame')
