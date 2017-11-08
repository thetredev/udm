# ../udm/config/__init__.py

"""Provides cvars for plugin configuration."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager as SpConfigManager

# Script Imports
#   Info
from udm.info import info


# =============================================================================
# >> CONFIG MANAGER
# =============================================================================
class _ConfigManager(SpConfigManager):
    """Class used to provide global access to the config cvars."""

    @property
    def cvars(self):
        """Return a dictionary item generator of the all config cvars."""
        return {
            section.name.replace(self.cvar_prefix, ''): section.cvar for section in self._sections
        }.items()


# =============================================================================
# >> CONFIGURATION CVARS
# =============================================================================
# Write the configuration file ../cfg/source-python/udm.cfg
with _ConfigManager(info.name, f'{info.name}_') as config:

    # The delay after which the player gets equipped on spawn
    cvar_equip_delay = config.cvar(
        'equip_delay', 0.0, 'The delay after which the player gets equipped on spawn. Must be positive!'
    )

    # High Explosive grenade equipment behaviour
    cvar_equip_hegrenade = config.cvar(
        'equip_hegrenade', 1, '0 = Off; 1 = Equip on spawn; 2 = Equip on spawn and after each detonation'
    )

    # The respawn delay in seconds
    cvar_respawn_delay = config.cvar(
        'respawn_delay', 2, 'The respawn delay in seconds.'
    )

    # The minimum distance players have to have between a spawn point for it to be 'safe'
    cvar_spawn_point_distance = config.cvar(
        'spawn_point_distance', 150,
        "The minimum distance players have to have between a spawn point for it to be 'safe'."
    )

    # The spawn protection duration in seconds
    cvar_spawn_protection_delay = config.cvar(
        'spawn_protection_delay', 2, 'The spawn protection delay in seconds.'
    )

    # The chat command used to open the admin menu
    cvar_saycommand_admin = config.cvar(
        'saycommand_admin', '!udm', 'The chat command used to open the admin menu.'
    )

    # The chat command used to open the weapons menu
    cvar_saycommand_guns = config.cvar(
        'saycommand_guns', 'guns', 'The chat command used to open the weapons menu.'
    )
