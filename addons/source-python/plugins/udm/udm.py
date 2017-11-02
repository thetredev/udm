# ../udm/udm.py

"""Main plugin module: adds Deathmatch gameplay."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Commands
from commands.typed import TypedSayCommand
#   Events
from events import Event
#   Filters
from filters.entities import EntityIter
#   Listeners
from listeners.tick import Delay

# Script Imports
#   Config
from udm.config import cvar_equip_delay
from udm.config import cvar_respawn_delay
from udm.config import cvar_saycommand
#   Menus
from udm.menus import primary_menu
#   Players
from udm.players import PlayerEntity
#   Weapons
from udm.weapons import weapon_iter


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a tuple of map functions, so we can remove them on round start
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

    # Get the delay value configured in the cvar 'udm_respawn_delay'
    delay = abs(cvar_respawn_delay.get_float())

    # Remove all idle weapons after half the delay
    Delay(delay / 2.0, weapon_iter.remove_idle)

    # Safely respawn the victim after the delay
    Delay(delay, victim.spawn)


@Event('round_start')
def on_round_start(event):
    """Remove all specified map functions from the map."""
    for map_function in map_functions:
        for entity in map_function:
            entity.remove()


@Event('weapon_reload')
def on_weapon_reload(event):
    PlayerEntity.from_userid(event.get_int('userid')).refill_ammo()


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand.get_string())
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
