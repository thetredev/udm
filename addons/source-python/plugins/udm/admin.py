# ../udm/admin.py

"""Provides the Admin menu."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus.radio import PagedRadioOption

# Script Imports
#   Menus
from udm.menus import CloseButtonPagedMenu
from udm.menus.decorators import CloseCallback
from udm.menus.decorators import SelectCallback
#   Weapons
from udm.weapons import melee_weapon


# =============================================================================
# >> ADMIN MENU
# =============================================================================
# TODO: Use submenu API from SP?
class _AdminMenu(CloseButtonPagedMenu):
    """Class used to provide a way to send this menu when a submenu is closed."""

    # Store players who are currently using the Admin menu
    users = dict()

    def register_submenu(self, submenu):
        """Always send this menu when a submenu is closed."""
        # Store `self.send` as the submenu's `close_callback`
        submenu.close_callback = self.send

        # Add the submenu
        self.append(PagedRadioOption(submenu.title, submenu))

    def _unload_instance(self):
        """Clear the users dict on unload."""
        # Clear the users dict
        self.users.clear()

        # Continue base routine
        super()._unload_instance()


# Store a global instance of `_AdminMenu`
admin_menu = _AdminMenu(title='Admin Menu')


# =============================================================================
# >> ADMIN MENU CALLBACKS
# =============================================================================
@CloseCallback(admin_menu)
def on_close_admin_menu(player):
    """Enable default gameplay for the admin player who just closed the Admin menu."""
    # Remove the player from the Admin menu users storage
    admin_menu.users[player.userid] = False

    # Equip the player with their inventory & a High Explosive grenade
    player.equip_inventory()
    player.give_named_item('weapon_hegrenade')

    # Disable damage protection
    player.disable_damage_protection()

    # Give a random melee weapon
    player.give_named_item(melee_weapon)


@SelectCallback(admin_menu)
def on_select_admin_submenu(player, option):
    """Send the submenu chosen to the player."""
    option.value.send(player.index)
