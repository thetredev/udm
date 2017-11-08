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
#   Entities
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
#   Events
from events import Event
#   Listeners
from listeners.tick import Delay
#   Memory
from memory import make_object
#   Weapons
from weapons.entity import Weapon

# Script Imports
#   Admin
from udm.admin import admin_menu
#   Config
from udm.config import cvar_equip_delay
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_respawn_delay
from udm.config import cvar_saycommand_admin
from udm.config import cvar_saycommand_guns
from udm.config.menus import config_manager_menu
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
#   Spawn Points
from udm.spawnpoints.menus import spawnpoints_manager_menu
#   Weapons
from udm.weapons import weapon_manager
from udm.weapons import weapon_iter


# =============================================================================
# >> REGISTER ADMIN MENU SUBMENUS
# =============================================================================
admin_menu.register_submenu(config_manager_menu)
admin_menu.register_submenu(spawnpoints_manager_menu)


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
    """Refill the attacker's active weapon's clip for a headshot & respawn the victim."""
    # Get a PlayerEntity instance for the attacker
    attacker = PlayerEntity.from_userid(event.get_int('attacker'))

    # Refill the attacker's active weapon's clip for a headshot
    if event.get_bool('headshot'):
        attacker.active_weapon.clip = weapon_manager.by_name(attacker.active_weapon.classname).clip

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
    weapon_data = weapon_manager[event.get_string('weapon')]

    if weapon_data.tag not in ('melee', 'grenade'):
        PlayerEntity.from_userid(event.get_int('userid')).refill_ammo()


@Event('hegrenade_detonate')
def on_hegrenade_detonate(event):
    """Equip the player with another High Explosive grenade if configured that way."""
    if cvar_equip_hegrenade.get_int() == 2:
        PlayerEntity.from_userid(event.get_int('userid')).give_named_item('weapon_hegrenade')


# =============================================================================
# >> ENTITY HOOKS
# =============================================================================
@EntityPreHook(EntityCondition.is_player, 'bump_weapon')
def on_item_pickup(stack_data):
    """Block picking up the weapon if it's not in the player's inventory."""
    # Get a Weapon instance for the weapon
    weapon = make_object(Weapon, stack_data[1])

    # Get the weapon's data
    weapon_data = weapon_manager.by_name(weapon.classname)

    # Make sure we are not dealing with any melee or grenade weapons
    if weapon_data is not None and weapon_data.tag not in ('melee', 'grenade'):

        # Get a PlayerEntity instance for the player
        player = make_object(PlayerEntity, stack_data[0])

        # Block the weapon bump if the player didn't choose it
        if player.inventory and weapon_data.basename not in [item.basename for item in player.inventory.values()]:
            return False


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
        player.tell('UDM', f'Inventory {WHITE}{player.inventory_selection} {ORANGE}unchanged.')
        return False

    # Calculate the selection index
    else:
        inventory_index = int(args[0]) - 1

    # Equip the player with random weapons if `inventory_index` is lower than 0 (`zero`)
    if inventory_index < 0:
        player.strip()
        player.equip_random_weapons()

        return False

    # Fix `inventory_index` if it is too high
    if inventory_index > len(player.inventories):
        inventory_index = len(player.inventories)

    # Create an empty inventory at `inventory_index` if none is present
    if inventory_index not in player.inventories:
        player.inventories[inventory_index] = PlayerInventory()

    # The player wants to edit the current inventory, if the player is already equipped with it
    if player.userid in player_inventories.selections and player.inventory_selection == inventory_index:

        # Make sure that the player currently owns the inventory's items
        weapons_owned = sorted([weapon.classname for weapon in player.weapons(not_filters=('melee', 'grenade'))])
        inventory_items = sorted([item.data.name for item in player.inventory.values()])

        edit = weapons_owned == inventory_items

    # Set the inventory at `inventory_index` as the player's current inventory selection
    player.inventory_selection = inventory_index

    # Equip the player if they don't want to edit the inventory and if there are weapons present in the inventory
    if not edit and player.inventory:
        player.strip()
        player.equip_inventory()

        # Tell the player
        player.tell('UDM', f'Equipping inventory {WHITE}{inventory_index + 1}')

    # Otherwise edit the player's current inventory
    else:
        primary_menu.send(player.index)

        # Tell the player
        player.tell('UDM', f'Editing inventory {WHITE}{inventory_index + 1}')

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
    player.strip(not_filters=None)

    # Send the Admin menu to the player
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False
