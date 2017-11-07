# ../udm/udm.py

"""Ultimate Deathmatch Plugin"""

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
    # Get a PlayerEntity instance for the player
    player = PlayerEntity.from_userid(event.get_int('userid'))

    # Prepare the player if they're alive and on a team
    if player.team > 1 and not player.dead:
        Delay(abs(cvar_equip_delay.get_float()), player.prepare)


@Event('player_death')
def on_player_death(event):
    """Respawn the victim."""
    # Get a PlayerEntity instance for the victim
    victim = PlayerEntity.from_userid(event.get_int('userid'))

    # Get the respawn time delay
    time_delay = abs(cvar_respawn_delay.get_float())

    # Get the delay list for `respawn_<victim.userid>`
    delay_list = delay_manager[f'respawn_{victim.userid}']

    # Remove all idle weapons after `time_delay / 2`
    delay_list.append(Delay(time_delay / 2, weapon_iter.remove_idle))

    # Respawn the victim after `time_delay`
    delay_list.append(Delay(time_delay, victim.spawn))


@Event('round_start')
def on_round_start(event):
    """Disable map function entities."""
    map_functions.disable()


@Event('round_end')
def on_round_end(event):
    """Cancel all pending delays."""
    delay_manager.cancel_all()


@Event('weapon_reload')
def on_weapon_reload(event):
    """Refill the player's active weapon's ammo after the reload animation has finished."""
    PlayerEntity.from_userid(event.get_int('userid')).refill_ammo()


@Event('hegrenade_detonate')
def on_hegrenade_detonate(event):
    """Equip the player with another High Explosive grenade if configured that way."""
    if cvar_equip_hegrenade.get_int() == 2:
        PlayerEntity.from_userid(event.get_int('userid')).give_named_item('weapon_hegrenade')


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand_guns.get_string())
def on_saycommand_guns(command_info, *args):
    """Allow the player to edit & equip one of their inventories."""
    # Get a PlayerEntity instance for the player who entered the chat command
    player = PlayerEntity(command_info.index)

    # Store a variable to decide whether the player wants to edit their current inventory
    edit = False

    # Figure out the selection index
    if not args:
        inventory_index = player.inventory_selection

    # Skip if the first argument is not an integer
    elif not args[0].isdigit():
        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Inventory {WHITE}{player.inventory_selection} {ORANGE}unchanged.'
        ).send(command_info.index)

        return False

    # Calculate the selection index
    else:
        inventory_index = int(args[0]) - 1

    # Equip the player with random weapons if `inventory_index` is lower than 0 (`zero`)
    if inventory_index < 0:
        player.strip(('melee', 'grenade'))
        player.equip_random_weapons()

        return False

    # Fix `inventory_index` if it is too high
    if inventory_index > len(player.inventories):
        inventory_index = len(player.inventories)

    # Create an empty inventory at `inventory_index` if none is present
    if inventory_index not in player.inventories:
        player.inventories[inventory_index] = PlayerInventory(player.uniqueid)

    # The player wants to edit the current inventory, if the player is already equipped with it
    if player.userid in player_inventories.selections and player.inventory_selection == inventory_index:

        # Make sure that the player currently owns the inventory's items
        weapons_owned = sorted([weapon.classname for weapon in player.weapons(not_filters=('melee', 'grenade'))])
        inventory_items = sorted([item.data.name for item in player.inventories[inventory_index].values()])

        edit = weapons_owned == inventory_items

    # Set the inventory at `inventory_index` as the player's current inventory selection
    player.inventory_selection = inventory_index

    # Get the inventory at `inventory_index`
    inventory = player.inventories[inventory_index]

    # Equip the player if they don't want to edit the inventory and if there are weapons present in the inventory
    if not edit and inventory:
        player.equip_inventory(inventory_index=inventory_index)

        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Equipping inventory {WHITE}{inventory_index + 1}'
        ).send(command_info.index)

    # Otherwise edit the player's current inventory
    else:
        SayText2(
            f'{ORANGE}[{WHITE}UDM{ORANGE}] Editing inventory {WHITE}{inventory_index + 1}'
        ).send(command_info.index)

        primary_menu.send(player.index)

    # Block the text from appearing in the chat window
    return False


@TypedSayCommand(cvar_saycommand_admin.get_string(), permission='udm.admin')
def on_saycommand_admin(command_info):
    """Send the Admin menu to the player."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(command_info.index)

    # Cancel the damage protect delay so we can ensure that the next call to `player.protect()` is unaffected by it
    delay_manager.cancel_delays(f'protect_{player.userid}')

    # Protect the player indefinitely
    player.enable_damage_protection()

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
