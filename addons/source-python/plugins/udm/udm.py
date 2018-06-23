# ../udm/udm.py

"""Ultimate Deathmatch Plugin"""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Random
import random

# Source.Python Imports
#   Commands
from commands.client import ClientCommandFilter
from commands.typed import TypedSayCommand
#   Core
from core import OutputReturn
#   Cvars
from cvars import cvar
#   Entities
from entities.entity import Entity
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
#   Events
from events import Event
from events.hooks import PreEvent
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnEntityDeleted
from listeners import OnEntitySpawned
from listeners import OnLevelEnd
from listeners import OnServerActivate
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
from udm.config import cvar_enable_infinite_ammo
from udm.config import cvar_enable_noblock
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_refill_clip_on_headshot
from udm.config import cvar_respawn_delay
from udm.config import cvar_restore_health_on_knife_kill
from udm.config import cvar_saycommand_admin
from udm.config import cvar_saycommand_guns
from udm.config import cvar_spawn_protection_delay
from udm.config import cvar_team_changes_per_round
#   Cvars
from udm.cvars import ManipulatedIntConVar
from udm.cvars import manipulated_int_convars
#   Delays
from udm.delays import delay_manager
#   Entities
from udm.entities import EntityInputDispatcher
from udm.entities import EntityRemover
#   Info
from udm.info import info
#   Menus
from udm.weapons.menus import primary_menu
#   Players
from udm.players import player_random_weapons
from udm.players import player_spawn_locations
from udm.players import player_team_changes
from udm.players import PlayerEntity
#   Spawn Points
from udm.spawnpoints.menus import spawnpoints_manager_menu
#   Weapons
from udm.weapons import is_silencer_option_primary
from udm.weapons import is_silencer_option_secondary
from udm.weapons import weapon_manager


# =============================================================================
# >> REGISTER ADMIN MENU SUBMENUS
# =============================================================================
admin_menu.register_submenu(spawnpoints_manager_menu)


# =============================================================================
# >> REGISTER MANIPULATED INTEGER CONVARS
# =============================================================================
manipulated_int_convars.extend([
    ManipulatedIntConVar('mp_buytime', 60 * 60),
    ManipulatedIntConVar('mp_startmoney', 10_000),
    ManipulatedIntConVar('mp_buy_anywhere', 1),
    ManipulatedIntConVar('mp_solid_teammates', int(cvar_enable_noblock.get_int() == 0))
])

# =============================================================================
# >> RESTART GAME CONVAR
# =============================================================================
mp_restartgame = cvar.find_var('mp_restartgame')


# =============================================================================
# >> FORBIDDEN ENTITIES
# =============================================================================
# Store a list of forbidden entities
forbidden_entities = list(
    [weapon_data.name for weapon_data in WeaponClassIter(is_filters='objective')] +
    ['hostage_entity', 'item_defuser']
)

# =============================================================================
# >> MAP FUNCTIONS
# =============================================================================
# Store a list of map functions to disable when they have spawned
map_functions = [
    'func_bomb_target', 'func_buyzone', 'func_hostage_rescue'
]


# =============================================================================
# >> HELPER FUNCTIONS
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
    spawnpoint = player.get_spawn_location()

    # Move the player to the spawn point found
    spawnpoint.move_player(player)

    # Equip the current inventory if not currently using the admin menu
    if player.userid not in admin_menu.users:
        player.equip_inventory()


# =============================================================================
# >> PRE EVENTS
# =============================================================================
@PreEvent('round_start')
def on_pre_round_start(game_event):
    """Enable delays right before any players spawn."""
    delay_manager.delays_enabled = True


@PreEvent('round_freeze_end')
def on_pre_round_freeze_end(game_event):
    """Enable damage protection for all players."""
    delay_time = abs(cvar_spawn_protection_delay.get_float())

    for player in PlayerEntity.alive():
        player.enable_damage_protection(delay_time)


# =============================================================================
# >> EVENTS
# =============================================================================
@Event('player_spawn')
def on_player_spawn(game_event):
    """Prepare the player for battle if they are alive and on a team."""
    player = PlayerEntity.from_userid(game_event['userid'])

    if not player.dead and player.team > 1:
        prepare_player(player)


@Event('player_death')
def on_player_death(game_event):
    """Handle attacker rewards & respawn the victim."""
    # Get the attacker's userid
    userid_attacker = game_event['attacker']

    # Handle attacker rewards, if the attacker's userid is valid
    if userid_attacker:
        attacker = PlayerEntity.from_userid(userid_attacker)

        # Handle headshot reward
        if cvar_refill_clip_on_headshot.get_int() > 0 and game_event['headshot']:

            # Get the weapon's data
            weapon_data = weapon_manager.by_name(attacker.active_weapon.weapon_name)

            # Refill the weapon's clip
            attacker.refill_clip(weapon_data)

            # Restore the weapon's ammo
            attacker.active_weapon.ammo = weapon_data.maxammo

        # Give a High Explosive grenade, if it was a HE grenade kill
        if cvar_equip_hegrenade.get_int() == 2 and game_event['weapon'] == 'hegrenade':
            attacker.give_weapon('weapon_hegrenade')

        # Restore the attacker's health if it was a knife kill
        if cvar_restore_health_on_knife_kill.get_int() > 0 and game_event['weapon'].startswith('knife'):
            attacker.health = 100

    # Get a PlayerEntity instance for the victim
    victim = PlayerEntity.from_userid(game_event['userid'])

    # Respawn the victim after the configured respawn delay
    delay_manager(
        f'respawn_{victim.userid}', abs(cvar_respawn_delay.get_float()), PlayerEntity.respawn, (victim.index, )
    )


@Event('player_disconnect')
def on_player_disconnect(game_event):
    """Cancel all pending delays for the disconnecting player."""
    player = PlayerEntity.from_userid(game_event['userid'])

    delay_manager.cancel(f'respawn_{player.userid}')
    delay_manager.cancel(f'protect_{player.userid}')


@Event('round_end')
def on_round_end(game_event):
    """Cancel all pending delays and team change counts."""
    delay_manager.clear()
    player_team_changes.clear()


@Event('hegrenade_detonate')
def on_hegrenade_detonate(game_event):
    """Equip the player with another High Explosive grenade if configured that way."""
    if cvar_equip_hegrenade.get_int() == 3:
        player = PlayerEntity.from_userid(game_event['userid'])
        player.give_weapon('weapon_hegrenade')


@Event('weapon_reload')
def on_weapon_reload(game_event):
    """Refill the player's ammo."""
    if cvar_enable_infinite_ammo.get_int() > 0:
        player = PlayerEntity.from_userid(game_event['userid'])
        player.refill_ammo()


@Event('weapon_fire')
def on_weapon_fire_on_empty(game_event):
    """Refill the player's ammo, if the player's active weapon's clip is about to be empty."""
    if cvar_enable_infinite_ammo.get_int() > 0:
        player = PlayerEntity.from_userid(game_event['userid'])

        # Refill only valid weapons
        if weapon_manager.by_name(player.active_weapon.weapon_name) is not None:

            # Refill only if this is the last round
            if player.active_weapon.clip == 1:
                player.refill_ammo(1)


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

    # Get a Weapon instance for the weapon
    weapon = make_object(Weapon, stack_data[1])

    # Get the weapon's data
    weapon_data = weapon_manager.by_name(weapon.weapon_name)

    # Only block bumping for valid weapons
    if weapon_data is not None and weapon_data.has_silencer:

        if player.random_mode:
            weapon_manager.set_silencer(weapon, random.randint(0, 1))

        # If the player is not in random mode,
        else:

            if weapon_data.tag not in player.inventory:
                return False

            inventory_item = player.inventory[weapon_data.tag]

            if inventory_item.data.name not in (weapon.weapon_name, weapon.classname):
                return False

            # Handle the inventory item's silencer option
            if weapon_data.has_silencer and weapon.get_property_bool('m_bSilencerOn') != inventory_item.silencer_option:
                weapon_manager.set_silencer(weapon, inventory_item.silencer_option)


@EntityPreHook(EntityCondition.is_human_player, 'drop_weapon')
@EntityPreHook(EntityCondition.is_bot_player, 'drop_weapon')
def on_pre_drop_weapon(stack_data):
    """Remove the dropped weapon after one second."""
    # Get the weapon dropped
    weapon_ptr = stack_data[1]

    # Continue only for valid weapons
    if weapon_ptr:

        # Get a Weapon instance for the dropped weapon
        weapon = make_object(Weapon, weapon_ptr)

        # Remove it after one second
        delay_manager(
            f'drop_{weapon.index}', 1, weapon_manager.remove_weapon, (weapon.index, )
        )


@EntityPreHook(is_silencer_option_primary, 'secondary_attack')
@EntityPreHook(is_silencer_option_secondary, 'secondary_attack')
def on_pre_secondary_fire(stack_data):
    """Store the silencer option when the player attaches or detaches the silencer."""
    # Get a Weapon instance for the weapon
    weapon = make_object(Weapon, stack_data[0])

    # Make sure the weapon's owner is valid
    if weapon.owner is not None and weapon.owner.is_player():

        # Get the weapon's data
        weapon_data = weapon_manager.by_name(weapon.weapon_name)

        # Store the silencer option if the weapon can be silenced
        if weapon_data is not None and weapon_data.has_silencer:

            # Get a PlayerEntity instance for the player
            player = PlayerEntity(weapon.owner.index)

            # Set the silencer option for the player's inventory item
            for inventory_item in player.inventory.values():
                if inventory_item.data.name == weapon.weapon_name:
                    inventory_item.silencer_option = not weapon.get_property_bool('m_bSilencerOn')
                    break


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def on_entity_deleted(base_entity):
    """Cancel the refill & drop delays for the deleted entity."""
    if base_entity.classname.startswith(weapon_manager.prefix):
        delay_manager.cancel(f'drop_{base_entity.index}')
        delay_manager.cancel(f'refill_clip_{base_entity.index}')


@OnEntitySpawned
def on_entity_spawned(base_entity):
    """Remove forbidden entities when they have spawned."""
    if base_entity.classname in forbidden_entities:
        base_entity.remove()

    # Disable map functions as well
    elif base_entity.classname in map_functions:
        entity = Entity(base_entity.index)
        entity.call_input('Disable')


@OnLevelEnd
def on_level_end():
    """Clear personal player dictionaries."""
    player_random_weapons.clear()
    player_spawn_locations.clear()
    player_team_changes.clear()

    # Cancel all delays
    delay_manager.clear()


@OnServerActivate
def on_server_activate(edicts, edict_count, max_clients):
    """Set plugin values for defaultable integer convars."""
    manipulated_int_convars.manipulate_values()


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
    """Handle buy anywhere & spwaning in the middle of the round."""
    # Get a PlayerEntity instance for the player
    player = PlayerEntity(index)

    # Get the client command
    client_command = command[0]

    # Handle client command `buy`
    if client_command == 'buy':
        player.choose_weapon(command[1])

        # Block any further command handling
        return False

    # Handle the client command `drop`
    if client_command == 'drop':
        player.weapon_dropped()

        # Block any further command handling
        return False

    # Allow any client command besides `jointeam`
    if client_command != 'jointeam':
        return True

    # Get the team the player wants to join
    team_index = int(command[1])

    # Allow spectators
    if team_index < 2:
        return True

    # Allow the team change, if the player hasn't yet exceeded the maximum team change count
    if player.team_changes < cvar_team_changes_per_round.get_int() + 1:
        player.team_changed(team_index)

        # Allow the client command
        return True

    # Block any further command handling
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
    selection = args[0] if args else None

    # If no selection was made, send the Primary Weapons menu
    if selection is None:
        primary_menu.send(player.index)

        # Tell the player
        player.tell(info.verbose_name, f'Editing inventory {MESSAGE_COLOR_WHITE}{player.inventory_selection + 1}')

        # Stop here and block the message from appearing in the chat window
        return False

    # Ignore invalid input when evaluating the inventory selection
    try:
        selection = int(selection)
    except ValueError:
        return False

    # Stop if the selection isn't valid
    if selection <= 0:
        return False

    # Make the player's choice their inventory selection
    player.inventory_selection = selection - 1

    # Send the Primary Weapons menu if the player is allowed to edit their inventory
    if player.carries_inventory:
        primary_menu.send(player.index)

        # Tell the player
        player.tell(info.verbose_name, f'Editing inventory {MESSAGE_COLOR_WHITE}{player.inventory_selection + 1}')

    # Else equip the selected inventory
    else:
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

    # Protect the player indefinitely
    player.enable_damage_protection()

    # Strip the player off their weapons
    player.strip(not_filters=None)

    # Send the Admin menu to the player
    admin_menu.users.append(player.userid)
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False


# =============================================================================
# >> LOAD & UNLOAD
# =============================================================================
def load():
    """Prepare deathmatch gameplay."""
    # Manipulate convar values
    manipulated_int_convars.manipulate_values()

    # Remove forbidden entities
    EntityRemover.perform_action(forbidden_entities)

    # Disable map functions
    EntityInputDispatcher.perform_action(map_functions, 'Disable')

    # Restart the game after 3 seconds
    mp_restartgame.set_int(3)


def unload():
    """Reset deathmatch gameplay."""
    # Enable map functions
    EntityInputDispatcher.perform_action(map_functions, 'Enable')

    # Clear the list of player personal random weapons
    player_random_weapons.clear()

    # Clear the list of player personal spawn points
    player_spawn_locations.clear()

    # Clear player team change counts
    player_team_changes.clear()

    # Restart the game after 1 second
    mp_restartgame.set_int(1)
