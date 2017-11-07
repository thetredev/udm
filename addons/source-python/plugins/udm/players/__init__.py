# ../udm/players/__init__.py

"""Provides an interface between a player entity and their inventories."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
import contextlib
#   Random
import random

# Source.Python Imports
#   Colors
from colors import Color
from colors import WHITE
#   Engines
from engines.server import global_vars
#   Listeners
from listeners import OnEntityDeleted
from listeners.tick import Delay
#   Players
from players.entity import Player

# Script Imports
#   Config
from udm.config import cvar_equip_hegrenade
from udm.config import cvar_spawn_protection_delay
#   Delays
from udm.delays import delay_manager
#   Players
from udm.players.inventories import PlayerInventory
from udm.players.inventories import player_inventories
#   Spawn Points
from udm.spawnpoints import spawnpoints
#   Weapons
from udm.weapons import refill_ammo
from udm.weapons import weapon_manager


# =============================================================================
# >> PLAYER ENTITY
# =============================================================================
class PlayerEntity(Player):
    """Class used to provide the following functionality:

        * inventories and inventory selections
        * battle preparation including damage protection
        * ammo refill
    """

    def equip(self, inventory_index=None, force_random=False):
        """Equip the inventory at `inventory_index`."""
        # Equip random weapons if forced to
        if force_random:
            for tag in weapon_manager.tags:
                self.give_named_item(random.choice(list(weapon_manager.by_tag(tag))).name)

        # Otherwise equip the inventory at `inventory_index`
        else:

            # Add a new inventory at `inventory_index` if none is present
            if inventory_index not in self.inventories:
                self.inventories[inventory_index] = PlayerInventory(self.uniqueid)

            # Get the inventory at `inventory_index`
            inventory = self.inventories[inventory_index]

            # Equip all weapons in `inventory`
            if inventory:
                for item in inventory.values():
                    item.equip(self)

            # Give random weapons, if `inventory` is empty
            else:
                for tag in weapon_manager.tags:
                    self.give_named_item(random.choice(list(weapon_manager.by_tag(tag))).name)

    def strip(self, keep=None):
        """Remove all the player's weapons except for those in `keep`."""
        for weapon in self.weapons(not_filters=keep):
            weapon.remove()

    def prepare(self):
        """Prepare the player for battle."""
        # Give armor
        self.give_named_item('item_assaultsuit')

        # Give a High Explosive grenade if configured that way
        if cvar_equip_hegrenade.get_int() > 0:
            self.give_named_item('weapon_hegrenade')

        # Enable damage protect
        self.protect(cvar_spawn_protection_delay.get_int())

        # Choose a random spawn point
        spawnpoint = spawnpoints.get_random()

        # Spawn the player on the location found
        if spawnpoint is not None:
            self.origin = spawnpoint
            self.view_angle = spawnpoint.angle

        # Strip the player off their weapons, but keep melee weapons and grenades
        self.strip(('melee', 'grenade'))

        # Equip the current inventory
        self.equip(self.inventory_selection)

    def protect(self, time_delay=None):
        """Enable damage protection and disable it after `time_delay` if `time_delay` is not None."""
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
            delay_manager[f'protect_{self.userid}'].append(Delay(time_delay, self.unprotect))

    def unprotect(self):
        """Disable damage protection."""
        # Disable god mode
        self.godmode = False

        # Reset the color
        self.color = WHITE

    def refill_ammo(self):
        """Refill the player's active weapon's ammo after the reload animation has finished."""
        with contextlib.suppress(ValueError):

            # Only refill for non-melee and non-grenade weapons
            if weapon_manager[self.active_weapon.classname].tag not in ('melee', 'grenade'):

                # Get the 'next attack' property for the current weapon
                next_attack = self.active_weapon.get_property_float('m_flNextPrimaryAttack')

                # Add a tolerance value of 1 second to somewhat counter the effects of lags, etc
                next_attack += 1

                # Calculate the amount of time it would take for the reload animation to finish
                duration = next_attack - global_vars.current_time

                # Call weapons.refill_ammo() after `duration`
                delay_manager[f'refill_{self.active_weapon.index}'].append(
                    Delay(duration, refill_ammo, (self.active_weapon, ))
                )

    def spawn(self):
        """Safely respawn the player."""
        if self.is_connected():
            super().spawn(True)

    @property
    def inventories(self):
        """Return the player's inventories."""
        return player_inventories[self.uniqueid]

    def set_inventory_selection(self, inventory_index):
        """Set the player's inventory selection to `inventory_index`."""
        player_inventories.selections[self.userid] = inventory_index

    def get_inventory_selection(self):
        """Return the player's current inventory selection - 0 if not present."""
        if self.userid in player_inventories.selections:
            return player_inventories.selections[self.userid]

        return 0

    # Set the `inventory_selection` property for PlayerEntity
    inventory_selection = property(get_inventory_selection, set_inventory_selection)


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def on_entity_deleted(entity):
    """Cancel the refill delay for the deleted entity."""
    with contextlib.suppress(ValueError):
        delay_manager.cancel_delays(f'refill_{entity.index}')
