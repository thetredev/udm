# ../udm/config/__init__.py

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
# >> CONFIGURATION CVARS
# =============================================================================
# Write the configuration file ../cfg/source-python/udm.cfg
with ConfigManager(info.name, f'{info.name}_') as config:

    config.text('----------------------------------')
    config.text('   * General')
    config.text('----------------------------------')

    # The respawn delay in seconds
    cvar_respawn_delay = config.cvar(
        'respawn_delay', 2, 'The respawn delay in seconds.'
    )

    # Enable or disable non-blocking mode for players
    cvar_enable_noblock = config.cvar(
        'enable_noblock', 1,
        'Enable or disable non-blocking mode for players.'
    )

    # The spawn protection duration in seconds
    cvar_spawn_protection_delay = config.cvar(
        'spawn_protection_delay', 2, 'The spawn protection delay in seconds.'
    )

    # Refill the killer's clip if they killed an enemy with a headshot
    cvar_refill_clip_on_headshot = config.cvar(
        'refill_clip_on_headshot', 1,
        "Refill the killer's clip if they killed an enemy with a headshot."
    )

    # Restore the killer's health to 100HP if they killed an enemy with the knife
    cvar_restore_health_on_knife_kill = config.cvar(
        'restore_health_on_knife_kill', 1,
        "Restore the killer's health to 100HP if they killed an enemy with the knife."
    )

    # The minimum distance players have to have between a spawn point for it to be 'safe'
    cvar_spawn_point_distance = config.cvar(
        'spawn_point_distance', 150,
        "The minimum distance players have to have between a spawn point for it to be 'safe'."
    )

    # The maximum amount of times a players are allowed to change their team per round.
    cvar_team_changes_per_round = config.cvar(
        'team_changes_per_round', 2,
        'The maximum amount of times a players are allowed to change their team per round.'
    )

    # The time in minutes a player who exceeded the maximum team change count has to wait until they can choose a
    # team again
    cvar_team_changes_reset_delay = config.cvar(
        'team_changes_reset_delay', 1.5,
        'The time in minutes a player who exceeded the maximum team change count has to wait until they can choose a'
        'team again.'
    )

    config.text('----------------------------------')
    config.text('   * Chat Commands')
    config.text('----------------------------------')

    # The chat command used to open the admin menu
    cvar_saycommand_admin = config.cvar(
        'saycommand_admin', '!udm', 'The chat command used to open the admin menu.'
    )

    # The chat command used to open the weapons menu
    cvar_saycommand_guns = config.cvar(
        'saycommand_guns', 'guns', 'The chat command used to open the weapons menu.'
    )

    config.text('----------------------------------')
    config.text('   * High Explosive Grenade')
    config.text('----------------------------------')

    # High Explosive grenade equipment behaviour
    cvar_equip_hegrenade = config.cvar(
        'equip_hegrenade', 2, 'High Explosive grenade behaviour'
    )

    # Options for cvar_equip_hegrenade
    cvar_equip_hegrenade.Options.append('0 = Off')
    cvar_equip_hegrenade.Options.append('1 = Equip on spawn')
    cvar_equip_hegrenade.Options.append('2 = Equip on spawn and on each HE grenade kill')
    cvar_equip_hegrenade.Options.append('3 = Equip on spawn and after each detonation')
