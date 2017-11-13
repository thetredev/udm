# ../udm/info.py

"""Provides/stores information about the plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Plugins
from plugins.manager import plugin_manager


# =============================================================================
# >> PLUGIN INFO
# =============================================================================
info = plugin_manager.get_plugin_info(__name__)
