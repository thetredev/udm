# ../udm/udm.py

"""Main plugin module: adds Deathmatch gameplay."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Colors
from colors import ORANGE
from colors import WHITE
#   Commands
from commands.typed import TypedSayCommand
#   Events
from events import Event
#   Listeners
from listeners.tick import Delay
#   Messages
from messages import SayText2

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
#   Maps
from udm.maps import map_functions
#   Menus
from udm.weapons.menus import primary_menu
#   Players
from udm.players import PlayerEntity
from udm.players.inventories import PlayerInventory
from udm.players.inventories import player_inventories
#   Weapons
from udm.weapons import weapon_iter


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
    map_functions.disable()


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
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand_guns.get_string())
def on_saycommand_guns(command_info, *args):
    """Send the Primary Weapons menu to the player."""
    # Get a udm.players.PlayerEntity instance for the player who entered the say command
    player = PlayerEntity(command_info.index)

    # Store a variable to decide whether the player wants to edit their current inventory
    edit = False

    # Figure out the selection index
    if not args:
        index = player.inventory_selection

    # Do nothing if the first argument is not an integer
    elif not args[0].isdigit():
        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Inventory {WHITE}{player.inventory_selection} {ORANGE}unchanged.'
        ).send(command_info.index)

        return False

    # Calculate the selection index
    else:
        index = int(args[0]) - 1

    # If we get a negative value, print an error message
    if index < 0:
        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Inventory {WHITE}{index + 1} {ORANGE} not found.'
        ).send(command_info.index)

        return False

    # Fix `index` if it is too high
    if index > len(player.inventories):
        index = len(player.inventories)

    # Create an empty inventory at `index` if none is present
    if index not in player.inventories:
        player.inventories[index] = PlayerInventory(player.uniqueid)

    # The player wants to edit the current inventory, if the player is already equipped with it
    if player.userid in player_inventories.selections and player.inventory_selection == index:
        edit = True

    # Store the inventory selection
    player.inventory_selection = index

    # Get the inventory at `index`
    inventory = player.inventories[index]

    # Equip the player if they don't want to edit the inventory and if there are weapons present in it
    if not edit and inventory:
        player.strip(('melee', 'grenade'))
        player.equip(inventory_index=index)

        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Equipping inventory {WHITE}{index + 1}'
        ).send(command_info.index)

    # Else edit that inventory
    else:
        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Editing inventory {WHITE}{index + 1}'
        ).send(command_info.index)

        primary_menu.send(player.index)

    # Block the text from appearing in the chat window
    return False


@TypedSayCommand(cvar_saycommand_admin.get_string(), permission='udm.admin')
def on_saycommand_admin(command_info):
    """Send the Admin menu to the player."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(command_info.index)

    # Cancel the protect delay so we can ensure that the next call to `player.protect()` stays unaffected by it
    delay_manager.cancel_delays(f'protect_{player.userid}')

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
    map_functions.enable()
