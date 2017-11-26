# ../udm/udm.py

"""Ultimate Deathmatch Plugin"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib

# Source.Python Imports
#   Commands
from commands.client import ClientCommandFilter
from commands.typed import TypedSayCommand
#   Core
from core import OutputReturn
#   Entities
from entities.entity import Entity
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
from entities.hooks import EntityPostHook
#   Events
from events import Event
from events.hooks import PreEvent
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnEntitySpawned
from listeners import OnPlayerRunCommand
from listeners import OnServerOutput
#   Memory
from memory import make_object
#   Weapons
from weapons.entity import Weapon

# Script Imports
#   Admin
from udm.admin import admin_menu
#   Colors
from udm.colors import MESSAGE_COLOR_WHITE
#   Config
from udm.config import cvar_enable_noblock
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_refill_clip_on_headshot
from udm.config import cvar_respawn_delay
from udm.config import cvar_restore_health_on_knife_kill
from udm.config import cvar_saycommand_admin
from udm.config import cvar_saycommand_guns
from udm.config import cvar_spawn_protection_delay
from udm.config import cvar_team_changes_per_round
#   Delays
from udm.delays import delay_manager
#   Info
from udm.info import info
#   Menus
from udm.weapons.menus import primary_menu
#   Players
from udm.players import team_changes
from udm.players import PlayerEntity
#   Spawn Points
from udm.spawnpoints import spawnpoints
from udm.spawnpoints.menus import spawnpoints_manager_menu
#   Weapons
from udm.weapons import remove_weapon
from udm.weapons import weapon_manager


# =============================================================================
# >> REGISTER ADMIN MENU SUBMENUS
# =============================================================================
admin_menu.register_submenu(spawnpoints_manager_menu)


# =============================================================================
# >> FORBIDDEN ENTITIES
# =============================================================================
# Store a list of forbidden entities
forbidden_entities = [weapon_class.name for weapon_class in WeaponClassIter(is_filters='objective')] + [
    'hostage_entity', 'item_defuser'
]


# =============================================================================
# >> MAP FUNCTIONS
# =============================================================================
# Store a list of map functions to disable when they have spawned
map_functions = [
    'func_bomb_target', 'func_buyzone', 'func_hostage_rescue'
]


# =============================================================================
# >> PLAYER PREPARATION
# =============================================================================
def prepare_player(player):
    """Prepare the player for battle."""
    # Give armor
    player.give_named_item('item_assaultsuit')

    # Give a High Explosive grenade if configured that way
    if cvar_equip_hegrenade.get_int() > 0:
        player.give_weapon('weapon_hegrenade')

    # Enable or disable non-blocking mode, depending on the configuration
    player.noblock = cvar_enable_noblock.get_int() > 0

    # Enable damage protection
    player.enable_damage_protection(
        None if player.userid in admin_menu.users
        else cvar_spawn_protection_delay.get_float()
    )

    # Choose a random spawn point
    spawnpoint = spawnpoints.get_random()

    # Spawn the player on the location found
    if spawnpoint is not None:
        player.origin = spawnpoint
        player.view_angle = spawnpoint.angle

    # Equip the current inventory if not currently using the admin menu
    if player.userid not in admin_menu.users:
        player.equip_inventory()


# =============================================================================
# >> PRE EVENTS
# =============================================================================
@PreEvent('round_start')
def on_pre_round_start(event):
    """Enable delays right before any players spawn."""
    delay_manager.delays_enabled = True


@PreEvent('round_freeze_end')
def on_pre_round_freeze_end(event):
    """Enable damage protection for all players."""
    delay_time = abs(cvar_spawn_protection_delay.get_float())

    for player in PlayerEntity.alive():
        player.enable_damage_protection(delay_time)


# =============================================================================
# >> EVENTS
# =============================================================================
@Event('player_spawn')
def on_player_spawn(event):
    """Prepare the player for battle if they are alive and on a team."""
    player = PlayerEntity.from_userid(event.get_int('userid'))

    if player.team > 1 and not player.dead:
        prepare_player(player)


@Event('player_death')
def on_player_death(event):
    """Refill the attacker's active weapon's clip for a headshot & respawn the victim."""
    # Get a PlayerEntity instance for the attacker
    attacker = PlayerEntity.from_userid(event.get_int('attacker'))

    # Refill the attacker's active weapon's clip for a headshot
    if cvar_refill_clip_on_headshot.get_int() > 0 and event.get_bool('headshot'):
        delay_manager(
            f'refill_clip_{attacker.active_weapon.index}', 0.1,
            attacker.active_weapon.set_clip, (weapon_manager.by_name(attacker.active_weapon.weapon_name).clip, )
        )

    # Give a High Explosive grenade, if it was a HE grenade kill
    if cvar_equip_hegrenade.get_int() == 2 and event.get_string('weapon') == 'hegrenade':
        attacker.give_weapon('weapon_hegrenade')

    # Restore the attacker's health if it was a knife kill
    if cvar_restore_health_on_knife_kill.get_int() > 0 and event.get_string('weapon').startswith('knife'):
        attacker.health = 100

    # Get a PlayerEntity instance for the victim
    victim = PlayerEntity.from_userid(event.get_int('userid'))

    # Respawn the victim after the configured respawn delay
    delay_manager(f'respawn_{victim.userid}', abs(cvar_respawn_delay.get_float()), victim.spawn)


@Event('player_disconnect')
def on_player_disconnect(event):
    """Cancel all pending delays for the disconnecting player."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity.from_userid(event.get_int('userid'))

    # Cancel the player's delays
    delay_manager.cancel(f'respawn_{player.userid}')
    delay_manager.cancel(f'protect_{player.userid}')


@Event('round_end')
def on_round_end(event):
    """Cancel all pending delays and team change counts."""
    delay_manager.clear()
    team_changes.clear()


@Event('weapon_reload')
def on_weapon_reload(event):
    """Refill the player's active weapon's ammo after the reload animation has finished."""
    player = PlayerEntity.from_userid(event.get_int('userid'))
    player.refill_ammo()


@Event('hegrenade_detonate')
def on_hegrenade_detonate(event):
    """Equip the player with another High Explosive grenade if configured that way."""
    if cvar_equip_hegrenade.get_int() == 3:
        player = PlayerEntity.from_userid(event.get_int('userid'))
        player.give_weapon('weapon_hegrenade')


# =============================================================================
# >> ENTITY HOOKS
# =============================================================================
@EntityPreHook(EntityCondition.is_human_player, 'bump_weapon')
@EntityPreHook(EntityCondition.is_bot_player, 'bump_weapon')
def on_pre_bump_weapon(stack_data):
    """Block bumping into the weapon if it's not in the player's inventory."""
    # Get a PlayerEntity instance for the player
    player = make_object(PlayerEntity, stack_data[0])

    # Block the weapon bump if the player is using the admin menu
    if player.userid in admin_menu.users:
        return False

    # Only block bumping if the weapon is not in random mode
    if not player.random_mode:

        # Get a Weapon instance for the weapon
        weapon = make_object(Weapon, stack_data[1])

        # Get the weapon's data
        weapon_data = weapon_manager.by_name(weapon.weapon_name)

        # Block the weapon bump if the weapon is not listed in the player's inventory
        if weapon_data is not None:
            if weapon_data.tag not in player.inventory:
                return False

            weapon_selected = player.inventory[weapon_data.tag].data.name

            if weapon_selected not in (weapon.weapon_name, weapon.classname):
                return False


@EntityPostHook(EntityCondition.is_human_player, 'drop_weapon')
@EntityPostHook(EntityCondition.is_bot_player, 'drop_weapon')
def on_post_drop_weapon(stack_data, nothing):
    """Remove the dropped weapon after half the respawn delay."""
    # Get a PlayerEntity instance for the player
    player = make_object(PlayerEntity, stack_data[0])

    # Remove the dropped weapon after the delay if this was a valid drop_weapon() call
    if player.classname == 'player':
        weapon = make_object(Weapon, stack_data[1])
        delay_manager(f'drop_{weapon.index}', abs(cvar_respawn_delay.get_float()) / 2, remove_weapon, (weapon, ))


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntitySpawned
def on_entity_spawned(base_entity):
    """Remove forbidden entities when they have spawned."""
    if base_entity.classname in forbidden_entities:
        base_entity.remove()

    # Disable map functions as well
    elif base_entity.classname in map_functions:
        entity = Entity(base_entity.index)
        entity.call_input('Disable')


@OnPlayerRunCommand
def on_player_run_command(player, cmd):
    """Refill the player's active weapon's ammo as soon as the player stops shooting a weapon with an empty clip."""
    with contextlib.suppress(ValueError):
        if player.active_weapon is not None and player.active_weapon.clip == 0:
            PlayerEntity(player.index).refill_ammo()


@OnServerOutput
def on_server_output(severity, msg):
    """Block the warning that any bot has spawned outside of a buy zone."""
    if 'bot spawned outside of a buy zone' in msg:
        return OutputReturn.BLOCK

    return OutputReturn.CONTINUE


# =============================================================================
# >> CLIENT COMMAND FILTER
# =============================================================================
@ClientCommandFilter
def client_command_filter(command, index):
    """Spawn the player if the round has already started."""
    # Allow the client command if it is not `jointeam`
    if command[0] != 'jointeam':
        return True

    # Get a PlayerEntity instance for the player
    player = PlayerEntity(index)

    # Get the team the player wants to join
    team_index = int(command[1])

    # Allow spectators
    if team_index < 2:
        return True

    # Allow the team change, if the player hasn't yet exceeded the maximum team change count
    if player.team_changes < cvar_team_changes_per_round.get_int() + 1:
        player.team = team_index

        # Take a note of the team change
        player.team_changes += 1

        # Respawn the player after the respawn delay
        delay_manager(f'respawn_{player.userid}', abs(cvar_respawn_delay.get_float()), player.spawn)

        # Allow the client command
        return True

    # Block the client command, if the player has exceeded the maximum team change count
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
        player.random_mode = False
        primary_menu.send(player.index)

        # Tell the player
        player.tell(info.verbose_name, f'Editing inventory {MESSAGE_COLOR_WHITE}{player.inventory_selection + 1}')

        # Stop here and block the message from appearing in the chat window
        return False

    # Give random weapons if the selection is not valid
    if selection <= 0:
        player.equip_random_weapons()

        # Stop here and block the message from appearing in the chat window
        return False

    # Disable random mode
    player.random_mode = False

    # Make the player's choice their inventory selection
    player.inventory_selection = selection - 1

    # Send the Primary Weapons menu if the player is allowed to edit their inventory
    if player.carries_inventory:
        primary_menu.send(player.index)

        # Tell the player
        player.tell(info.verbose_name, f'Editing inventory {MESSAGE_COLOR_WHITE}{player.inventory_selection + 1}')

    # Else equip the selected inventory
    else:
        player.strip()
        player.equip_inventory()

        # Tell the player
        player.tell(info.verbose_name, f'Equipping inventory {MESSAGE_COLOR_WHITE}{player.inventory_selection + 1}')

    # Block the message from appearing in the chat window
    return False


@TypedSayCommand(cvar_saycommand_admin.get_string(), permission=f'{info.name}.admin')
def on_saycommand_admin(command_info):
    """Send the Admin menu to the player."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(command_info.index)

    # Cancel the damage protect delay so we can ensure that the next call to `player.protect()` is unaffected by it
    delay_manager.cancel(f'protect_{player.userid}')

    # Protect the player indefinitely
    player.enable_damage_protection()

    # Strip the player off their weapons
    player.strip(not_filters=None)

    # Send the Admin menu to the player
    admin_menu.users.append(player.userid)
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False
