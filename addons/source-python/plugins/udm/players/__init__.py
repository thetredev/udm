# ../udm/players/__init__.py

"""Provides an interface between a player entity and their inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Contextlib
import contextlib
#   Datetime
import datetime
#   Random
import random

# Source.Python Imports
#   Colors
from colors import Color
from colors import WHITE
#   Filters
from filters.players import PlayerIter
#   Memory
from memory import make_object
#   Messages
from messages import SayText2
#   Players
from players.entity import Player
#   Weapons
from weapons.entity import Weapon

# Script Imports
#   Colors
from udm.colors import MESSAGE_COLOR_ORANGE
from udm.colors import MESSAGE_COLOR_WHITE
#   Config
from udm.config import cvar_team_changes_per_round
from udm.config import cvar_team_changes_reset_delay
from udm.config import cvar_respawn_delay
#   Delays
from udm.delays import delay_manager
#   Info
from udm.info import info
#   Players
from udm.players.inventories import player_inventories
#   Spawn Points
from udm.spawnpoints import SAFE_SPAWN_DISTANCE
from udm.spawnpoints import spawnpoint_manager
from udm.spawnpoints import SpawnPoint
#   Weapons
from udm.weapons import weapon_manager


# =============================================================================
# >> TEAM CHANGES
# =============================================================================
# Store team changes count for each player
player_team_changes = defaultdict(int)

# Store personal player spawn points
player_spawn_locations = defaultdict(list)

# Store personal player random weapons
player_random_weapons = defaultdict(lambda: {tag: list() for tag in weapon_manager.tags})


# =============================================================================
# >> PLAYER ENTITY
# =============================================================================
class PlayerEntity(Player):
    """Class used to provide the following functionality:

        * Respawn
        * Damage Protection
        * Access personal inventories
        * Access personal random weapons
        * Access personal spawn points
        * Refill weapon ammo
        * Refill weapon clip
    """

    @classmethod
    def alive(cls):
        """Yield a `PlayerEntity` (subclass) instance for each alive player."""
        for player in PlayerIter('alive'):
            yield cls(player.index)

    @classmethod
    def by_team(cls, team_index):
        """Yield a `PlayerEntity` (subclass) instance for each alive player of team `team_index`."""
        for player in PlayerIter(('alive', 't' if team_index == 2 else 'ct')):
            yield cls(player.index)

    @classmethod
    def respawn(cls, index):
        """Respawn a player if they are still connected."""
        with contextlib.suppress(ValueError):
            cls(index).spawn(True)

    @classmethod
    def disable_damage_protection(cls, index):
        """Disable damage protection if the player is still connected."""
        with contextlib.suppress(ValueError):

            # Get a PlayerEntity instance for the player index
            player = cls(index)

            # Disable god mode
            player.godmode = False

            # Reset the color
            player.color = WHITE

    @staticmethod
    def reset_team_changes(userid):
        """Reset the player's team change count."""
        if userid in player_team_changes:
            del player_team_changes[userid]

    def tell(self, prefix, message):
        """Send the player a prefixed chat message."""
        SayText2(
            f'{MESSAGE_COLOR_ORANGE}[{MESSAGE_COLOR_WHITE}{prefix}{MESSAGE_COLOR_ORANGE}] {message}'
        ).send(self.index)

    def give_weapon(self, name):
        """Fix for give_named_item() deciding which weapon actually spawns based on the player's loadout."""
        # Fix taken from GunGame-SP
        #  see https://github.com/GunGame-Dev-Team/GunGame-SP/commit/bc3e7ab3630a5e3680ff35d726e810370b86a5ea
        #  and https://forums.sourcepython.com/viewtopic.php?f=31&t=1597

        # Give the player the weapon entity
        weapon = make_object(Weapon, self.give_named_item(name))

        # Return it if it doesn't share its classname with another weapon
        if weapon.classname == weapon.weapon_name:
            return weapon

        # Remove it, if it does
        weapon.remove()

        # Switch the player's team and give the weapon entity again
        self.team_index = 5 - self.team
        weapon = make_object(Weapon, self.give_named_item(name))

        # Reset the player's team
        self.team_index = 5 - self.team

        # Return the correct weapon entity
        return weapon

    def equip_weapon(self, weapon_name):
        """Equip the player with the weapon from `weapon_name`."""
        # Give the player the weapon entity
        weapon = self.give_weapon(weapon_name)

        # Force the player to use it
        self.client_command(f'use {weapon.classname}', True)

    def equip_inventory(self):
        """Equip the player's currently selected inventory."""
        if self.inventory:
            for tag in self.inventory.keys():
                self.equip_inventory_item(tag)

        # Give random weapons, if the inventory is empty
        else:
            self.equip_random_weapons()

    def equip_inventory_item(self, tag):
        """Equip the inventory item for `tag`."""
        # Remove any weapon which is not listed in the player's inventory
        tags_to_remove = [tag for tag in weapon_manager.tags if tag not in self.inventory]

        if tags_to_remove:
            self.strip(is_filters=tags_to_remove)

        # Get the equipped weapon at `tag`
        weapon = self.get_weapon(is_filters=tag)

        # Get the inventory item
        inventory_item = self.inventory[tag]

        # Equip the weapon if the player isn't equipped with it
        if weapon is None:
            self.equip_weapon(inventory_item.data.name)

        # Replace it with the correct weapon, if the player isn't supposed to be equipped with it
        else:
            weapon_data = weapon_manager.by_name(weapon.weapon_name)

            if weapon_data.name != inventory_item.data.name:
                weapon.remove()

                # Equip the correct weapon
                self.equip_weapon(inventory_item.data.name)

    def equip_random_weapon(self, tag):
        """Equip the player with a random weapon."""
        self.equip_weapon(self.get_random_weapon(tag))

    def equip_random_weapons(self):
        """Equip random weapons by weapon tag."""
        # Enable random mode
        self.random_mode = True

        # Strip the player off their weapons
        self.strip()

        # Equip random weapons
        for tag in self.random_weapons.keys():
            self.equip_random_weapon(tag)

    def weapon_dropped(self):
        """Handle removing the player's active weapon from their inventory if it has been dropped."""
        if self.active_weapon is not None:
            weapon_data = weapon_manager.by_name(self.active_weapon.weapon_name)

            if weapon_data is not None:

                # Equip a random weapon if the player has random mode activated
                if self.random_mode:

                    # Remove the player's active weapon
                    self.active_weapon.remove()

                    # Equip the player with a random weapon
                    self.equip_random_weapon(weapon_data.tag)

                # Else, equip random weapons of the player's inventory is empty
                else:
                    self.inventory.remove_inventory_item(self, weapon_data.tag)

                    if not self.inventory:
                        self.equip_random_weapons()

    def choose_weapon(self, weapon_basename):
        """Handle choosing a weapon from the buy menu or the weapon menu."""
        # Disable random mode
        self.random_mode = False

        # Only allow choosing valid weapons
        if weapon_basename in weapon_manager:

            # Get the weapon's data
            weapon_data = weapon_manager[weapon_basename]

            # Add the weapon to the player's inventory
            self.inventory.add_inventory_item(weapon_basename, weapon_data)

            # Equip the player with the weapon if the player is alive and on a team
            if not self.dead and self.team_index > 1:
                self.equip_inventory_item(weapon_data.tag)

    def strip(self, is_filters=None, not_filters=('melee', 'grenade')):
        """Remove the player's weapons in `is_filters` & keep those in `not_filters`."""
        for weapon in self.weapons(is_filters=is_filters, not_filters=not_filters):
            weapon.remove()

    def enable_damage_protection(self, time_delay=None):
        """Enable damage protection and disable it after `time_delay` if `time_delay` is not None."""
        # Cancel the damage protection delay for the player
        delay_manager.cancel(f'protect_{self.userid}')

        # Enable god mode
        self.godmode = True

        # Set protection color
        self.color = Color(100, 70, 0)

        # Disable protection after `time_delay`
        if time_delay is not None:
            delay_manager(
                f'protect_{self.userid}', time_delay, PlayerEntity.disable_damage_protection, (self.index, ),
                call_on_cancel=True
            )

    def refill_ammo(self, clip_fix=0):
        """Restore the player's active weapon's ammo."""
        # Get the weapon's data
        weapon_data = weapon_manager.by_name(self.active_weapon.weapon_name)

        # Add up the weapon's ammo
        self.active_weapon.ammo = weapon_data.maxammo - self.active_weapon.clip + weapon_data.clip + clip_fix

    def refill_clip(self, weapon_data):
        """Restore the player's active weapon's clip."""
        delay_manager(
            f'refill_clip_{self.active_weapon.index}', 0.1,
            self.active_weapon.set_clip, (weapon_data.clip,)
        )

    def get_random_weapon(self, tag):
        """Return a random weapon for the given weapon tag."""
        return self.random_weapons[tag].pop()

    def get_spawn_location(self):
        """Return a unique spawn location for the player."""
        # Get a list of current player origins
        player_origins = [player.origin for player in PlayerEntity.alive() if player.userid != self.userid]

        # Loop through all the player's spawn points
        for spawn_location in self.spawn_locations.copy():

            # Calculate the distances between the spawn point and all player origins
            distances = [origin.get_distance(spawn_location) for origin in player_origins]

            # Continue if there is enough space around the spawn point
            if distances and min(distances) >= SAFE_SPAWN_DISTANCE:

                # Remove the spawn point from the player's spawn points list
                self.spawn_locations.remove(spawn_location)

                # Return the spawn point found
                return spawn_location

        # Return the player's current location as a spawn point if no spawn point has been found
        return SpawnPoint.from_player_location(self)

    @property
    def random_weapons(self):
        """Return personal random weapons for the player."""
        # Get the player's personal random weapon map
        random_weapons = player_random_weapons[self.userid]

        # Iterate through it
        for tag, weapon_list in random_weapons.items():

            # Fill in all weapons of `tag` in shuffled form if the tag's weapon list is empty
            if not weapon_list:
                weapon_list.extend([weapon_data.name for weapon_data in weapon_manager.by_tag(tag)])
                random.shuffle(weapon_list)

        # Return it
        return player_random_weapons[self.userid]

    @property
    def spawn_locations(self):
        """Return personal spawn locations for the player."""
        # Get the player's personal spawn locations list
        spawn_locations = player_spawn_locations[self.userid]

        # Fill in spawn points in shuffled form if it is empty
        if not spawn_locations:
            spawn_locations.extend(spawnpoint_manager)
            random.shuffle(spawn_locations)

        # Return it
        return spawn_locations

    def team_changed(self, team_index):
        self.team = team_index

        # Take a note of the team change
        self.team_changes += 1

        # Reset the player's team change count after the team change reset delay if the maximum team change count
        # has been reached
        if self.team_changes == cvar_team_changes_per_round.get_int() + 1:
            penalty_seconds = abs(cvar_team_changes_reset_delay.get_float()) * 60.0

            delay_manager(
                f'reset_team_changes_{self.userid}', penalty_seconds,
                PlayerEntity.reset_team_changes, (self.userid,)
            )

            penalty_start = datetime.datetime.now()
            penalty_end = penalty_start + datetime.timedelta(seconds=penalty_seconds)

            penalty_delta = penalty_end - penalty_start
            minutes, seconds = str(penalty_delta).split(':')[1:]

            penalty_map = {
                'minutes': int(minutes),
                'seconds': int(seconds)
            }

            penalty_strings = [f'{penalty_map[key]} {key}' for key in sorted(penalty_map) if penalty_map[key] > 0]

            # Fix postfix 's' if the respective time value is not higher than 1
            penalty_strings = [s if s[0] > '1' else s[:-1] for s in penalty_strings]

            # Join the strings together
            penalty_string = ' and '.join(penalty_strings)

            # Tell the player
            self.tell(
                info.verbose_name, f'{MESSAGE_COLOR_WHITE}You will have to wait {MESSAGE_COLOR_ORANGE}{penalty_string}'
                                   f'{MESSAGE_COLOR_WHITE} to join any other team from now on.'
            )

        # Respawn the player after the respawn delay
        delay_manager(
            f'respawn_{self.userid}', abs(cvar_respawn_delay.get_float()), PlayerEntity.respawn, (self.index,)
        )

    def set_team_changes(self, value):
        """Store `value` as the team change count for the player."""
        player_team_changes[self.uniqueid] = value

    def get_team_changes(self):
        """Return the team change count for the player."""
        return player_team_changes[self.uniqueid]

    # Set the `team_changes` property for PlayerEntity
    team_changes = property(get_team_changes, set_team_changes)

    def set_inventory_selection(self, inventory_index):
        """Set the player's inventory selection to `inventory_index`."""
        player_inventories.selections[self.uniqueid] = inventory_index

    def get_inventory_selection(self):
        """Return the player's current inventory selection."""
        return player_inventories.selections[self.uniqueid]

    # Set the `inventory_selection` property for PlayerEntity
    inventory_selection = property(get_inventory_selection, set_inventory_selection)

    def set_random_mode(self, value):
        """Set random mode for the player."""
        player_inventories.selections_random[self.userid] = value

    def get_random_mode(self):
        """Return whether the player is currently in random mode."""
        return player_inventories.selections_random[self.userid]

    # Set the `random_mode` property for PlayerEntity
    random_mode = property(get_random_mode, set_random_mode)

    @property
    def inventories(self):
        """Return the player's inventories."""
        return player_inventories[self.uniqueid]

    @property
    def inventory(self):
        """Return the player's current inventory."""
        return self.inventories[self.inventory_selection]

    @property
    def carries_inventory(self):
        """Return whether the player is currently carrying the weapons of their selected inventory."""
        for tag, item in self.inventory.items():

            # Get the equipped weapon for the tag
            weapon_equipped = self.get_weapon(is_filters=tag)

            # Return False if no weapon is equipped
            if weapon_equipped is None:
                return False

            # Return False if the equipped weapon is not the one selected for the tag
            if item.data.name not in (weapon_equipped.weapon_name, weapon_equipped.classname):
                return False

            # Return False if the weapon is in a different silencer state than it's supposed to be
            if item.data.has_silencer and item.silencer_option != weapon_equipped.get_property_bool('m_bSilencerOn'):
                return False

        # Return True if the player carries all the weapons in their selected inventory
        return True
