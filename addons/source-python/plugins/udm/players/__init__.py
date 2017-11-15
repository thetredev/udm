# ../udm/players/__init__.py

"""Provides an interface between a player entity and their inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Random
import random

# Source.Python Imports
#   Colors
from colors import Color
from colors import WHITE
#   Engines
from engines.server import global_vars
#   Filters
from filters.players import PlayerIter
#   Messages
from messages import SayText2
#   Players
from players.entity import Player

# Script Imports
#   Colors
from udm.colors import MESSAGE_COLOR_ORANGE
from udm.colors import MESSAGE_COLOR_WHITE
#   Delays
from udm.delays import delay_manager
#   Players
from udm.players.inventories import player_inventories
#   Weapons
from udm.weapons import refill_ammo
from udm.weapons import weapon_manager


# =============================================================================
# >> ALIVE PLAYERS GENERATOR
# =============================================================================
# Store an instance of PlayerIter for alive players
_playeriter_alive = PlayerIter('alive')


# =============================================================================
# >> PLAYER ENTITY
# =============================================================================
class PlayerEntity(Player):
    """Class used to provide the following functionality:

        * inventories and inventory selections
        * battle preparation including damage protection
        * ammo refill
    """

    @classmethod
    def alive(cls):
        for player in _playeriter_alive:
            yield cls(player.index)

    def tell(self, prefix, message):
        """Tell the player a prefixed chat message."""
        SayText2(
            f'{MESSAGE_COLOR_ORANGE}[{MESSAGE_COLOR_WHITE}{prefix}{MESSAGE_COLOR_ORANGE}] {message}'
        ).send(self.index)

    def equip_inventory(self):
        """Equip the player's currently selected inventory."""
        if self.inventory:
            self.inventory.equip(self)

        # Give random weapons, if the inventory is empty
        else:
            self.equip_random_weapons()

    def equip_random_weapons(self):
        """Equip random weapons by weapon tag."""
        # Enable random mode
        self.random_mode = True

        # Strip the player off their weapons
        self.strip()

        # Equip random weapons
        for tag in weapon_manager.tags:
            self.give_named_item(random.choice(list(weapon_manager.by_tag(tag))).name)

    def strip(self, is_filters=None, not_filters=('melee', 'grenade')):
        """Remove the player's weapons in `is_filters` & keep those in `not_filters`."""
        for weapon in self.weapons(is_filters=is_filters, not_filters=not_filters):
            weapon.remove()

    def enable_damage_protection(self, time_delay=None):
        """Enable damage protection and disable it after `time_delay` if `time_delay` is not None."""
        # Disable all damage protection delays for the player
        delay_manager.cancel(f'protect_{self.userid}')

        # Enable god mode
        self.godmode = True

        # Set protection color
        self.color = Color(
            210 if self.team == 2 else 0,
            0,
            210 if self.team == 3 else 0
        )

        # Disable protection after `time_delay`
        if time_delay is not None:
            delay_manager(f'protect_{self.userid}', time_delay, self.disable_damage_protection)

    def disable_damage_protection(self):
        """Disable damage protection."""
        # Disable god mode
        self.godmode = False

        # Reset the color
        self.color = WHITE

    def refill_ammo(self):
        """Refill the player's active weapon's ammo after the reload animation has finished."""
        # Refill only valid weapons
        if weapon_manager.by_name(self.active_weapon.weapon_name).tag in ('melee', 'grenade'):
            return

        # Get the 'next attack' property for the current weapon
        next_attack = self.active_weapon.get_property_float('m_flNextPrimaryAttack')

        # Add a tolerance value of 1 second to somewhat counter the effects of lags, etc
        next_attack += 1

        # Calculate the amount of time it would take for the reload animation to finish
        duration = next_attack - global_vars.current_time

        # Call weapons.refill_ammo() after `duration`
        delay_manager(f'refill_{self.active_weapon.index}', duration, refill_ammo, (self.active_weapon, ))

    def spawn(self):
        """Always force spawn the player."""
        super().spawn(True)

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
        """Return whether the player is currently carrying the weapons in their selected inventory."""
        for tag, item in self.inventory.items():

            # Get the equipped weapon for the tag
            weapon_equipped = self.get_weapon(is_filters=tag)

            # Return False if no weapon is equipped
            if weapon_equipped is None:
                return False

            # Return False if the equipped weapon is not the one selected for the tag
            if item.data.name not in (weapon_equipped.weapon_name, weapon_equipped.classname):
                return False

        # Return True if the player carries all the weapons in their selected inventory
        return True

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
