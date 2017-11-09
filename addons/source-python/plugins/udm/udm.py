# ../udm/udm.py

"""Ultimate Deathmatch Plugin"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Colors
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
        attacker.active_weapon.clip = weapon_manager.by_name(attacker.active_weapon.weapon_name).clip

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
    # Refill the weapon's ammo
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
def on_bump_weapon(stack_data):
    """Block picking up the weapon if it's not in the player's inventory."""
    # Get a PlayerEntity instance for the player
    player = make_object(PlayerEntity, stack_data[0])

    # Block the weapon bump if the player is using the admin menu
    if player.userid in admin_menu.users and admin_menu.users[player.userid]:
        return False

    # Get a Weapon instance for the weapon
    weapon = make_object(Weapon, stack_data[1])

    # Get the weapon's data
    weapon_data = weapon_manager.by_name(weapon.weapon_name)

    # Block the weapon bump if the player didn't choose it
    if weapon_data is not None and player.inventory and weapon_data.basename not in\
            [item.basename for item in player.inventory.values()]:
        return False


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(cvar_saycommand_guns.get_string())
def on_saycommand_guns(command_info, *args):
    """Allow the player to edit & equip one of their inventories."""
    # Get a PlayerEntity instance for the player who entered the chat command
    player = PlayerEntity(command_info.index)

    # Get the selection for the inventory the player wants to equip or edit
    selection = int(args[0]) if args and args[0].isdigit() else None

    # If no selection was made, send the Primary Weapons menu
    if selection is None:
        primary_menu.send(player.index)

        # Tell the player
        player.tell('UDM', f'Editing inventory {WHITE}{player.inventory_selection + 1}')

        # Stop here and block the message from appearing in the chat window
        return False

    # Give random weapons if the selection is not valid
    if selection <= 0:
        player.equip_random_weapons()

        # Stop here and block the message from appearing in the chat window
        return False

    # Make the player's choice their inventory selection
    player.inventory_selection = selection - 1

    # Decide whether the player wants to edit or equip their inventory
    if player.inventory:

        # If the weapons owned and the weapons of the inventory are the same,
        # the player is allowed to edit their inventory
        # Otherwise they are going to be equipped with it
        weapons_owned = sorted([weapon.classname for weapon in player.weapons(not_filters=('melee', 'grenade'))])
        inventory_weapons = sorted([item.data.name for item in player.inventory.values()])

        edit = weapons_owned == inventory_weapons

    # The player is allowed to equip their inventory if no item is present in it
    else:
        edit = True

    # Send the Primary Weapons menu if the player is allowed to edit their inventory
    if edit:
        primary_menu.send(player.index)

        # Tell the player
        player.tell('UDM', f'Editing inventory {WHITE}{player.inventory_selection + 1}')

    # Else equip the selected inventory
    else:
        player.strip()
        player.equip_inventory()

        # Tell the player
        player.tell('UDM', f'Equipping inventory {WHITE}{player.inventory_selection + 1}')

    # Stop here and block the message from appearing in the chat window
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
    admin_menu.users[player.userid] = True
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False
