# ../udm/udm.py

"""Main plugin module: adds Deathmatch gameplay."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Commands
from commands.typed import TypedSayCommand

# Script Imports
#   Config
from udm.config import cvar_saycommand
#   Menus
from udm.menus import secondary_menu


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand.get_string())
def on_saycommand_guns(command_info):
    """Send the Secondary Weapons menu to the player."""
    # Send the Secondary Weapons menu to the player
    secondary_menu.send(command_info.index)

    # Block the text from appearing in the chat
    return False
