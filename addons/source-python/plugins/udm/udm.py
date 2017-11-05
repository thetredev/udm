# ../udm/udm.py

"""Main plugin module: adds Deathmatch gameplay."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib

# Source.Python Imports
#   Commands
from commands.typed import TypedSayCommand
#   Events
from events import Event
#   Filters
from filters.entities import EntityIter
#   Listeners
from listeners import OnClientDisconnect
from listeners import OnLevelEnd
from listeners import OnLevelInit
from listeners.tick import Delay
#   Players
from players.helpers import userid_from_index

# Script Imports
#   Admin
from udm.admin import admin_menu
#   Config
from udm.config import cvar_equip_delay
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_respawn_delay
from udm.config import cvar_saycommand_admin
from udm.config import cvar_saycommand_guns
#   Delays
from udm.delays import delay_manager
#   Menus
from udm.weapons.menus import primary_menu
#   Players
from udm.players import PlayerEntity
#   Spawn Points
from udm.spawnpoints import spawnpoints
from udm.spawnpoints import SpawnPoint
#   Weapons
from udm.weapons import weapon_iter


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a tuple of map functions, so we can disable them on round start
map_functions = (
    EntityIter('func_buyzone'),
    EntityIter('func_bomb_target'),
    EntityIter('func_hostage_rescue')
)


# =============================================================================
# >> EVENTS
# =============================================================================
@Event('player_spawn')
def on_player_spawn(event):
    """Prepare the player for battle if the player is alive and on a team."""
    # Get a udm.players.PlayerEntity instance for the player's userid
    player = PlayerEntity.from_userid(event.get_int('userid'))

    # Prepare the player if they're alive and on a team
    if player.team > 1 and not player.dead:
        Delay(abs(cvar_equip_delay.get_float()), player.prepare)


@Event('player_death')
def on_player_death(event):
    """Remove all weapons the player owns and respawn the player."""
    # Get a udm.players.PlayerEntity instance for the victim's userid
    victim = PlayerEntity.from_userid(event.get_int('userid'))

    # Add the victim's location as a spawn point
    # Note: This is for testing purposes only...
    spawnpoints.append(SpawnPoint(victim.origin.x, victim.origin.y, victim.origin.z, victim.view_angle))

    # Get the time delay value configured in the cvar 'respawn_delay'
    time_delay = abs(cvar_respawn_delay.get_float())

    # Get the delay list from the delay manager
    delay_list = delay_manager[f'respawn_{victim.userid}']

    # Remove all idle weapons after half the delay
    delay_list.append(Delay(time_delay / 2.0, weapon_iter.remove_idle))

    # Safely respawn the victim after the delay
    delay_list.append(Delay(time_delay, victim.spawn))


@Event('round_start')
def on_round_start(event):
    """Disable all specified map functions."""
    for map_function in map_functions:
        for entity in map_function:
            entity.call_input('Disable')


@Event('round_end')
def on_round_end(event):
    """Cancel all pending delays."""
    delay_manager.cancel_all()


@Event('weapon_reload')
def on_weapon_reload(event):
    """Refill the player's ammo after the reload animation has finished."""
    PlayerEntity.from_userid(event.get_int('userid')).refill_ammo()


@Event('hegrenade_detonate')
def on_hegrenade_detonate(event):
    """Equip the player with another High Explosive grenade if configured that way."""
    if cvar_equip_hegrenade.get_int() == 2:
        PlayerEntity.from_userid(event.get_int('userid')).give_named_item('hegrenade')


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnClientDisconnect
def on_client_disconnect(index):
    """Cancel all pending delays of the client."""
    # Note: This is done, because the event 'player_disconnect' somehow does not get fired...
    with contextlib.suppress(ValueError):

        # Get the userid of the client
        userid = userid_from_index(index)

        # Cancel the client's pending delays
        delay_manager.cancel_delays(f"respawn_{userid}")
        delay_manager.cancel_delays(f"protect_{userid}")


@OnLevelEnd
def on_level_end():
    """Cancel all pending delays."""
    delay_manager.cancel_all()


@OnLevelInit
def on_level_init(map_name):
    """Reload spawn points."""
    spawnpoints.clear()
    spawnpoints.load()


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand_guns.get_string())
def on_saycommand_guns(command_info):
    """Send the Primary Weapons menu to the player."""
    # Get a udm.players.PlayerEntity instance for the player who entered the say command
    player = PlayerEntity(command_info.index)

    # Clear their inventory
    player.inventory.clear()

    # Send the Primary Weapons menu to them
    primary_menu.send(player.index)

    # Block the text from appearing in the chat window
    return False


@TypedSayCommand(cvar_saycommand_admin.get_string(), permission='udm.admin')
def on_saycommand_admin(command_info):
    """Send the Admin menu to the player."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(command_info.index)

    # Protect the player for an unknown amount of time
    player.protect()

    # Strip the player off their weapons
    player.strip()

    # Send the Admin menu to the player
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False


# =============================================================================
# >> UNLOAD
# =============================================================================
def unload():
    """Clean up."""
    # Cancel all pending delays
    delay_manager.cancel_all()

    # Enable all specified map functions
    for map_function in map_functions:
        for entity in map_function:
            entity.call_input('Enable')
