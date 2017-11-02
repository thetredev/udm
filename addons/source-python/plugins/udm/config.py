# ../udm/config.py

"""Provides cvars for plugin configuration."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> PLUGIN CONFIGURATION CVARS
# =============================================================================
# Write the configuration file ../cfg/source-python/udm.cfg
with ConfigManager(info.name, f'{info.name}_') as config:

    # The delay after which the player gets equipped on spawn
    cvar_equip_delay = config.cvar(
        'equip_delay', 0.0, 'The delay after which the player gets equipped on spawn. Must be positive!'
    )

    cvar_equip_hegrenade = config.cvar(
        'equip_hegrenade', 1, '0 = Off; 1 = Equip on spawn; 2 = Equip on spawn and after each detonation'
    )

    # The respawn delay in seconds
    cvar_respawn_delay = config.cvar(
        'respawn_delay', 2, 'The respawn delay in seconds.'
    )

    # The chat command used to open the weapons menu
    cvar_saycommand = config.cvar(
        'saycommand', 'guns', 'The chat command used to open the weapons menu.'
    )
