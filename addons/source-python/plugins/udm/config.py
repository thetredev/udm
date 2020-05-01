# ../udm/config/__init__.py

"""Provides config cvars for plugin configuration."""

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

# ../cfg/source-python/udm.cfg
with ConfigManager(info.name, f'{info.name}_') as config:

    config.text('Ultimate Deathmatch plugin configuration file')
    config.text(' ')

    config.text('----------------------------------')
    config.text('   * Respawn')
    config.text('----------------------------------')

    cvar_respawn_delay = config.cvar(
        'respawn_delay',
        2,
        'The respawn delay (in seconds).'
    )

    config.text('----------------------------------')
    config.text('   * Spawn Protection')
    config.text('----------------------------------')

    cvar_spawn_protection_delay = config.cvar(
        'spawn_protection_delay',
        2,
        'The spawn protection delay (in seconds).'
    )

    config.text('----------------------------------')
    config.text('   * Infinite Ammo')
    config.text('----------------------------------')

    cvar_enable_infinite_ammo = config.cvar(
        'enable_infinite_ammo',
        1,
        'Enable infinite ammo?'
    )

    config.text('----------------------------------')
    config.text('   * NoBlock')
    config.text('----------------------------------')

    cvar_enable_noblock = config.cvar(
        'enable_noblock',
        1,
        'Enable NoBlock mode for players?'
    )

    config.text('----------------------------------')
    config.text('   * Kill Rewards')
    config.text('----------------------------------')

    cvar_refill_clip_on_headshot = config.cvar(
        'refill_clip_on_headshot',
        1,
        "Refill the players's clip following a headshot kill?"
    )

    cvar_restore_health_on_knife_kill = config.cvar(
        'restore_health_on_knife_kill',
        1,
        "Restore the players's health to 100HP following a knife kill?"
    )

    config.text('----------------------------------')
    config.text('   * High Explosive Grenade Behavior')
    config.text('----------------------------------')

    cvar_equip_hegrenade = config.cvar(
        'equip_hegrenade',
        2,
        'High Explosive grenade behavior'
    )

    cvar_equip_hegrenade.Options.append('0 = Off')
    cvar_equip_hegrenade.Options.append('1 = Equip on spawn')
    cvar_equip_hegrenade.Options.append('2 = Equip on spawn and on each HE grenade kill')
    cvar_equip_hegrenade.Options.append('3 = Equip on spawn and after each detonation')

    config.text('----------------------------------')
    config.text('   * Flashbang Grenade Behavior')
    config.text('----------------------------------')

    cvar_equip_flashbang_grenade = config.cvar(
        'equip_flashbang_grenade',
        3,
        'Flashbang grenade behavior'
    )

    cvar_equip_flashbang_grenade.Options.append('0 = Off')
    cvar_equip_flashbang_grenade.Options.append('1 = Equip on spawn')
    cvar_equip_flashbang_grenade.Options.append('2 = Equip on spawn and after each detonation')
    cvar_equip_flashbang_grenade.Options.append('3 = Equip on spawn and after each kill caused by flashing an enemy')

    config.text('----------------------------------')
    config.text('   * Smoke Grenade Behavior')
    config.text('----------------------------------')

    cvar_equip_smoke_grenade = config.cvar(
        'equip_smoke_grenade',
        3,
        'Smoke grenade behavior'
    )

    cvar_equip_smoke_grenade.Options.append('0 = Off')
    cvar_equip_smoke_grenade.Options.append('1 = Equip on spawn')
    cvar_equip_smoke_grenade.Options.append('2 = Equip on spawn and after each detonation')
    cvar_equip_smoke_grenade.Options.append('3 = Equip on spawn and after killing an enemy trough the smoke')

    config.text('----------------------------------')
    config.text('   * Team Changes Management')
    config.text('----------------------------------')

    cvar_team_changes_per_round = config.cvar(
        'team_changes_per_round',
        2,
        'The maximum amount of times a players is allowed to change their team per round.'
    )

    cvar_team_changes_reset_delay = config.cvar(
        'team_changes_reset_delay',
        1.5,
        'Time penalty (in minutes) for exceeding the maximum team change count.'
    )

    config.text('----------------------------------')
    config.text('   * Say Commands')
    config.text('----------------------------------')

    cvar_saycommand_admin = config.cvar(
        'saycommand_admin',
        '!udm',
        'The say command used to open the admin menu.'
    )

    cvar_saycommand_guns = config.cvar(
        'saycommand_guns',
        'guns',
        'The say command used to open the weapons menu.'
    )
