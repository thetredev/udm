# ../udm/colors.py

"""Provides chat message colors."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Colors
from colors import WHITE
from colors import ORANGE
#   Core
from core import SOURCE_ENGINE


# =============================================================================
# >> MESSAGE COLORS
# =============================================================================
MESSAGE_COLOR_WHITE = '\x01' if SOURCE_ENGINE == 'csgo' else WHITE
MESSAGE_COLOR_ORANGE = '\x10' if SOURCE_ENGINE == 'csgo' else ORANGE
