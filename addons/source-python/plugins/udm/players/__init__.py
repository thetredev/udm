# ../udm/players/__init__.py

"""Provides a convenience class for player entities."""

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
from udm.weapons import weapons


# =============================================================================
# >> PLAYER ENTITY
# =============================================================================
class PlayerEntity(Player):
    """Convenience class used for the following things:

        - Wrap players.entity.Player.give_named_item() to return an actual weapons.entity.Weapon instance
        - Provide a safe and easy way to access the player's inventory"""

    def equip(self, inventory_index):
        """Equip the player with their inventory."""
        # Equip the player their inventory
        if inventory_index not in self.inventories:
            self.inventories[inventory_index] = PlayerInventory(self.uniqueid)

        inventory = self.inventories[inventory_index]

        # Equip only if the player has chosen any weapons
        if inventory:
            for item in inventory.values():
                item.equip(self)

        # Or give random weapons, if the inventory is empty
        else:
            for tag in weapons.tags:
                self.give_named_item(random.choice(list(weapons.by_tag(tag))).name)

    def prepare(self):
        """Prepare the player for battle."""
        # Equip the player with armor
        self.give_named_item('item_assaultsuit')

        # Equip the player with a High Explosive grenade if configured that way
        if cvar_equip_hegrenade.get_int() > 0:
            self.give_named_item('weapon_hegrenade')

        # Protect the player from any damage
        self.protect(cvar_spawn_protection_delay.get_int())

        # Choose a random spawn point
        spawnpoint = spawnpoints.get_random()

        # Spawn the player on the location found
        if spawnpoint is not None:
            self.origin = spawnpoint
            self.view_angle = spawnpoint.angle

        # Strip the player off their weapons, but keep the knife
        self.strip(('melee', 'grenade'))

        # Equip the player
        self.equip(self.inventory_selection)

    def protect(self, time_delay=None):
        """Protect the player for the configured spawn protection duration."""
        # Enable god mode
        self.godmode = True

        # Set the player's color
        self.color = Color(
            210 if self.team == 2 else 0,
            0,
            210 if self.team == 3 else 0
        )

        # Call _unprotect() after the configured spawn protection duration
        if time_delay is not None:
            delay_manager[f'protect_{self.userid}'].append(Delay(time_delay, self.unprotect))

    def refill_ammo(self):
        """Refill the player's ammo on reload after the reload animation has finished."""
        with contextlib.suppress(ValueError):
            if weapons[self.active_weapon.classname].tag != 'meele':

                # Get the 'next attack' property for the current weapon, plus a tolerance value of one second
                next_attack = self.active_weapon.get_property_float('m_flNextPrimaryAttack') + 1

                # Calculate the amount of time it would take for the reload animation to finish (tolerance included)
                duration = next_attack - global_vars.current_time

                # Refill the weapon's ammo after the reload animation has finished
                delay_manager[f'refill_{self.active_weapon.index}'].append(
                    Delay(duration, refill_ammo, (self.active_weapon, ))
                )

    def spawn(self):
        """Safely respawn the player."""
        if self.is_connected():
            super().spawn(True)

    def strip(self, keep=None):
        """Remove all the player's weapons except for 'knife'."""
        for weapon in self.weapons(not_filters=keep):
            weapon.remove()

    def unprotect(self):
        """Enable default gameplay, if they're still online."""
        if self.is_connected():

            # Disable god mode
            self.godmode = False

            # Reset the player's color
            self.color = WHITE

    @property
    def inventories(self):
        """Provide access to the player's inventories."""
        return player_inventories[self.uniqueid]

    def set_inventory_selection(self, inventory_index):
        """Set the player's inventory selection to `inventory_index`."""
        player_inventories.selections[self.userid] = inventory_index

    def get_inventory_selection(self):
        """Return the player's inventory selection - 0 if not present."""
        if self.userid in player_inventories.selections:
            return player_inventories.selections[self.userid]

        return 0

    inventory_selection = property(get_inventory_selection, set_inventory_selection)


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def on_entity_deleted(entity):
    """Cancel the refill delay for the deleted entity."""
    with contextlib.suppress(ValueError):
        delay_manager.cancel_delays(f'refill_{entity.index}')
