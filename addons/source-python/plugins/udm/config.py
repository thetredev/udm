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

    # The chat command used to open the weapons menu
    cvar_saycommand = config.cvar('saycommand', 'guns', 'The chat command used to open the weapons menu.')
